#!/usr/bin/env bash
set -euo pipefail

BROKERS="${BROKERS:-kafka:9092}"

create() {
  local topic="$1"
  local partitions="${2:-3}"
  local retention_ms="${3:-604800000}" # 7 days
  kafka-topics --bootstrap-server "$BROKERS" --create \
    --topic "$topic" --partitions "$partitions" --replication-factor 1 \
    --config retention.ms="$retention_ms" \
    --config cleanup.policy=delete \
    --config min.insync.replicas=1
}

echo "Creating topics on $BROKERS ..."
create traffic.raw.sensors 3 604800000
create traffic.curated.sensors 3 1209600000
create traffic.anomalies 3 1209600000

echo "Listing topics:"
kafka-topics --bootstrap-server "$BROKERS" --list
