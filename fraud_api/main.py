from fastapi import FastAPI
import threading
import time
import json
from kafka import KafkaConsumer
import joblib
import os

app = FastAPI()

# Global counters
total_fraud = 0
total_safe = 0

# Load the model (though we'll use mock prediction)
model_path = os.path.join(os.path.dirname(__file__), 'fraud_model.xgb')
model = joblib.load(model_path)

def consume_transactions():
    global total_fraud, total_safe
    consumer = KafkaConsumer(
        'fraud_transactions',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='fraud_detector',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    for message in consumer:
        transaction = message.value
        amount = transaction['amount']
        
        # Mock prediction: if amount > 4500, flag as fraud
        is_fraud = amount > 4500
        
        if is_fraud:
            total_fraud += 1
            print(f"Fraud detected: {transaction}")
        else:
            total_safe += 1
            print(f"Safe transaction: {transaction}")

@app.on_event("startup")
def startup_event():
    # Start background thread for consuming Kafka messages
    thread = threading.Thread(target=consume_transactions, daemon=True)
    thread.start()

@app.get("/metrics")
def get_metrics():
    # Prometheus format
    metrics = f"""# HELP total_fraud Total number of fraudulent transactions detected
# TYPE total_fraud counter
total_fraud {total_fraud}

# HELP total_safe Total number of safe transactions
# TYPE total_safe counter
total_safe {total_safe}
"""
    return metrics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)