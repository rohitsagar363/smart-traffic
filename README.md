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

