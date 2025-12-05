import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# 1. Setup Directories
os.makedirs("models", exist_ok=True)
os.makedirs("data", exist_ok=True)

# 2. Load Data
data = load_breast_cancer()
df = pd.DataFrame(data.data, columns=data.feature_names)
df['target'] = data.target

# 3. Split Data
X_train, X_test, y_train, y_test = train_test_split(df.drop('target', axis=1), df['target'], test_size=0.3, random_state=42)

# 4. Train Model
model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
model.fit(X_train, y_train)

# 5. Save Artifacts
joblib.dump(model, "models/model.joblib")

# --- FIX: ADD PREDICTION COLUMN TO REFERENCE DATA ---
# We must generate predictions on the training set so Evidently 
# has a baseline to compare against.
reference_df = X_train.copy()
reference_df['prediction'] = model.predict(X_train)

# Save the REFERENCE data (Features + Prediction)
reference_df.to_csv("data/reference_data.csv", index=False)

# Save the PRODUCTION Source (Features only, acts as "New Traffic")
X_test.to_csv("data/production_data_source.csv", index=False)

print("✅ Model trained. Reference data (with predictions) saved.")