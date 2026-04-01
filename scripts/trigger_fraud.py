import json, pandas as pd, sys
from confluent_kafka import Producer

sys.path.append('/workspaces/realtime-fraud-engine')
from config import Config

p = Producer({'bootstrap.servers': Config.KAFKA_SERVER})

def test_fraud():
    print("🔍 Searching for a confirmed fraud case in dataset...")
    df = pd.read_csv(Config.RAW_DATA)
    # Find a real thief from the CSV
    thief = df[df['Class'] == 1].iloc[0].drop('Class').to_dict()
    
    print(f"🥷 Sending REAL Stolen Card transaction (Amt: ${thief['Amount']})...")
    p.produce(Config.KAFKA_TOPIC, json.dumps(thief).encode('utf-8'))
    p.flush()
    print("✅ Injected. Switch to the API terminal to see the Alert!")

if __name__ == "__main__":
    test_fraud()