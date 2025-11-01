import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import os

fake = Faker()
os.makedirs("data/raw_logs", exist_ok=True)

def generate_synthetic_logs(n=1000, anomalies=100):
    logs = []
    base_time = datetime.now()

    for i in range(n):
        timestamp = base_time + timedelta(seconds=i * 30)
        device_id = f"device_{np.random.randint(1, 50)}"
        login_attempts = np.random.randint(1, 10)
        app_crashes = np.random.randint(0, 3)
        cpu_usage = np.random.uniform(10, 90)

        logs.append([timestamp, device_id, login_attempts, app_crashes, cpu_usage])

    df = pd.DataFrame(logs, columns=["timestamp", "device_id", "login_attempts", "app_crashes", "cpu_usage"])

    # Add anomalies
    anomaly_indices = np.random.choice(df.index, anomalies, replace=False)
    df.loc[anomaly_indices, "cpu_usage"] *= np.random.uniform(1.8, 3.0, size=anomalies)

    df.to_csv("data/raw_logs/mdm_100_anomalies.csv", index=False)
    print("✅ Synthetic logs with anomalies created at: data/raw_logs/mdm_100_anomalies.csv")

if __name__ == "__main__":
    generate_synthetic_logs()
