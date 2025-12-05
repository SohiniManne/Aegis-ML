import streamlit as st
import pandas as pd
import sqlite3
import json
import time
import streamlit.components.v1 as components

# --- CONFIGURATION ---
st.set_page_config(page_title="Aegis ML Monitor", layout="wide")
DB_PATH = "data/monitoring.db"
JSON_REPORT_PATH = "reports/drift_report_latest.json"
HTML_REPORT_PATH = "reports/drift_report_latest.html"

# --- HELPER FUNCTIONS ---
def load_recent_logs(limit=100):
    """Fetch the most recent predictions from SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)
        query = f"SELECT * FROM predictions ORDER BY timestamp DESC LIMIT {limit}"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

def load_drift_status():
    """Read the latest JSON drift report."""
    try:
        with open(JSON_REPORT_PATH, 'r') as f:
            report = json.load(f)
        # Extract the global drift boolean (structure depends on Evidently version, this is standard)
        drift_detected = report['metrics'][0]['result']['dataset_drift']
        # Extract drift score (share of drifting features)
        drift_share = report['metrics'][0]['result']['drift_share']
        return drift_detected, drift_share
    except FileNotFoundError:
        return None, 0

# --- DASHBOARD LAYOUT ---

st.title("🛡️ Aegis ML: Production Monitor")
st.markdown("Real-time observability for Breast Cancer Prediction Model (v1.0)")

# 1. TOP METRICS ROW
col1, col2, col3, col4 = st.columns(4)

df_logs = load_recent_logs()
drift_detected, drift_share = load_drift_status()

with col1:
    st.metric("Total Predictions", len(df_logs) if not df_logs.empty else 0)

with col2:
    if not df_logs.empty:
        # Calculate current average radius
        avg_radius = df_logs['mean_radius'].mean()
        # Compare to baseline (approx 14.0) to show delta
        st.metric("Avg Mean Radius", f"{avg_radius:.2f}", delta=f"{avg_radius-14.12:.2f}")
    else:
        st.metric("Avg Mean Radius", "0")

with col3:
    # DRIFT STATUS INDICATOR
    if drift_detected is None:
        st.metric("Drift Status", "Waiting...", delta_color="off")
    elif drift_detected:
        st.metric("Drift Status", "CRITICAL", "Drift Detected", delta_color="inverse")
    else:
        st.metric("Drift Status", "HEALTHY", "Stable", delta_color="normal")

with col4:
    st.metric("Drifting Features", f"{drift_share * 100:.1f}%")


# 2. MAIN VISUALIZATION TABS
tab1, tab2 = st.tabs(["📈 Live Traffic", "🔍 Deep Dive Analysis"])

with tab1:
    st.subheader("Live Feature Stream")
    if not df_logs.empty:
        # Create a line chart of the input feature over time
        chart_data = df_logs.set_index('timestamp')[['mean_radius', 'mean_texture']]
        st.line_chart(chart_data)
        
        st.subheader("Recent Raw Logs")
        st.dataframe(df_logs)
    else:
        st.info("Waiting for data stream...")

with tab2:
    st.subheader("Statistical Drift Report (Evidently AI)")
    try:
        # Read the HTML file as a string
        with open(HTML_REPORT_PATH, 'r', encoding='utf-8') as f:
            html_string = f.read()
        # Render it in an iframe
        components.html(html_string, height=1000, scrolling=True)
    except FileNotFoundError:
        st.warning("No drift report found. Run 'src/monitor.py' first.")

# Auto-refresh button (Simulates real-time dashboard)
if st.button('Refresh Monitor'):
    st.rerun()