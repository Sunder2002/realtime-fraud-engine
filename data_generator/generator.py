import json
import time
import random
import uuid
from datetime import datetime
from kafka import KafkaProducer

# Kafka configuration
KAFKA_BROKER = 'localhost:9092'
TOPIC = 'fraud_transactions'

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_transaction():
    return {
        'transaction_id': str(uuid.uuid4()),
        'user_id': random.randint(1000, 9999),
        'amount': round(random.uniform(10.0, 10000.0), 2),
        'location': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
        'timestamp': datetime.utcnow().isoformat()
    }

def main():
    print("Starting data generator...")
    while True:
        transaction = generate_transaction()
        producer.send(TOPIC, transaction)
        print(f"Sent transaction: {transaction}")
        time.sleep(0.5)

if __name__ == "__main__":
    main()