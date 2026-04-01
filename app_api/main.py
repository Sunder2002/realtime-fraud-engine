import json, joblib, redis, threading, time, logging, sys
import pandas as pd
from fastapi import FastAPI, Response
from confluent_kafka import Consumer
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import sessionmaker, declarative_base
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

sys.path.append('/workspaces/realtime-fraud-engine')
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SentinelAPI")

engine = create_engine(Config.DB_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    status = Column(String)
    probability = Column(Float)

FRAUD_COUNT = Counter('fraud_detected_total', 'Total frauds')
SAFE_COUNT = Counter('safe_processed_total', 'Total safe')
PROB_GAUGE = Gauge('last_transaction_prob', 'Last fraud score')

app = FastAPI()

def engine_worker():
    time.sleep(15) 
    Base.metadata.create_all(bind=engine)
    
    model = joblib.load(Config.MODEL_PATH)
    cols = joblib.load(Config.COLS_PATH)
    scaler = joblib.load(Config.SCALER_PATH)
    cache = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
    
    c = Consumer({'bootstrap.servers': Config.KAFKA_SERVER, 'group.id': 'sentinel-final-v2', 'auto.offset.reset': 'latest'})
    c.subscribe([Config.KAFKA_TOPIC])
    
    logger.info("🛡️ SENTINEL ACTIVE: Watching for Real Dollars...")
    
    while True:
        msg = c.poll(1.0)
        if msg is None or msg.error(): continue
        try:
            data = json.loads(msg.value().decode('utf-8'))
            raw_amt = float(data['Amount']) # THIS IS THE REAL DOLLAR VALUE
            
            # --- INTERNAL ML SCALING ---
            # We scale a copy of the data for the model, but keep raw_amt for humans
            input_df = pd.DataFrame([data])[cols]
            input_df['Amount'] = scaler.transform(input_df[['Amount']])[0][0]
            
            prob = float(model.predict_proba(input_df)[0][1])
            
            v_id = f"user:{data.get('V1', 'unknown')}"
            velocity = cache.incr(v_id)
            if velocity == 1: cache.expire(v_id, 60)

            is_fraud = (prob > 0.6 or velocity > 5)
            status = "FRAUD" if is_fraud else "SAFE"

            # Save Real Dollars to DB
            db = SessionLocal()
            db.add(Transaction(amount=raw_amt, status=status, probability=prob))
            db.commit()
            db.close()

            PROB_GAUGE.set(prob)
            if is_fraud: 
                FRAUD_COUNT.inc()
                logger.info(f"🚨 ALERT: {status} | Prob: {prob:.2%} | Amt: ${raw_amt:,.2f}")
            else: 
                SAFE_COUNT.inc()
                logger.info(f"✅ Normal: {status} | Prob: {prob:.2%} | Amt: ${raw_amt:,.2f}")

        except Exception as e:
            logger.error(f"⚠️ Error: {e}")

threading.Thread(target=engine_worker, daemon=True).start()

@app.get("/metrics")
def metrics(): return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def home(): return {"status": "Engine Operational"}