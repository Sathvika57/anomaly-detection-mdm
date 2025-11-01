"""
parse_logs.py
Reads CSV files from data/raw_logs, filters rows by timestamp range (if provided),
and writes processed CSVs to data/processed/.
Usage (args passed from batch):
    python src/parse_logs.py <start_date YYYYMMDD or empty> <start_time HHMM or empty> <end_date or empty> <end_time or empty>
"""
import os, sys
import pandas as pd
from datetime import datetime

RAW = "data/raw_logs"
PROCESSED = "data/processed"
os.makedirs(PROCESSED, exist_ok=True)

def parse_file(file_path, start_dt=None, end_dt=None):
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"❌ Failed to read {file_path}: {e}")
        return None

    if "timestamp" not in df.columns:
        print(f"⚠️ Skipping {os.path.basename(file_path)} (no 'timestamp' column).")
        return None

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    if start_dt:
        df = df[df["timestamp"] >= start_dt]
    if end_dt:
        df = df[df["timestamp"] <= end_dt]
    return df

def parse_all(start_date, start_time, end_date, end_time):
    # Convert input strings to datetimes if provided
    def to_dt(d, t, is_end=False):
        if not d:
            return None
        if not t:
            t = "0000" if not is_end else "2359"
        try:
            return datetime.strptime(d + t, "%Y%m%d%H%M")
        except Exception:
            return None

    start_dt = to_dt(start_date, start_time, is_end=False)
    end_dt = to_dt(end_date, end_time, is_end=True)

    files = [f for f in os.listdir(RAW) if f.lower().endswith(".csv")]
    if not files:
        print("⚠️ No CSV files found in data/raw_logs/")
        return 0

    processed_count = 0
    for f in files:
        p = os.path.join(RAW, f)
        df = parse_file(p, start_dt, end_dt)
        if df is None or df.empty:
            print(f"⚠️ No matching data for {f} in requested range.")
            continue
        out = os.path.join(PROCESSED, f"processed_{f}")
        df.to_csv(out, index=False)
        processed_count += 1
        print(f"✅ Processed and saved: {out} (rows: {len(df)})")

    print("Finished parsing all log files.")
    return processed_count

if __name__ == "__main__":
    start_date = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() != "" else None
    start_time = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].strip() != "" else None
    end_date = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3].strip() != "" else None
    end_time = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4].strip() != "" else None

    print(f"Started log parsing at {datetime.now()}")
    parse_all(start_date, start_time, end_date, end_time)
