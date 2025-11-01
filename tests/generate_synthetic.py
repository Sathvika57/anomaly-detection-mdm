# tests/generate_synthetic.py
"""
Generate synthetic MDM logs with both normal and injected anomalies for testing.
Writes CSV(s) into data/data_raw/
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

OUT_DIR = "data/data_raw"
os.makedirs(OUT_DIR, exist_ok=True)

def generate(n_devices=8, days=2, anomalies_per_device=3):
    rows = []
    base = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    for d in range(n_devices):
        dev = f"D{d:04d}"
        # normal activity: hourly check-ins
        for h in range(days*24):
            ts = base - timedelta(hours=h)
            # a few events per hour
            for e in range(np.random.poisson(2)+1):
                rows.append({
                    "device_id": dev,
                    "timestamp": (ts + pd.to_timedelta(np.random.randint(0,3600), unit='s')).isoformat(),
                    "status": "200",
                    "message": "normal checkin",
                    "event_type": "checkin",
                    "app_id": "com.company.app"
                })
        # injected anomalies for device
        for a in range(anomalies_per_device):
            ts = base - timedelta(hours=np.random.randint(0, days*24))
            rows.append({
                "device_id": dev,
                "timestamp": ts.isoformat(),
                "status": "500",
                "message": "failed login attempt detected",
                "event_type": "auth_fail",
                "app_id": "com.malicious.app"
            })
            # simulated jailbreak
            if np.random.rand() < 0.3:
                rows.append({
                    "device_id": dev,
                    "timestamp": (ts + timedelta(seconds=10)).isoformat(),
                    "status": "200",
                    "message": "jailbreak/root detected",
                    "event_type": "device_integrity",
                    "app_id": "com.unknown"
                })

    df = pd.DataFrame(rows)
    fname = os.path.join(OUT_DIR, f"synthetic_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv")
    df.to_csv(fname, index=False)
    print("Generated synthetic log:", fname)

if __name__ == "__main__":
    generate(n_devices=8, days=2, anomalies_per_device=3)
