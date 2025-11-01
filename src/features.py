# src/features.py
"""
Build features from cleaned CSVs and save features_{timestamp}.csv into data/data_features.
Aggregates logs by device and time window (default 1h).
"""
import argparse, os
import pandas as pd
import numpy as np
from datetime import datetime

CLEAN_DIR = "data/data_clean"
FEAT_DIR = "data/data_features"
os.makedirs(FEAT_DIR, exist_ok=True)

def map_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

def build_features(df: pd.DataFrame, window="1h"):
    ts_col = map_col(df, ["timestamp"])
    device_col = map_col(df, ["device_id", "device"])
    msg_col = map_col(df, ["message", "msg"])
    event_col = map_col(df, ["event_type", "event"])
    app_col = map_col(df, ["app_id", "app"])

    if ts_col is None or device_col is None:
        raise ValueError("timestamp and device_id required in cleaned CSV")

    df = df.copy()
    df[ts_col] = pd.to_datetime(df[ts_col], utc=True)
    df = df.sort_values(ts_col)

    # create binary flags
    df["is_error"] = df.get("status","").astype(str).str.startswith(("4","5"), na=False)
    if msg_col:
        df["failed_login"] = df[msg_col].str.contains("failed login|auth fail|passcode", case=False, na=False)
        df["jailbreak"] = df[msg_col].str.contains("jailbreak|root", case=False, na=False)
        df["blocked_app"] = df[msg_col].str.contains("blocked app|blacklist|blocked install", case=False, na=False)
        df["profile_fail"] = df[msg_col].str.contains("profile.*fail|install.*fail", case=False, na=False)
    else:
        df["failed_login"] = False
        df["jailbreak"] = False
        df["blocked_app"] = False
        df["profile_fail"] = False

    # resample per device
    df = df.set_index(ts_col)
    groups = []
    devices = df[device_col].unique()
    for dev in devices:
        dev_df = df[df[device_col] == dev]
        if dev_df.empty:
            continue
        res = dev_df.resample(window).agg({
            device_col: lambda s: s.mode()[0] if len(s)>0 else dev,
            ts_col: "count",
            "is_error": "sum",
            "failed_login": "sum",
            "profile_fail":"sum",
            "jailbreak":"sum",
            "blocked_app":"sum"
        })
        res = res.rename(columns={ts_col:"events"}).reset_index().rename(columns={"index":"window_start"})
        res["device_id"] = dev
        groups.append(res)
    if not groups:
        return pd.DataFrame()
    out = pd.concat(groups, ignore_index=True)
    out["error_rate"] = np.where(out["events"]>0, out["is_error"]/out["events"], 0)
    out["fail_ratio"] = np.where(out["events"]>0, out["failed_login"]/out["events"], 0)
    # rename columns to compact names
    out = out[["device_id","window_start","events","is_error","failed_login","profile_fail","jailbreak","blocked_app","error_rate","fail_ratio"]]
    return out

def select_latest_clean(date_substr="", time_substr=""):
    files = sorted([f for f in os.listdir(CLEAN_DIR) if f.endswith(".csv")])
    if not files:
        raise FileNotFoundError("No cleaned CSV found. Run parse_normalize.py first.")
    if date_substr:
        for f in reversed(files):
            if date_substr in f and (not time_substr or time_substr in f):
                return os.path.join(CLEAN_DIR, f)
        raise FileNotFoundError("No cleaned file matching date/time")
    return os.path.join(CLEAN_DIR, files[-1])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="", help="date substring")
    parser.add_argument("--time", default="", help="time substring")
    parser.add_argument("--window", default="1h", help="resample window e.g. 1h")
    args = parser.parse_args()

    try:
        src = select_latest_clean(args.date, args.time)
    except Exception as e:
        print("ERROR selecting cleaned file:", e)
        raise SystemExit(1)
    print("Building features from:", src)
    df = pd.read_csv(src, parse_dates=["timestamp"], low_memory=False)
    feats = build_features(df, window=args.window)
    if feats.empty:
        print("No features generated.")
        raise SystemExit(1)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(FEAT_DIR, f"features_{ts}.csv")
    feats.to_csv(out, index=False)
    print("Saved features:", out)

if __name__ == "__main__":
    main()
