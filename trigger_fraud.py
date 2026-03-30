import json, time, pandas as pd
from confluent_kafka import Producer

# Connect to the Conveyor Belt (Kafka)
producer = Producer({'bootstrap.servers': 'localhost:9092'})

# 1. Load the original data
df = pd.read_csv('/workspaces/realtime-fraud-engine/model_training/creditcard.csv')

# 2. Find a row where 'Class' is 1 (This is a confirmed thief!)
thief_row = df[df['Class'] == 1].iloc[0].drop('Class').to_dict()

print("🥷 Simulating a STOLEN CARD transaction...")
producer.produce('fraud_transactions', json.dumps(thief_row).encode('utf-8'))
producer.flush()
print("✅ Done. Now check your Terminal 2 (The API) for the red alert!")