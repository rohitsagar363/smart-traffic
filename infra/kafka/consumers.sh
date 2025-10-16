#!/usr/bin/env bash
set -euo pipefail
BROKERS="${BROKERS:-kafka:9092}"
TOPIC="${1:-traffic.raw.sensors}"

kafka-console-consumer --bootstrap-server "$BROKERS" --topic "$TOPIC" --from-beginning
