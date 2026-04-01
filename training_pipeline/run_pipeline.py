import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import sys, os

sys.path.append('/workspaces/realtime-fraud-engine')
from config import Config

def run_production_pipeline():
    print("🧹 [1/4] Loading Raw Data...")
    df = pd.read_csv(Config.RAW_DATA).dropna()
    
    print("✂️ [2/4] Splitting Data (Raw for Generator, Scaled for Brain)...")
    # Split first! test_df stays RAW.
    train_df, test_df = train_test_split(df, test_size=0.2, stratify=df['Class'], random_state=42)
    
    # Save RAW data for the Generator to use later
    test_df.to_csv(Config.UNSEEN_DATA, index=False)

    print("📏 [3/4] Fitting Scaler on Training Data...")
    scaler = StandardScaler()
    # We only train the scaler on the training set (Standard ML practice)
    train_amounts_scaled = scaler.fit_transform(train_df[['Amount']])
    joblib.dump(scaler, Config.SCALER_PATH)

    print("🧠 [4/4] Training Brain (XGBoost)...")
    features = [f'V{i}' for i in range(1, 29)] + ['Amount']
    
    # Prepare training features (Replace Amount with scaled version)
    X_train = train_df[features].copy()
    X_train['Amount'] = train_amounts_scaled
    y_train = train_df['Class']
    
    model = XGBClassifier(scale_pos_weight=580, n_estimators=100, max_depth=4)
    model.fit(X_train, y_train)
    
    joblib.dump(model, Config.MODEL_PATH)
    joblib.dump(features, Config.COLS_PATH)
    
    print(f"✅ Success! Artifacts in /artifacts and RAW unseen data in {Config.DATA_STREAM}")

if __name__ == "__main__":
    run_production_pipeline()