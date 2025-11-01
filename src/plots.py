import os
import pandas as pd
import matplotlib.pyplot as plt

def generate_combined_plots():
    reports_dir = "data/reports"
    features_file = os.path.join("data", "data_features", "features_anomaly.csv")

    if not os.path.exists(features_file):
        print("No features file found. Skipping plots.")
        return

    df = pd.read_csv(features_file)
    metrics = ["error_rate", "fail_ratio", "jailbreak_hits", "blocked_app_hits"]

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()

    for idx, col in enumerate(metrics):
        ax = axes[idx]
        if col not in df.columns:
            print(f"Skipping {col}, not found in features file.")
            continue
        for device in df["device_id"].unique():
            device_data = df[df["device_id"] == device]
            ax.plot(device_data.index, device_data[col], label=device, alpha=0.6)
        ax.set_title(col.replace("_", " ").title())
        ax.set_xlabel("Record Index")
        ax.set_ylabel(col)
        ax.legend(fontsize=6, loc="upper right")

    plt.tight_layout()
    combined_path = os.path.join(reports_dir, "all_metrics_combined.png")
    plt.savefig(combined_path)
    plt.close()
    print(f"Combined plot saved to {combined_path}")

if __name__ == "__main__":
    generate_combined_plots()
