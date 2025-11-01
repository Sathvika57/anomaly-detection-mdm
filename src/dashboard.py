"""
dashboard.py
Streamlit dashboard to show latest anomaly file (largest non-empty) from data/anomalies.
"""
import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="MDM Anomaly Detection Dashboard", layout="wide")
st.title("📊 MDM Anomaly Detection Dashboard")
st.caption("Live monitoring of unusual device activities in MTM Blocks")

ANOMALIES = "data/anomalies"
if not os.path.exists(ANOMALIES):
    st.warning("No anomalies directory found. Run the pipeline first.")
else:
    files = [os.path.join(ANOMALIES, f) for f in os.listdir(ANOMALIES) if f.endswith(".csv")]
    if not files:
        st.warning("No anomalies detected yet. Waiting for logs...")
    else:
        # choose largest CSV (most records) to show
        largest = max(files, key=lambda p: os.path.getsize(p))
        df = pd.read_csv(largest)

        st.sidebar.header("Run Info")
        st.sidebar.write("File:")
        st.sidebar.write(os.path.basename(largest))
        st.sidebar.write("Rows:")
        st.sidebar.write(len(df))

        if df.empty:
            st.success("No anomalies detected.")
        else:
            # High-level metrics
            total_window = st.sidebar.empty()
            anomalies_count = len(df)
            devices_monitored = df['device_id'].nunique() if 'device_id' in df.columns else 'N/A'

            st.markdown("### Run Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total window records (latest run)", str(df.shape[0]))
            col2.metric("Anomalies flagged", str(anomalies_count))
            col3.metric("Devices monitored", str(devices_monitored))

            # time series if timestamp exists
            if 'timestamp' in df.columns:
                try:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                    times = df.groupby(pd.Grouper(key='timestamp', freq='1H')).size()
                    st.line_chart(times)
                except Exception:
                    pass

            # show top anomaly features if exist
            st.markdown("### Top anomalies (first 100 rows)")
            st.dataframe(df.head(100))

            # show distribution of anomaly scores (if present)
            if 'anomaly_score' in df.columns:
                st.markdown("### Anomaly score distribution")
                st.bar_chart(df['anomaly_score'].abs().sort_values(ascending=False).head(50))

            st.markdown("### Download")
            st.download_button("Download anomaly CSV", data=open(largest, "rb"), file_name=os.path.basename(largest))
