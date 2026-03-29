import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

# Create dummy training data
np.random.seed(42)
n_samples = 10000

data = {
    'amount': np.random.uniform(10, 10000, n_samples),
    'user_id': np.random.randint(1000, 10000, n_samples),
    'location': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'], n_samples),
    'fraud': np.random.choice([0, 1], n_samples, p=[0.95, 0.05])  # 5% fraud
}

df = pd.DataFrame(data)

# Encode location
df['location_encoded'] = df['location'].astype('category').cat.codes

# Features and target
X = df[['amount', 'user_id', 'location_encoded']]
y = df['fraud']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train XGBoost model
model = XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {accuracy:.4f}")

# Save model
model_path = os.path.join(os.path.dirname(__file__), '..', 'fraud_api', 'fraud_model.xgb')
joblib.dump(model, model_path)
print(f"Model saved to {model_path}")