#!/bin/bash

echo "📌 Creating Kafka topics..."

TOPICS=("traffic.raw.sensors" "traffic.curated.sensors" "traffic.anomalies")

for TOPIC in "${TOPICS[@]}"; do
  echo "⏳ Creating topic: $TOPIC"
  kafka-topics --create \
    --if-not-exists \
    --bootstrap-server kafka:9092 \
    --replication-factor 1 \
    --partitions 1 \
    --topic "$TOPIC"
done

echo "✅ All topics created."
