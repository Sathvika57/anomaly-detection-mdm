# generate_100_anomaly_logs.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
os.makedirs("data/raw_logs", exist_ok=True)

def generate(total=500, anomaly_count=100):
    base = datetime(2025,11,1,9,0,0)
    timestamps = [base + timedelta(minutes=1*i) for i in range(total)]
    device_ids = [f"MDM{str(i%50+1).zfill(3)}" for i in range(total)]
    cpu = np.random.normal(30,8,total).round(2)
    mem = np.random.normal(45,5,total).round(2)
    resp = np.random.normal(1.2,0.4,total).round(2)
    event = np.random.choice(["checkin","app_install","sim_swap","location_update","app_crash"], total)

    idx = np.random.choice(range(total), anomaly_count, replace=False)
    cpu[idx] = np.random.uniform(85,100, anomaly_count).round(2)
    mem[idx] = np.random.uniform(85,100, anomaly_count).round(2)
    resp[idx] = np.random.uniform(10,30, anomaly_count).round(2)
    df = pd.DataFrame({
        "timestamp": timestamps,
        "device_id": device_ids,
        "cpu_usage": cpu,
        "memory_usage": mem,
        "response_time": resp,
        "event_type": event
    })
    out = "data/raw_logs/mdm_100_anomalies.csv"
    df.to_csv(out, index=False)
    print(f"✅ Generated {out} with {anomaly_count} anomalies out of {total} rows")

if __name__ == "__main__":
    generate()
