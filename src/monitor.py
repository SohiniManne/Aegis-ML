import sqlite3
import pandas as pd
import json
import os
from datetime import datetime

# Import Aegis's core detection engine
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

# --- CONFIGURATION ---
DB_PATH = "data/monitoring.db"
REF_DATA_PATH = "data/reference_data.csv"
REPORTS_DIR = "reports"
WINDOW_SIZE = 500

os.makedirs(REPORTS_DIR, exist_ok=True)

def load_data():
    """
    Loads Reference and Current data, ensuring schemas match perfectly.
    """
    # 1. Load Reference Data (The CSV has 30 cols, we only want 3 + prediction)
    reference = pd.read_csv(REF_DATA_PATH)
    
    # Define exactly which columns we are monitoring
    # These must match the names in the CSV exactly (spaces, not underscores)
    monitored_features = ['mean radius', 'mean texture', 'mean smoothness', 'prediction']
    
    # Filter reference to only these columns
    reference = reference[monitored_features]
    
    # 2. Load Current Data from SQLite
    conn = sqlite3.connect(DB_PATH)
    # query selects the columns using SQL names (underscores)
    query = f"""
    SELECT mean_radius, mean_texture, mean_smoothness, prediction 
    FROM predictions 
    ORDER BY timestamp DESC 
    LIMIT {WINDOW_SIZE}
    """
    current = pd.read_sql_query(query, conn)
    conn.close()
    
    # 3. SCHEMA ALIGNMENT (Crucial Step)
    # Rename SQLite columns (underscores) to match CSV columns (spaces)
    current = current.rename(columns={
        'mean_radius': 'mean radius',
        'mean_texture': 'mean texture',
        'mean_smoothness': 'mean smoothness'
    })
    
    # Ensure column types match (sometimes SQLite returns floats as strings)
    current['prediction'] = current['prediction'].astype(int)
    
    return reference, current

def run_analysis():
    # REMOVED EMOJI HERE
    print(f"[*] Aegis ML: Starting Drift Analysis...")
    
    try:
        reference, current = load_data()
        
        if len(current) < 10:
            # REMOVED EMOJI HERE
            print("[!] Not enough data. Run producer.py longer.")
            return

        print(f"   Analyzing {len(current)} logs against reference data...")

        # --- THE MATHEMATICAL CORE ---
        drift_report = Report(metrics=[
            DataDriftPreset(), 
        ])
        
        drift_report.run(reference_data=reference, current_data=current)
        
        # --- ARTIFACT GENERATION ---
        json_path = f"{REPORTS_DIR}/drift_report_latest.json"
        drift_report.save_json(json_path)
        
        html_path = f"{REPORTS_DIR}/drift_report_latest.html"
        drift_report.save_html(html_path)

        # Check result
        with open(json_path, 'r') as f:
            metrics = json.load(f)
            
        drift_detected = metrics['metrics'][0]['result']['dataset_drift']
        
        if drift_detected:
            # REMOVED EMOJI HERE
            print(f"[ALERT] DRIFT DETECTED! View report at: {html_path}")
        else:
            # REMOVED EMOJI HERE
            print(f"[OK] System Healthy. View report at: {html_path}")

    except Exception as e:
        # REMOVED EMOJI HERE
        print(f"[X] Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_analysis()