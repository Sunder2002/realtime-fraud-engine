import json, joblib, redis, threading, time, os
import pandas as pd
from fastapi import FastAPI, Response
from confluent_kafka import Consumer
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import sessionmaker, declarative_base
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

# --- MONITORING METRICS ---
FRAUD_ALERTS = Counter('fraud_detected_total', 'Total fraud alerts triggered')
SAFE_PROCESSED = Counter('safe_processed_total', 'Total safe transactions processed')
PROBABILITY_GAUGE = Gauge('last_transaction_prob', 'Probability of fraud in last transaction')

# --- DATABASE SETUP ---
DB_URL = "postgresql://admin:password123@localhost:5432/fraud_db"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class TransactionRecord(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    status = Column(String)
    probability = Column(Float)

app = FastAPI()

# --- LOAD INTELLIGENCE ---
BASE = "/workspaces/realtime-fraud-engine/fraud_api"
model = joblib.load(os.path.join(BASE, 'fraud_model.xgb'))
cols = joblib.load(os.path.join(BASE, 'model_columns.pkl'))
cache = redis.Redis(host='localhost', port=6379, db=0)

def run_fraud_engine():
    time.sleep(15) 
    Base.metadata.create_all(bind=engine)
    
    c = Consumer({
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'final-stable-group', 
        'auto.offset.reset': 'latest'
    })
    c.subscribe(['fraud_transactions'])
    
    print("🧠 Sentinel Engine: Active and Monitoring Highway...")
    while True:
        msg = c.poll(1.0)
        if msg is None or msg.error(): continue
        
        try:
            val = msg.value().decode('utf-8').strip()
            if not val: continue 
            
            data = json.loads(val)
            amt = data.get('Amount', 0.0)
            
            # ML Prediction
            input_df = pd.DataFrame([data])[cols]
            prob = float(model.predict_proba(input_df)[0][1])
            
            # Velocity Check
            v_id = f"user:{data.get('V1', 'unknown')}"
            velocity = cache.incr(v_id)
            if velocity == 1: cache.expire(v_id, 60)

            is_fraud = (prob > 0.5) or (velocity > 5)
            status = "FRAUD" if is_fraud else "SAFE"

            # Save to Database
            db = SessionLocal()
            db.add(TransactionRecord(amount=amt, status=status, probability=prob))
            db.commit()
            db.close()

            # Update Metrics
            PROBABILITY_GAUGE.set(prob)
            if is_fraud:
                FRAUD_ALERTS.inc()
                print(f"🚨 ALERT: {status} | Amount: ${amt:<8} | Prob: {prob:.2%} | Saved ✅")
            else:
                SAFE_PROCESSED.inc()
                print(f"✅ Normal: {status} | Amount: ${amt:<8} | Prob: {prob:.2%} | Saved ✅")

        except Exception as e:
            pass # Silent skip for corrupted bits

threading.Thread(target=run_fraud_engine, daemon=True).start()

@app.get("/metrics")
def get_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def home(): return {"status": "Engine Live", "monitoring": "Active"}