# 🚦 Smart Traffic Project — Step 1: Infrastructure Setup

This step sets up the base infrastructure using Docker Compose. It includes essential components like Kafka, Zookeeper, MongoDB, Spark, and Grafana — all containerized and ready for the smart traffic pipeline.

---

## ✅ Components Launched

| Service     | Port(s)     | Description                     |
|-------------|-------------|----------------------------------|
| Zookeeper   | 2181        | Kafka's dependency for metadata |
| Kafka       | 9092        | Messaging broker                |
| MongoDB     | 27017       | Storage for traffic data        |
| Spark       | (Internal)  | Processing engine               |
| Grafana     | 3000        | Dashboard and metrics           |

---

## 🚀 Getting Started

### 1. Start the Containers

```bash
cd infra
docker compose up -d
```

This will spin up:
- Zookeeper
- Kafka
- MongoDB
- Spark
- Grafana

### 2. Verify All Containers

```bash
docker compose ps
```

You should see all services `Up (healthy)`.

---

## 📦 Kafka Topic Setup

Kafka topics are **not auto-created** by default. Run the script **inside the Kafka container**:

### Option A: Manual Topic Creation

```bash
docker compose exec kafka bash
bash /data/kafka/create_topics.sh
```

Creates the following topics:

| Topic                    | Partitions | Retention (ms) |
|--------------------------|------------|----------------|
| `traffic.raw.sensors`    | 3          | 604800000 (7d) |
| `traffic.curated.sensors`| 3          | 1209600000 (14d) |
| `traffic.anomalies`      | 3          | 1209600000 (14d) |

---

## 👂 Consume Kafka Messages

To read from a topic:

```bash
docker compose exec kafka bash
bash /data/kafka/consumers.sh traffic.raw.sensors
```

You can replace the topic name to view other topics too.

---

## 📊 Access Grafana Dashboard

After containers are running:

- Open: [http://localhost:3000](http://localhost:3000)
- Default credentials:
  - **Username:** `admin`
  - **Password:** `admin`

---

## 🗂 Directory Structure

```
smart-traffic/
├── infra/
│   ├── docker-compose.yaml
│   └── kafka/
│       ├── create_topics.sh
│       └── consumers.sh
├── data/
│   └── samples/
│       └── anomaly_event.json  # Not used in Step 1
```

---

## 🧪 Health Checks

You can check the logs or run:

```bash
docker compose logs --tail=50 kafka
```

All services should be healthy.

---

### ✅ Step 2: Kafka Producers and Consumers

This step sets up the basic data flow using Kafka, simulating real-time traffic sensor data.

#### 🛠️ Components

- **Kafka Topics**:
  - `traffic.raw.sensors`
  - `traffic.curated.sensors`
  - `traffic.anomalies`

- **Producer**:
  - `producer.py`: Sends sample sensor readings (e.g., speed, location, z-score) to Kafka topics.

- **Consumer**:
  - `infra/kafka/consumers.sh`: Bash-based Kafka console consumer for testing.

#### 🧪 How to Test

```bash
# Run Bash consumer for a topic
docker compose exec kafka bash
bash /data/kafka/consumers.sh traffic.raw.sensors


# Run Python producer to send test messages
python producer.py

--

### ⚙️ Step 3: Spark Streaming — Enrichment & Filtering

In this step, we implemented a **Spark Structured Streaming job** to consume sensor data from Kafka, enrich it, and split it into curated and anomaly streams.

---

### 🎯 Goals

- Read JSON events from `traffic.raw.sensors` Kafka topic.
- Enrich each event (e.g., parse timestamps, derive speed categories, etc.).
- Apply basic **anomaly detection** (e.g., high `z_score`).
- Write:
  - **All enriched data** to `traffic.curated.sensors`
  - **Only anomalies** to `traffic.anomalies`

---

### 🛠️ Components

| File                                     | Purpose                                          |
|------------------------------------------|--------------------------------------------------|
| `streaming/spark_app/stream_processor.py` | Main Spark job that reads, enriches, and filters |
| `infra/docker-compose.yaml`              | Defines Spark service and mounts code volume     |

---

### 📦 Kafka Topics

| Topic                    | Description                             |
|--------------------------|-----------------------------------------|
| `traffic.raw.sensors`    | Raw data from Kafka producer            |
| `traffic.curated.sensors`| All enriched sensor records             |
| `traffic.anomalies`      | Filtered records with high `z_score`    |

---

### 🚀 Run the Spark Job

This is handled automatically via `docker-compose`. The `spark` service will:

- Use the official image: `apache/spark:3.5.1-java17`
- Run `spark-submit` on `stream_processor.py`
- Use `spark-sql-kafka` dependency

To re-run Spark manually if needed:

```bash
docker compose restart spark


## 🧩 Step 4: MongoDB Sink — Persist to Database

In this step, we created a **new Spark Structured Streaming job** (`stream_processor_mongo.py`) to store both curated and anomaly data directly into **MongoDB** collections, allowing us to persist enriched streaming data for further querying and visualization.

---

### 🎯 Goals

- Read JSON events from Kafka topic `traffic.raw.sensors`
- Parse and enrich events using Spark
- Split into:
  - `curated_sensors` (all events)
  - `anomaly_sensors` (events with non-null `reason`)
- Store each stream in MongoDB collections using Spark Connector

---

### 🛠️ Components

| File                                       | Purpose                                                   |
|-------------------------------------------|-----------------------------------------------------------|
| `streaming/spark_app/stream_processor_mongo.py` | Spark job that writes curated and anomaly data to MongoDB |
| `mongodb` container                        | Stores all sensor data in collections under `traffic` DB  |

---

### 🗃 MongoDB Collections

| Database | Collection         | Description                        |
|----------|--------------------|------------------------------------|
| `traffic` | `curated_sensors`  | All enriched/valid sensor events   |
| `traffic` | `anomaly_sensors`  | Events flagged as anomalies        |

---

### 🚀 Run the Spark Job

If your container is configured correctly, the job will run automatically when you start the stack:

```bash
docker compose restart spark
```

To manually run only this MongoDB Spark job:

```bash
docker compose exec spark spark-submit /opt/workspace/streaming/spark_app/stream_processor_mongo.py
```

---

### 🧪 Verify MongoDB Storage

**Option 1: Terminal — `mongosh`**

```bash
docker compose exec mongodb mongosh
```

```javascript
use traffic;
db.curated_sensors.find().pretty();
db.anomaly_sensors.find().pretty();
```

**Option 2: MongoDB Compass**

- Install via Homebrew:
  ```bash
  brew install --cask mongodb-compass
  ```
- Connect to:
  ```
  mongodb://localhost:27017
  ```
- Browse the `traffic` DB and view documents

---

### 💡 Notes

- Checkpoints:
  - Curated: `/tmp/checkpoints/curated`
  - Anomalies: `/tmp/checkpoints/anomalies`
- This job **does not write back** to Kafka — it’s focused solely on MongoDB persistence
- Data is now queryable, indexable, and ready for dashboards (via Compass or Grafana Mongo plugin)

---

✅ **Next:** Use MongoDB data to create interactive Grafana dashboards (Step 5)
