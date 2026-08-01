# Courier Radar - User & Developer Manual

Welcome to the **Courier Radar Live Fleet & Delivery Tracker**! This guide details how to install, run, customize, and troubleshoot the Courier Radar tracking platform.

---

## 🚀 Quick Start Guide

To run Courier Radar on your local machine, follow these steps:

### 1. Launch the Container Network
Open a terminal in the root directory and start the Docker services in the background:
```bash
docker compose up -d
```
*Docker Compose will download base images for Kafka, Redis, PostgreSQL + PostGIS, and compile our custom PHP, PySpark, Python Simulator, and Node.js containers.*

### 2. Prepare the Database (PostGIS)
Once the containers are running, execute database migrations to set up relational tables and geospatial indices:
```bash
docker compose exec backend php artisan migrate
```

### 3. Open the Dashboard
Open your browser and navigate to:
```http
http://localhost:5173
```
*Note: Make sure that local ports `5173`, `8005`, `8090`, `5432`, `6379`, and `9092` are not allocated by other host processes before launching.*

---

## 🖥️ Operating the Dashboard

The dashboard is divided into three functional areas:

### 1. Interactive Control Map (Center)
- **Map Theme**: A custom Dark Matter theme is used to highlight vehicle markers.
- **Markers**: Vehicles are displayed as colored triangles. The tip of the triangle points in the vehicle's direction of movement (calculated dynamically by Spark).
- **Tooltips**: Click a vehicle marker to view its name, ID, type, current speed, and active status.
- **Geofence Zone**: The red dashed rectangle outlines the **Galle Face Green Delivery Zone (A)**.

### 2. Fleet Status Directory (Left Sidebar)
- **Statistics**: Monitors active counts of:
  - **Total Assets**: Registered fleet size.
  - **Moving**: Vehicles moving at speed.
  - **Idle**: Vehicles that have stopped (simulating a package pickup/delivery drop).
  - **Geofenced**: Number of vehicles currently inside the active Galle Face boundary.
- **Asset List**: Displays all vehicles. Clicking on any vehicle row instantly centers the map on its current location and opens its info popup.

### 3. System Alerts Log (Right Sidebar)
- Displays real-time operational feeds:
  - **Geofence Breach**: Alerts (`🚨 Entry` / `ℹ️ Exit`) are triggered when vehicles cross the Galle Face boundary.
  - **Connection Alerts**: Displays `⚠️ Connection lost` warnings if a vehicle has not sent telemetry pings for over 8 seconds (marks the asset as `Offline`).

---

## ⚙️ Developer Customizations

### 1. Adjusting Geofence Coordinates
The geofence check is run in the Spark streaming container. To adjust the boundaries:
1. Open [spark/stream_processor.py](file:///d:/xampp/htdocs/Courier%20Radar/spark/stream_processor.py#L38-L41) and adjust the bounding box check:
   ```python
   is_inside = (MIN_LAT <= lat <= MAX_LAT) and (MIN_LON <= lng <= MAX_LON)
   ```
2. Open the frontend component [frontend/src/App.vue](file:///d:/xampp/htdocs/Courier%20Radar/frontend/src/App.vue#L225) and update the map rectangle coords:
   ```javascript
   const geofenceRect = L.rectangle([[MIN_LAT, MIN_LON], [MAX_LAT, MAX_LON]], { ... })
   ```

### 2. Modifying Simulator Fleet Settings
To scale the simulation up/down or introduce new vehicle models:
- Edit [simulator/simulator.py](file:///d:/xampp/htdocs/Courier%20Radar/simulator/simulator.py#L14-L21). You can add items to the `VEHICLES` list or change speed factors:
  ```python
  VEHICLES = [
      {"id": "V-101", "name": "Rapid Rider (Tuk-Tuk)", "type": "tuktuk", "speed_factor": 0.00015},
      ...
  ]
  ```

---

## 🛠️ Troubleshooting

### 1. WSL2 / Alpine DNS Query Hangs
If HTTP requests from Spark to Laravel time out, it is likely caused by the Windows/WSL2 DNS IPv6 lookup delay on Alpine images.
- **Fix**: We have switched the Laravel container base to a **Debian CLI (`php:8.4-cli`)** image which contains `glibc` and handles host lookups without delays. Ensure you build and run using this Debian setup.

### 2. Port Allocations / Port Conflicts
If docker-compose fails due to a port bind conflict:
- **Port 8080**: Reverb has been remapped to expose host port `8090` (`8090:8080`).
- **Port 8000**: Laravel has been remapped to expose host port `8005` (`8005:8000`).
If port 5173, 5432, or 6379 are occupied, change the host-side port mapping (first number before the colon) under `ports:` in the `docker-compose.yml` file.

### 3. Cleaning the Cache and Stored Volumes
If database migrations fail or you want a fresh telemetry run:
```bash
# Stop containers and destroy PostGIS and Kafka volumes
docker compose down -v
# Rebuild and launch fresh
docker compose up -d --build
```
