import pandas as pd
from xgboost import XGBClassifier
import joblib

print("🚀 Loading REAL Dataset...")
df = pd.read_csv("creditcard.csv")

# The real dataset has 'Time', 'Amount', 'V1-V28', and 'Class'
X = df.drop('Class', axis=1)
y = df['Class']

print("🧠 Training Real XGBoost Model...")
model = XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1)
model.fit(X, y)

# Save the brain and the column names (very important for real systems!)
joblib.dump(model, '../fraud_api/fraud_model.xgb')
joblib.dump(X.columns.tolist(), '../fraud_api/model_columns.pkl')

print("✅ Model trained and exported to fraud_api/")