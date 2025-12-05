import time
import pandas as pd
import joblib
import sqlite3
import random
import numpy as np
from datetime import datetime

# 1. Load Model and "Live" Data Source
model = joblib.load("models/model.joblib")
data_source = pd.read_csv("data/production_data_source.csv")

# 2. Setup SQLite (Our "Log Stream")
db_path = "data/monitoring.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
# Create a table to store inputs, predictions, and timestamps
cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        timestamp TEXT,
        mean_radius REAL,
        mean_texture REAL,
        mean_smoothness REAL,
        prediction INTEGER
    )
''')
conn.commit()

print("🚀 Producer started... Press Ctrl+C to stop.")

# 3. Simulate Traffic Loop
row_index = 0
try:
    while True:
        # Select a row from our test set
        row = data_source.iloc[row_index % len(data_source)].copy()
        
        # --- DRIFT SIMULATION LOGIC ---
        # After 50 iterations, we start corrupting the 'mean radius' feature
        # This simulates a broken sensor or data pipeline change
        if row_index > 50:
            drift_factor = np.random.uniform(1.5, 3.0) # Multiply by 1.5x to 3x
            row['mean radius'] = row['mean radius'] * drift_factor
            status = "⚠️ DRIFTED"
        else:
            status = "✅ Normal"
        
        # Make Prediction
        # (Reshape because sklearn expects 2D array)
        prediction = model.predict(pd.DataFrame([row]))[0]
        
        # Log to SQLite
        cursor.execute('''
            INSERT INTO predictions (timestamp, mean_radius, mean_texture, mean_smoothness, prediction)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            row['mean radius'],
            row['mean texture'],
            row['mean smoothness'],
            int(prediction)
        ))
        conn.commit()
        
        print(f"[{row_index}] {status} | Radius: {row['mean radius']:.2f} | Pred: {prediction}")
        
        # Wait a bit to simulate real-time traffic (fast enough for demo)
        time.sleep(0.5) 
        row_index += 1

except KeyboardInterrupt:
    print("\n🛑 Producer stopped.")
    conn.close()