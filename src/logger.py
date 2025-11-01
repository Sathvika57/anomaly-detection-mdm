# src/logger.py
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "run_history.log")

def log_run(input_file: str, output_file: str, model: str, extra: str = ""):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] IN:{input_file} OUT:{output_file} MODEL:{model} {extra}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
