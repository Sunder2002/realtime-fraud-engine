import time, json, pandas as pd, numpy as np, os
from confluent_kafka import Producer

producer = Producer({'bootstrap.servers': 'localhost:9092'})

def stream_transactions():
    BASE = "/workspaces/realtime-fraud-engine/data_generator"
    df = pd.read_csv(os.path.join(BASE, 'unseen_test_data.csv')).drop('Class', axis=1)

    print(f"🚀 Streaming transactions...")
    
    for _, row in df.iterrows():
        try:
            transaction = row.to_dict()
            # Add stochastic noise
            for v_col in [f'V{i}' for i in range(1, 29)]:
                transaction[v_col] += np.random.normal(0, 0.01)
            
            payload = json.dumps(transaction)
            producer.produce('fraud_transactions', payload.encode('utf-8'))
            producer.flush() # Ensure it leaves the generator immediately
            time.sleep(0.5)
        except Exception as e:
            print(f"Generator Error: {e}")

if __name__ == "__main__":
    stream_transactions()