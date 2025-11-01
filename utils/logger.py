from datetime import datetime
import os

def log_run(input_file, output_file):
    """
    Log a pipeline run to logs/run_history.log
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "run_history.log")
    
    with open(log_file, "a") as f:
        f.write(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Input: {input_file} -> Output: {output_file}\n"
        )
