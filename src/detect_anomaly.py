# src/detect_anomaly.py
"""
Load latest feature file, run chosen anomaly model, save anomalies to data/data_anomalies.
Supports: isoforest, oneclass, dbscan, autoencoder (optional)
"""
import argparse, os
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from src.logger import log_run

FEAT_DIR = "data/data_features"
ANOM_DIR = "data/data_anomalies"
os.makedirs(ANOM_DIR, exist_ok=True)

def latest_feature():
    files = sorted([f for f in os.listdir(FEAT_DIR) if f.endswith(".csv")])
    if not files:
        return None
    return os.path.join(FEAT_DIR, files[-1])

def run_isoforest(X, contamination):
    clf = IsolationForest(n_estimators=200, contamination=contamination, random_state=42)
    preds = clf.fit_predict(X)
    scores = clf.decision_function(X)
    return preds, scores

def run_oneclass(X, nu=0.05):
    clf = OneClassSVM(gamma='scale', nu=nu)
    preds = clf.fit_predict(X)
    try:
        scores = clf.score_samples(X)
    except Exception:
        scores = np.zeros(len(preds))
    return preds, scores

def run_dbscan(X):
    clf = DBSCAN(eps=0.5, min_samples=5)
    labels = clf.fit_predict(X)
    preds = np.where(labels==-1, -1, 1)
    scores = np.zeros(len(preds))
    return preds, scores

def run_autoencoder(X):
    # optional: requires tensorflow installed
    try:
        from tensorflow.keras import layers, models
    except Exception as e:
        raise RuntimeError("Autoencoder requires tensorflow. Install or choose another model.")
    input_dim = X.shape[1]
    model = models.Sequential([
        layers.InputLayer(input_shape=(input_dim,)),
        layers.Dense(max(4, input_dim//2), activation="relu"),
        layers.Dense(max(2, input_dim//4), activation="relu"),
        layers.Dense(max(4, input_dim//2), activation="relu"),
        layers.Dense(input_dim, activation="linear")
    ])
    model.compile(optimizer="adam", loss="mse")
    model.fit(X, X, epochs=20, batch_size=32, verbose=0)
    recon = model.predict(X)
    mse = np.mean(np.square(X - recon), axis=1)
    # choose threshold as e.g. mean + 3*std
    thresh = mse.mean() + 3*mse.std()
    preds = np.where(mse > thresh, -1, 1)
    scores = -mse  # more negative -> larger recon error
    return preds, scores

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="isoforest", choices=["isoforest","oneclass","dbscan","autoencoder"])
    parser.add_argument("--contamination", type=float, default=0.05)
    args = parser.parse_args()

    feat = latest_feature()
    if not feat:
        print("No feature file found. Run features.py first.")
        raise SystemExit(1)
    print("Using feature file:", feat)
    df = pd.read_csv(feat, parse_dates=["window_start"])
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        print("No numeric columns for modeling.")
        raise SystemExit(1)
    X = df[numeric_cols].fillna(0).values
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    if args.model == "isoforest":
        preds, scores = run_isoforest(Xs, args.contamination)
    elif args.model == "oneclass":
        preds, scores = run_oneclass(Xs, nu=args.contamination)
    elif args.model == "dbscan":
        preds, scores = run_dbscan(Xs)
    elif args.model == "autoencoder":
        preds, scores = run_autoencoder(Xs)
    else:
        print("Unknown model")
        raise SystemExit(1)

    df["anomaly_score_raw"] = scores
    df["anomaly_label"] = preds
    df["is_anomaly"] = df["anomaly_label"] == -1
    df["run_time"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(ANOM_DIR, f"anomalies_{ts}.csv")
    df.to_csv(out, index=False)
    print("Saved anomalies:", out)

    # log run
    log_run(input_file=feat, output_file=out, model=args.model, extra=f"cont={args.contamination}")

if __name__ == "__main__":
    main()
