# src/policy_filters.py
import pandas as pd

MAINT_HOURS_UTC = set([1,2,3])  # example hours to ignore to reduce false positives

def prefilter(df: pd.DataFrame) -> pd.DataFrame:
    """Exclude maintenance hours if window_start present."""
    if "window_start" in df.columns:
        hrs = pd.to_datetime(df["window_start"]).dt.hour
        return df[~hrs.isin(MAINT_HOURS_UTC)]
    return df

def postfilter_alerts(alerts: pd.DataFrame, top_k: int = 100) -> pd.DataFrame:
    """Keep alerts with meaningful reasons or extreme scores."""
    a = alerts.copy()
    if a.empty:
        return a
    # prefer columns indicating reasons
    reason_cols = [c for c in ["failed_login","profile_fail","jailbreak","blocked_app","is_error"] if c in a.columns]
    if reason_cols:
        mask = (a[reason_cols].fillna(0).sum(axis=1) > 0) | (a.get("anomaly_score_raw", 0) < -0.05)
    else:
        mask = a.get("anomaly_score_raw", 0) < -0.05
    a = a[mask]
    if "anomaly_score_raw" in a.columns:
        a = a.sort_values("anomaly_score_raw").head(top_k)
    else:
        a = a.head(top_k)
    return a
