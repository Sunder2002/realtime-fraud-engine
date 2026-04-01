import os

class Config:
    KAFKA_SERVER = "localhost:9092"
    KAFKA_TOPIC = "fraud_transactions"
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    DB_URL = "postgresql://admin:password123@localhost:5432/fraud_db"
    
    BASE = "/workspaces/realtime-fraud-engine"
    ARTIFACTS = os.path.join(BASE, "artifacts")
    
    MODEL_PATH = os.path.join(ARTIFACTS, "fraud_model.xgb")
    COLS_PATH = os.path.join(ARTIFACTS, "model_columns.pkl")
    SCALER_PATH = os.path.join(ARTIFACTS, "scaler.pkl")
    
    RAW_DATA = os.path.join(BASE, "training_pipeline/creditcard.csv")
    UNSEEN_DATA = os.path.join(BASE, "data_stream/unseen_test_data.csv")

    # --- NEW: SAFETY & LOGGING ---
    LOG_FILE = os.path.join(BASE, "sentinel.log")
