import os, time
import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="MDM Anomaly Dashboard", layout="wide")

ANOMALY_PATH = "data/anomalies"

def load_latest_anomalies():
    files = [f for f in os.listdir(ANOMALY_PATH) if f.endswith(".csv")]
    if not files:
        return pd.DataFrame()
    files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(ANOMALY_PATH, x)), reverse=True)
    latest_file = os.path.join(ANOMALY_PATH, files[0])
    df = pd.read_csv(latest_file)
    return df

st.title("📊 MDM Anomaly Detection Dashboard")
st.caption("Live monitoring of unusual device activities in MTM Blocks")

placeholder = st.empty()

while True:
    df = load_latest_anomalies()
    if df.empty:
        placeholder.warning("No anomalies detected yet. Waiting for logs...")
    else:
        total = len(df)
        st.success(f"✅ {total} anomalies detected as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.dataframe(df.tail(10))
        st.bar_chart(df['event_type'].value_counts())

        if 'timestamp' in df.columns:
            st.line_chart(df.groupby('timestamp').size())

    time.sleep(10)  # auto refresh every 10 seconds
