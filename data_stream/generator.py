import time, json, pandas as pd, numpy as np, os, sys
from confluent_kafka import Producer

# Absolute import fix
sys.path.append('/workspaces/realtime-fraud-engine')
from config import Config

producer = Producer({'bootstrap.servers': Config.KAFKA_SERVER})

def stream_transactions():
    if not os.path.exists(Config.UNSEEN_DATA):
        print(f"❌ Error: {Config.UNSEEN_DATA} not found! Run the training pipeline first.")
        return

    df = pd.read_csv(Config.UNSEEN_DATA).drop('Class', axis=1)
    print(f"🚀 Streaming from {Config.UNSEEN_DATA}...")
    
    for _, row in df.iterrows():
        try:
            transaction = row.to_dict()
            # Add stochastic noise to V columns
            for i in range(1, 29):
                transaction[f'V{i}'] += np.random.normal(0, 0.01)
            
            producer.produce(Config.KAFKA_TOPIC, json.dumps(transaction).encode('utf-8'))
            producer.flush() 
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠️ Streamer Error: {e}")

if __name__ == "__main__":
    stream_transactions()