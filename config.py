import os

class Config:
    # Infrastructure
    KAFKA_SERVER = "localhost:9092"
    KAFKA_TOPIC = "fraud_transactions"
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    DB_URL = "postgresql://admin:password123@localhost:5432/fraud_db"
    
    # Base Directory
    BASE = "/workspaces/realtime-fraud-engine"
    
    # New Folder Names (Corrected)
    ARTIFACTS = os.path.join(BASE, "artifacts")
    DATA_STREAM = os.path.join(BASE, "data_stream")
    TRAINING_PIPE = os.path.join(BASE, "training_pipeline")
    
    # Files
    MODEL_PATH = os.path.join(ARTIFACTS, "fraud_model.xgb")
    COLS_PATH = os.path.join(ARTIFACTS, "model_columns.pkl")
    SCALER_PATH = os.path.join(ARTIFACTS, "scaler.pkl")
    
    RAW_DATA = os.path.join(TRAINING_PIPE, "creditcard.csv")
    UNSEEN_DATA = os.path.join(DATA_STREAM, "unseen_test_data.csv")