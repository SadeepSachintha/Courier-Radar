import os
import sys
import json
import math
import time
import redis
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

# Configs
KAFKA_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
LARAVEL_API = os.getenv('LARAVEL_API_URL', 'http://backend:8000/api/telemetry')
TOPIC_NAME = 'gps-telemetry'

# Haversine distance in km
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# Bearing calculation in degrees (0-360)
def calculate_bearing(lat1, lon1, lat2, lon2):
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    d_lon = math.radians(lon2 - lon1)
    y = math.sin(d_lon) * math.cos(lat2_r)
    x = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(d_lon)
    initial_bearing = math.atan2(y, x)
    return (math.degrees(initial_bearing) + 360) % 360

# Process batch data
def process_batch(df, batch_id):
    rows = df.collect()
    if not rows:
        return

    # Redis connection (hot cache)
    r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

    for row in rows:
        vehicle_id = row.vehicle_id
        name = row.vehicle_name
        v_type = row.vehicle_type
        lat = row.latitude
        lng = row.longitude
        status = row.status
        timestamp = row.timestamp

        # Geofence boundary: Galle Face Green (Colombo, Sri Lanka)
        # lat: [6.924, 6.930], lon: [79.840, 79.846]
        is_inside = (6.9240 <= lat <= 6.9300) and (79.8400 <= lng <= 79.8460)
        geofence_zone = "Galle Face Green (Zone A)" if is_inside else None

        # Fetch previous coordinates from Redis to compute speed and bearing
        prev_key = f"vehicle:{vehicle_id}:prev"
        prev_data = r.get(prev_key)
        
        speed = 0.0
        bearing = 0.0

        if prev_data:
            try:
                prev = json.loads(prev_data)
                prev_lat = prev['lat']
                prev_lng = prev['lng']
                prev_time = prev['time']

                time_diff = timestamp - prev_time
                if time_diff > 0.1:
                    dist = haversine(prev_lat, prev_lng, lat, lng)
                    # Speed in km/h
                    speed = (dist / time_diff) * 3600.0
                    # Clip anomalies/outliers
                    max_speed = 70.0 if v_type == 'bicycle' else 110.0
                    speed = min(speed, max_speed)
                    if speed < 0.5:
                        speed = 0.0

                    bearing = calculate_bearing(prev_lat, prev_lng, lat, lng)
            except Exception as e:
                print(f"Error computing movement stats: {e}", file=sys.stderr)

        # Update previous position cache
        r.set(prev_key, json.dumps({
            "lat": lat,
            "lng": lng,
            "time": timestamp
        }))

        # Send processed telemetry update to Laravel Backend Webhook
        payload = {
            "vehicle_id": vehicle_id,
            "vehicle_name": name,
            "vehicle_type": v_type,
            "latitude": lat,
            "longitude": lng,
            "speed": round(speed, 2),
            "bearing": round(bearing, 2),
            "status": status,
            "geofence_zone": geofence_zone,
            "timestamp": timestamp
        }

        try:
            res = requests.post(LARAVEL_API, json=payload, timeout=2)
            print(f"Processed: {vehicle_id} | Speed: {payload['speed']} km/h | Bearing: {payload['bearing']}° | Status: {payload['status']} | Laravel: {res.status_code}")
        except Exception as e:
            print(f"Failed to post telemetry to Laravel: {e}", file=sys.stderr)

def main():
    print("Starting Spark Telemetry Processor...")
    
    # Initialize Spark Session with Kafka package configuration
    spark = SparkSession.builder \
        .appName("TelemetryStreamProcessor") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .getOrCreate()

    # Set log level
    spark.sparkContext.setLogLevel("WARN")

    # Define GPS telemetry schema
    schema = StructType([
        StructField("vehicle_id", StringType(), True),
        StructField("vehicle_name", StringType(), True),
        StructField("vehicle_type", StringType(), True),
        StructField("latitude", DoubleType(), True),
        StructField("longitude", DoubleType(), True),
        StructField("status", StringType(), True),
        StructField("timestamp", DoubleType(), True)
    ])

    print(f"Subscribing to Kafka topic '{TOPIC_NAME}' at {KAFKA_SERVERS}...")
    
    # Read stream from Kafka
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_SERVERS) \
        .option("subscribe", TOPIC_NAME) \
        .option("startingOffsets", "latest") \
        .load()

    # Parse JSON payload
    parsed_df = kafka_df \
        .selectExpr("CAST(value AS STRING) as json_value") \
        .select(from_json(col("json_value"), schema).alias("data")) \
        .select("data.*")

    # Stream output executing the processing loop per micro-batch
    query = parsed_df.writeStream \
        .foreachBatch(process_batch) \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
