import os
import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime

PROCESSED_PATH = "data/processed"
ANOMALIES_PATH = "data/anomalies"
os.makedirs(ANOMALIES_PATH, exist_ok=True)

def detect_anomalies():
    print(f"Started anomaly detection at {datetime.now()}")

    for file in os.listdir(PROCESSED_PATH):
        if not file.endswith(".csv"):
            continue

        df = pd.read_csv(os.path.join(PROCESSED_PATH, file))
        if df.empty:
            continue

        numeric_df = df.select_dtypes(include=['number'])
        if numeric_df.empty:
            continue

        model = IsolationForest(contamination=0.02, random_state=42)
        df["anomaly"] = model.fit_predict(numeric_df)
        anomalies = df[df["anomaly"] == -1]

        out_path = os.path.join(ANOMALIES_PATH, f"anomalies_{file}")
        anomalies.to_csv(out_path, index=False)

        print(f"✅ Anomalies detected in {file}: {len(anomalies)} rows")
        print(f"📁 Saved to: {out_path}")

    print("Finished anomaly detection.")

if __name__ == "__main__":
    detect_anomalies()
