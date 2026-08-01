import time
import json
import random
import os
import math
from kafka import KafkaProducer

# Configuration
KAFKA_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
TOPIC_NAME = 'gps-telemetry'

# Bounding box for Colombo, Sri Lanka (lat: 6.90 to 6.95, lon: 79.84 to 79.88)
LAT_MIN, LAT_MAX = 6.9000, 6.9500
LON_MIN, LON_MAX = 79.8400, 79.8800

# Vehicle profiles
VEHICLES = [
    {"id": "V-101", "name": "Rapid Rider (Tuk-Tuk)", "type": "tuktuk", "speed_factor": 0.00015},
    {"id": "V-102", "name": "City Express (Bike)", "type": "bike", "speed_factor": 0.00020},
    {"id": "V-103", "name": "Green Delivery (Bicycle)", "type": "bicycle", "speed_factor": 0.00008},
    {"id": "V-104", "name": "Metro Van (Van)", "type": "van", "speed_factor": 0.00012},
    {"id": "V-105", "name": "Flash Courier (Bike)", "type": "bike", "speed_factor": 0.00022},
]

# Initialize state
for v in VEHICLES:
    v["lat"] = random.uniform(LAT_MIN, LAT_MAX)
    v["lon"] = random.uniform(LON_MIN, LON_MAX)
    v["target_lat"] = random.uniform(LAT_MIN, LAT_MAX)
    v["target_lon"] = random.uniform(LON_MIN, LON_MAX)
    v["status"] = "Moving"
    v["idle_timer"] = 0

def move_vehicle(v):
    if v["status"] == "Idle":
        v["idle_timer"] -= 1
        if v["idle_timer"] <= 0:
            v["status"] = "Moving"
            v["target_lat"] = random.uniform(LAT_MIN, LAT_MAX)
            v["target_lon"] = random.uniform(LON_MIN, LON_MAX)
        return

    # Calculate distance to target
    d_lat = v["target_lat"] - v["lat"]
    d_lon = v["target_lon"] - v["lon"]
    distance = math.sqrt(d_lat**2 + d_lon**2)

    # If arrived or very close, transition to idle or select new target
    if distance < 0.0005:
        # 30% chance to idle for a bit (e.g. package pickup/dropoff)
        if random.random() < 0.3:
            v["status"] = "Idle"
            v["idle_timer"] = random.randint(5, 15) # idle for 5-15 seconds
            print(f"Vehicle {v['id']} is now Idle (delivery/pickup).")
        else:
            v["target_lat"] = random.uniform(LAT_MIN, LAT_MAX)
            v["target_lon"] = random.uniform(LON_MIN, LON_MAX)
        return

    # Move towards target
    step = v["speed_factor"] * random.uniform(0.8, 1.2)
    v["lat"] += (d_lat / distance) * step
    v["lon"] += (d_lon / distance) * step

    # Occasional GPS drift anomaly (1% chance)
    if random.random() < 0.01:
        # Simulate a slight GPS jump
        v["lat"] += random.uniform(-0.001, 0.001)
        v["lon"] += random.uniform(-0.001, 0.001)
        print(f"Vehicle {v['id']} experienced GPS drift anomaly.")

def main():
    print(f"Connecting to Kafka at {KAFKA_SERVERS}...")
    producer = None
    retries = 0
    while not producer:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_SERVERS.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("Connected to Kafka successfully!")
        except Exception as e:
            retries += 1
            print(f"Kafka connection attempt {retries} failed. Retrying in 5 seconds... Error: {e}")
            time.sleep(5)

    print("Starting simulation stream...")
    while True:
        try:
            for v in VEHICLES:
                move_vehicle(v)
                
                payload = {
                    "vehicle_id": v["id"],
                    "vehicle_name": v["name"],
                    "vehicle_type": v["type"],
                    "latitude": v["lat"],
                    "longitude": v["lon"],
                    "status": v["status"],
                    "timestamp": time.time()
                }
                
                # Send to Kafka
                producer.send(TOPIC_NAME, payload)
                
            producer.flush()
            time.sleep(1.5)
        except Exception as e:
            print(f"Error during simulation run: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
