from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, DoubleType

# Define schema for the JSON events
schema = StructType() \
    .add("sensor_id", StringType()) \
    .add("event_time", StringType()) \
    .add("z_score", DoubleType()) \
    .add("speed_kph", DoubleType()) \
    .add("lat", DoubleType()) \
    .add("lon", DoubleType()) \
    .add("reason", StringType()) \
    .add("window_sec", DoubleType())

# Initialize Spark session with Mongo connector
print("🔧 Starting Spark session...")
spark = SparkSession.builder \
    .appName("SmartTrafficStreaming") \
    .config("spark.mongodb.write.connection.uri", "mongodb://mongodb:27017") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
print("✅ Spark session initialized.")

# Read from Kafka
print("📡 Connecting to Kafka topic: traffic.raw.sensors...")
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "traffic.raw.sensors") \
    .option("startingOffsets", "latest") \
    .load()

# Parse Kafka JSON messages
parsed_df = raw_df.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*")

# Split into curated and anomaly
curated_df = parsed_df
anomaly_df = parsed_df.filter(col("reason").isNotNull())

# Write curated to MongoDB
print("📝 Starting write stream to MongoDB collection: curated_sensors...")
curated_query = curated_df.writeStream \
    .format("mongodb") \
    .option("spark.mongodb.write.connection.uri", "mongodb://mongodb:27017") \
    .option("spark.mongodb.write.database", "traffic") \
    .option("spark.mongodb.write.collection", "curated_sensors") \
    .option("checkpointLocation", "/tmp/checkpoints/curated") \
    .outputMode("append") \
    .start()

# Write anomalies to MongoDB
print("🛑 Starting write stream to MongoDB collection: anomaly_sensors...")
anomaly_query = anomaly_df.writeStream \
    .format("mongodb") \
    .option("spark.mongodb.write.connection.uri", "mongodb://mongodb:27017") \
    .option("spark.mongodb.write.database", "traffic") \
    .option("spark.mongodb.write.collection", "anomaly_sensors") \
    .option("checkpointLocation", "/tmp/checkpoints/anomalies") \
    .outputMode("append") \
    .start()

print("🚀 Streaming job is running... Awaiting termination.")
curated_query.awaitTermination()
anomaly_query.awaitTermination()
