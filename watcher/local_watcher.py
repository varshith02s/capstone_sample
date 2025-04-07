import os
import time
import json
import pandas as pd
from google.cloud import pubsub_v1
from datetime import datetime

# GCP Setup
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp_credentials.json"
project_id = "daring-atrium-454004-n4"
topics = {
    "clickstream": "clickstream_topic",
    "socialmedia": "socialmedia_topic",
    "weathermarket": "weathermarket_topic"
}

# File paths
BASE_PATH = r"C:\Users\varshith.s.lv\Documents\final_datasets"
files = {
    "clickstream": os.path.join(BASE_PATH, "clickstream_data.csv"),
    "socialmedia": os.path.join(BASE_PATH, "corrected_social_media_trends.csv"),
    "weathermarket": os.path.join(BASE_PATH, "weather_market_trends (1).csv")
}

# Track last seen index
last_seen = {key: 0 for key in files}

# Pub/Sub client
publisher = pubsub_v1.PublisherClient()

def publish_new_rows(dataset_key, new_rows):
    topic_path = publisher.topic_path(project_id, topics[dataset_key])
    for _, row in new_rows.iterrows():
        message = row.to_dict()

        # Convert timestamp/date
        if "event_timestamp" in message:
            message["event_timestamp"] = pd.to_datetime(message["event_timestamp"]).isoformat()
        if "recorded_at" in message:
            message["recorded_at"] = str(pd.to_datetime(message["recorded_at"]).date())

        data = json.dumps(message).encode("utf-8")
        future = publisher.publish(topic_path, data)
        print(f"[{dataset_key.upper()}] Published: {message}")
        future.result()
        time.sleep(1)  # 1-second gap to simulate real-time

def watch_csv_files(poll_interval=5):
    print("📡 Watching CSV files for new rows...\n")
    
    # Initial ingestion of all data
    for key, file_path in files.items():
        df = pd.read_csv(file_path)
        if not df.empty:
            publish_new_rows(key, df)
            last_seen[key] = len(df)

    # Watch for new data
    while True:
        for key, file_path in files.items():
            df = pd.read_csv(file_path)
            if len(df) > last_seen[key]:
                new_rows = df.iloc[last_seen[key]:]
                publish_new_rows(key, new_rows)
                last_seen[key] = len(df)
        time.sleep(poll_interval)

if __name__ == "__main__":
    watch_csv_files()
