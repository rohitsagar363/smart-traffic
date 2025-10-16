# producer/producer.py

import json
import time
from kafka import KafkaProducer

KAFKA_BROKER = "localhost:29092"
TOPIC = "traffic.raw.sensors"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

with open("data/samples/anomaly_event.json") as f:
    event = json.load(f)

print(f"Sending event to topic '{TOPIC}' every 2 seconds... Press CTRL+C to stop.")

try:
    while True:
        # Add timestamp or modify event if needed
        producer.send(TOPIC, event)
        print(f"✅ Sent: {event}")
        time.sleep(2)
except KeyboardInterrupt:
    print("Stopped producer.")
