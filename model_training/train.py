import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

# Absolute paths for reliability
BASE_DIR = "/workspaces/realtime-fraud-engine"
DATA_FILE = os.path.join(BASE_DIR, "model_training/creditcard.csv")

def train_sentinel_model():
    print("📂 Step 1: Loading Real Dataset...")
    df = pd.read_csv(DATA_FILE)

    print("✂️ Step 2: Splitting Data (80% Train / 20% Unseen Simulation)...")
    train_df, test_df = train_test_split(df, test_size=0.2, stratify=df['Class'], random_state=42)

    # Features: V1-V28 and Amount (Kaggle Standard)
    features = [f'V{i}' for i in range(1, 29)] + ['Amount']
    X_train = train_df[features]
    y_train = train_df['Class']

    print(f"🧠 Step 3: Training XGBoost Reasoning Machine on {len(X_train)} transactions...")
    # scale_pos_weight=580 handles the 0.17% fraud ratio
    model = XGBClassifier(
        scale_pos_weight=580, 
        n_estimators=100, 
        max_depth=4,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    model.fit(X_train, y_train)

    print("💾 Step 4: Exporting Intelligence to API folder...")
    joblib.dump(model, os.path.join(BASE_DIR, 'fraud_api/fraud_model.xgb'))
    joblib.dump(features, os.path.join(BASE_DIR, 'fraud_api/model_columns.pkl'))

    print("📦 Step 5: Saving hidden test data for the live generator...")
    test_df.to_csv(os.path.join(BASE_DIR, 'data_generator/unseen_test_data.csv'), index=False)
    print("✅ System Ready: Intelligence is synced across all layers.")

if __name__ == "__main__":
    train_sentinel_model()