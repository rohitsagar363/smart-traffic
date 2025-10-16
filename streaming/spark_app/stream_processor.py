# streaming/spark_app/stream_processor.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp
from pyspark.sql.types import StructType, StringType, DoubleType

KAFKA_BROKERS = "kafka:9092"
RAW_TOPIC = "traffic.raw.sensors"
CURATED_TOPIC = "traffic.curated.sensors"
ANOMALIES_TOPIC = "traffic.anomalies"

# Define schema for the incoming Kafka JSON
schema = StructType() \
    .add("sensor_id", StringType()) \
    .add("event_time", StringType()) \
    .add("z_score", DoubleType()) \
    .add("speed_kph", DoubleType()) \
    .add("lat", DoubleType()) \
    .add("lon", DoubleType()) \
    .add("reason", StringType()) \
    .add("window_sec", DoubleType())

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("TrafficStreamProcessor") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Read from Kafka
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKERS) \
    .option("subscribe", RAW_TOPIC) \
    .option("startingOffsets", "earliest") \
    .load()

# Parse JSON from Kafka value
df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json_str") \
    .withColumn("data", from_json("json_str", schema)) \
    .select("data.*") \
    .withColumn("received_at", current_timestamp())

# Filter anomalies
df_anomalies = df_parsed.filter(col("reason") == "sudden_drop")

# Write full curated stream back to Kafka
df_parsed.selectExpr("to_json(struct(*)) AS value") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKERS) \
    .option("topic", CURATED_TOPIC) \
    .option("checkpointLocation", "/tmp/checkpoints/curated") \
    .start()

# Write anomalies to separate topic
df_anomalies.selectExpr("to_json(struct(*)) AS value") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKERS) \
    .option("topic", ANOMALIES_TOPIC) \
    .option("checkpointLocation", "/tmp/checkpoints/anomalies") \
    .start() \
    .awaitTermination()
