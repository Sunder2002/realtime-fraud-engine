import json, joblib, redis, threading, time, logging, sys
import pandas as pd
from fastapi import FastAPI, Response
from confluent_kafka import Consumer
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import sessionmaker, declarative_base
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Tell Python where config is
sys.path.append('/workspaces/realtime-fraud-engine')
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SentinelAPI")

# DB Setup
engine = create_engine(Config.DB_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    status = Column(String)
    probability = Column(Float)

# --- METRIC DEFINITIONS ---
FRAUD_COUNT = Counter('fraud_detected_total', 'Total frauds caught')
SAFE_COUNT = Counter('safe_processed_total', 'Total safe processed')
# We name it exactly this for Grafana
RISK_GAUGE = Gauge('current_fraud_probability', 'Live Fraud Risk Score (0-1)')

# PRO-TIP: Initialize to 0 so Prometheus sees it immediately
RISK_GAUGE.set(0.0)

app = FastAPI()

def engine_worker():
    time.sleep(15) # Wait for infrastructure
    Base.metadata.create_all(bind=engine)
    
    # Load Artifacts
    model = joblib.load(Config.MODEL_PATH)
    cols = joblib.load(Config.COLS_PATH)
    scaler = joblib.load(Config.SCALER_PATH)
    cache = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
    
    c = Consumer({
        'bootstrap.servers': Config.KAFKA_SERVER, 
        'group.id': 'sentinel-final-v3', # New group to ensure fresh start
        'auto.offset.reset': 'latest'
    })
    c.subscribe([Config.KAFKA_TOPIC])
    
    logger.info("🛡️ SENTINEL ACTIVE: Monitoring Live Highway...")
    
    while True:
        msg = c.poll(1.0)
        if msg is None or msg.error(): continue
        try:
            data = json.loads(msg.value().decode('utf-8'))
            raw_amt = float(data['Amount'])
            
            # Preprocessing
            amt_df = pd.DataFrame([[raw_amt]], columns=['Amount'])
            data['Amount'] = scaler.transform(amt_df)[0][0]
            
            # AI Inference
            input_df = pd.DataFrame([data])[cols]
            prob = float(model.predict_proba(input_df)[0][1])
            
            # Behavioral check
            v_id = f"user:{data.get('V1', 'unknown')}"
            velocity = cache.incr(v_id)
            if velocity == 1: cache.expire(v_id, 60)

            status = "FRAUD" if (prob > 0.6 or velocity > 5) else "SAFE"

            # DB Save
            db = SessionLocal()
            db.add(Transaction(amount=raw_amt, status=status, probability=prob))
            db.commit()
            db.close()

            # --- UPDATE METRICS ---
            RISK_GAUGE.set(prob) # This moves the needle in Grafana
            if status == "FRAUD": FRAUD_COUNT.inc()
            else: SAFE_COUNT.inc()
            
            logger.info(f"[{status}] Prob: {prob:.2%} | Amt: ${raw_amt:,.2f}")
        except Exception as e:
            logger.error(f"⚠️ Error: {e}")

threading.Thread(target=engine_worker, daemon=True).start()

@app.get("/metrics")
def metrics(): return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def home(): return {"status": "Sentinel v1.1 Active"}