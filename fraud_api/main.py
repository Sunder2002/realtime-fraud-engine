import json, joblib, threading, redis
import pandas as pd
from fastapi import FastAPI
from kafka import KafkaConsumer
from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. SETUP DATABASE (PostgreSQL)
DB_URL = "postgresql://admin:password123@localhost:5432/fraud_db"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class TransactionRecord(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    prediction = Column(String) # 'FRAUD' or 'SAFE'

Base.metadata.create_all(bind=engine)

# 2. SETUP CACHE (Redis)
cache = redis.Redis(host='localhost', port=6379, db=0)

# 3. LOAD MODEL
model = joblib.load('fraud_model.xgb')
model_cols = joblib.load('model_columns.pkl')

app = FastAPI()

def process_stream():
    consumer = KafkaConsumer('fraud_transactions', bootstrap_servers='localhost:9092',
                             value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    
    for msg in consumer:
        data = msg.value
        user_id = data.get('V1', 'unknown') # Using V1 as a dummy user_id
        
        # --- REAL WORLD LOGIC: VELOCITY CHECK ---
        # If a user appears more than 5 times in 60 seconds, flag as suspicious
        user_count = cache.incr(user_id)
        if user_count == 1:
            cache.expire(user_id, 60)
        
        # --- MACHINE LEARNING PREDICTION ---
        input_df = pd.DataFrame([data])[model_cols]
        pred = model.predict(input_df)[0]
        status = "FRAUD" if (pred == 1 or user_count > 5) else "SAFE"
        
        # --- PERMANENT STORAGE ---
        db = SessionLocal()
        record = TransactionRecord(amount=data['Amount'], prediction=status)
        db.add(record)
        db.commit()
        db.close()
        
        print(f"Result: {status} | Amount: {data['Amount']} | User Velocity: {user_count}")

threading.Thread(target=process_stream, daemon=True).start()

@app.get("/health")
def health():
    return {"status": "running"}