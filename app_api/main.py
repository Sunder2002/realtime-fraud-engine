import json, joblib, redis, threading, time, logging, sys
from logging.handlers import RotatingFileHandler
import pandas as pd
from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel, Field
from confluent_kafka import Consumer
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import sessionmaker, declarative_base
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

sys.path.append('/workspaces/realtime-fraud-engine')
from config import Config

# --- STEP 1: INDUSTRIAL LOGGING (The Black Box) ---
log_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
file_handler = RotatingFileHandler(Config.LOG_FILE, maxBytes=5*1024*1024, backupCount=2)
file_handler.setFormatter(log_formatter)

logger = logging.getLogger("Sentinel")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(logging.StreamHandler()) # Still show in terminal

# --- STEP 2: DATA VALIDATION (The Shield) ---
class TransactionSchema(BaseModel):
    # Ensures incoming Kafka data isn't corrupted
    Amount: float = Field(..., gt=-1)
    V1: float
    V2: float
    # We could list all 28, but keeping it brief for the schema check
    class Config:
        extra = "allow" # Allows the other V columns

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

# Metrics
FRAUD_COUNT = Counter('fraud_detected_total', 'Total frauds')
SAFE_COUNT = Counter('safe_processed_total', 'Total safe')
RISK_GAUGE = Gauge('last_transaction_prob', 'Last fraud score')

app = FastAPI(title="Sentinel Fraud Engine", version="1.2.0")

def engine_worker():
    logger.info("🚀 Sentinel worker initializing...")
    time.sleep(15) 
    Base.metadata.create_all(bind=engine)
    
    try:
        model = joblib.load(Config.MODEL_PATH)
        cols = joblib.load(Config.COLS_PATH)
        scaler = joblib.load(Config.SCALER_PATH)
        cache = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
        
        c = Consumer({'bootstrap.servers': Config.KAFKA_SERVER, 'group.id': 'sentinel-vfinal', 'auto.offset.reset': 'latest'})
        c.subscribe([Config.KAFKA_TOPIC])
    except Exception as e:
        logger.critical(f"❌ Failed to load artifacts: {e}")
        return

    while True:
        msg = c.poll(1.0)
        if msg is None or msg.error(): continue
        
        try:
            raw_data = json.loads(msg.value().decode('utf-8'))
            
            # --- VALIDATION ---
            tx = TransactionSchema(**raw_data)
            
            # --- INFERENCE ---
            input_df = pd.DataFrame([tx.model_dump()])[cols]
            input_df['Amount'] = scaler.transform(input_df[['Amount']])[0][0]
            prob = float(model.predict_proba(input_df)[0][1])
            
            v_id = f"user:{tx.V1}"
            velocity = cache.incr(v_id)
            if velocity == 1: cache.expire(v_id, 60)

            status = "FRAUD" if (prob > 0.6 or velocity > 5) else "SAFE"

            # --- PERSISTENCE ---
            db = SessionLocal()
            db.add(Transaction(amount=tx.Amount, status=status, probability=prob))
            db.commit()
            db.close()

            # --- TELEMETRY ---
            RISK_GAUGE.set(prob)
            if status == "FRAUD": FRAUD_COUNT.inc()
            else: SAFE_COUNT.inc()
            
            logger.info(f"AUDIT | Status: {status} | Amt: ${tx.Amount} | Prob: {prob:.4f}")

        except Exception as e:
            logger.error(f"⚠️ Transaction Rejected: {e}")

threading.Thread(target=engine_worker, daemon=True).start()

@app.get("/health")
def health_check():
    # HR loves health checks. It shows you know how Kubernetes monitors apps.
    return {"status": "healthy", "uptime": time.time()}

@app.get("/metrics")
def metrics(): return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
