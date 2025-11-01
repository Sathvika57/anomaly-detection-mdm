import os
import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime

# --- CONFIG ---
INPUT_DIR = "data/processed"
OUTPUT_DIR = "data/anomalies"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def detect_anomalies_iso_forest(file_path, contamination=0.2):
    """Detect anomalies using Isolation Forest with tuned parameters."""
    df = pd.read_csv(file_path)
    numeric_df = df.select_dtypes(include=['float64', 'int64'])

    if numeric_df.shape[1] < 2:
        print(f"⚠️ {os.path.basename(file_path)} has insufficient numeric data.")
        return

    # ✅ More precise model
    model = IsolationForest(
        n_estimators=300,          # more trees = stable results
        contamination=contamination,  # model assumes ~20% anomalies
        max_samples='auto',
        random_state=42,
        bootstrap=True
    )

    model.fit(numeric_df)
    df['anomaly_score'] = model.decision_function(numeric_df)
    df['is_anomaly'] = model.predict(numeric_df)

    # Convert to 1 = anomaly, 0 = normal
    df['is_anomaly'] = df['is_anomaly'].apply(lambda x: 1 if x == -1 else 0)

    # ✅ Adaptive threshold (keeps roughly 100 anomalies if >100 found)
    total_anomalies = df['is_anomaly'].sum()
    if total_anomalies > 120:
        top_anomalies = df.nlargest(100, 'anomaly_score')
        df['is_anomaly'] = df.index.isin(top_anomalies.index).astype(int)

    anomalies = df[df['is_anomaly'] == 1]
    out_path = os.path.join(OUTPUT_DIR, f"anomalies_{os.path.basename(file_path)}")
    anomalies.to_csv(out_path, index=False)

    print(f"✅ Anomalies detected in {os.path.basename(file_path)}: {len(anomalies)} rows")
    print(f"📁 Saved to: {out_path}")

def main():
    print(f"Started tuned anomaly detection at {datetime.now()}")
    for file_name in os.listdir(INPUT_DIR):
        if file_name.endswith(".csv"):
            detect_anomalies_iso_forest(os.path.join(INPUT_DIR, file_name), contamination=0.2)
    print("✅ Finished tuned anomaly detection.")

if __name__ == "__main__":
    main()
