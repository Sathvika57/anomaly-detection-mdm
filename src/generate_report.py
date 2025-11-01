"""
generate_report.py
Summarizes anomalies present in data/anomalies and writes summary CSV/XLSX.
"""
import os
import pandas as pd
from datetime import datetime

ANOMALIES = "data/anomalies"
REPORTS = "reports"
os.makedirs(REPORTS, exist_ok=True)

def generate_report():
    print(f"📄 Generating anomaly report at {datetime.now()}")
    rows = []
    files = [f for f in os.listdir(ANOMALIES) if f.endswith(".csv")]
    for f in files:
        path = os.path.join(ANOMALIES, f)
        try:
            df = pd.read_csv(path)
            count = len(df)
        except Exception:
            count = 0
        rows.append({"file": f, "anomaly_count": int(count)})
    if not rows:
        print("⚠️ No anomaly files found to summarize.")
        return
    summary = pd.DataFrame(rows)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_out = os.path.join(REPORTS, f"Anomaly_Report_{ts}.csv")
    xlsx_out = os.path.join(REPORTS, f"Anomaly_Report_{ts}.xlsx")
    summary.to_csv(csv_out, index=False)
    summary.to_excel(xlsx_out, index=False)
    print(f"✅ Report saved: {csv_out} and {xlsx_out}")
    print(summary)

if __name__ == "__main__":
    generate_report()
