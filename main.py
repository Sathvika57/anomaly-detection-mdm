 
import pandas as pd
from src.preprocessing import preprocess_logs
from src.model import train_model, detect_anomalies

def main():
    # Load data
    df = pd.read_csv("data/processed/mdm_logs.csv")

    # Preprocess
    clean_data = preprocess_logs(df)

    # Train model
    model = train_model(clean_data)

    # Detect anomalies
    anomalies = detect_anomalies(model, clean_data)

    print("Detected Anomalies:")
    print(anomalies.head())

if __name__ == "__main__":
    main()
