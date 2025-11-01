# src/parse_normalize.py
"""
Select and normalize a raw CSV log into data/data_clean/clean_{timestamp}.csv
Usage:
    python src/parse_normalize.py --date 20250917 --time 2116
If no date/time provided, the script uses the latest CSV in data/data_raw/.
"""
import argparse, os
import pandas as pd
from datetime import datetime

RAW_DIR = "data/data_raw"
CLEAN_DIR = "data/data_clean"
os.makedirs(CLEAN_DIR, exist_ok=True)

def select_file(folder, date_substr="", time_substr=""):
    files = [f for f in os.listdir(folder) if f.lower().endswith(".csv")]
    if not files:
        raise FileNotFoundError(f"No CSV files in {folder}")
    files = sorted(files)
    if date_substr:
        for f in reversed(files):
            if date_substr in f and (not time_substr or time_substr in f):
                return os.path.join(folder, f)
        raise FileNotFoundError(f"No file matching date {date_substr} time {time_substr}")
    return os.path.join(folder, files[-1])

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # standardize common column names
    cmap = {}
    for c in df.columns:
        lc = c.lower()
        if "device" in lc and "id" in lc:
            cmap[c] = "device_id"
        elif "timestamp" in lc or "time" in lc:
            cmap[c] = "timestamp"
        elif "status" in lc:
            cmap[c] = "status"
        elif "message" in lc or "msg" in lc:
            cmap[c] = "message"
        elif "app" in lc and "id" in lc:
            cmap[c] = "app_id"
        elif "event" in lc and ("type" in lc or True):
            cmap[c] = "event_type"
    df = df.rename(columns=cmap)
    # parse timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    else:
        # attempt to parse first column
        try:
            df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], errors="coerce", utc=True)
            df = df.rename(columns={df.columns[0]:"timestamp"})
        except Exception:
            raise ValueError("No timestamp found or parsed")
    # basic cleanup
    df = df.drop_duplicates().reset_index(drop=True)
    return df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="", help="substring to match in filename (YYYYMMDD)")
    parser.add_argument("--time", default="", help="time substring (HHMM)")
    args = parser.parse_args()

    try:
        src = select_file(RAW_DIR, args.date, args.time)
    except Exception as e:
        print("ERROR selecting file:", e)
        raise SystemExit(1)
    print("Using raw file:", src)
    df = pd.read_csv(src, low_memory=False)
    try:
        df = normalize_columns(df)
    except Exception as e:
        print("ERROR normalizing:", e)
        raise SystemExit(1)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(CLEAN_DIR, f"clean_{ts}.csv")
    df.to_csv(out, index=False)
    print("Saved cleaned file:", out)

if __name__ == "__main__":
    main()
