from flask import Flask, request
from google.cloud import bigquery
import base64
import json
import os

app = Flask(__name__)
bq_client = bigquery.Client()

TABLE_MAP = {
    "clickstream_topic": "bronze_clickstream",
    "socialmedia_topic": "bronze_social_media",
    "weathermarket_topic": "bronze_weather_market"
}

DATASET_ID = "bronze_layer"
PROJECT_ID = "daring-atrium-454004-n4"

@app.route("/", methods=["POST"])
def pubsub_to_bq():
    envelope = request.get_json()
    if not envelope or "message" not in envelope:
        return "Invalid Pub/Sub message", 400

    pubsub_message = envelope["message"]
    data = base64.b64decode(pubsub_message["data"]).decode("utf-8")
    message = json.loads(data)

    # Use the correct table based on the topic hint
    attributes = pubsub_message.get("attributes", {})
    topic_name = attributes.get("topic")

    table_id = TABLE_MAP.get(topic_name)
    if not table_id:
        return f"Unknown topic: {topic_name}", 400

    full_table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_id}"
    errors = bq_client.insert_rows_json(full_table_id, [message])
    
    if errors:
        print("BigQuery errors:", errors)
        return "Failed", 500

    print(f"Ingested to {full_table_id}: {message}")
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

