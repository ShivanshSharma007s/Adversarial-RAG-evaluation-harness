import os
import json

REGRESSION_FILE = "report/regression_history.json"

def track_regression(current_accuracy: float, run_id: str):
    """
    Saves the current run metrics and compares with the previous run.
    """
    history = []
    if os.path.exists(REGRESSION_FILE):
        with open(REGRESSION_FILE, "r") as f:
            history = json.load(f)
            
    regression_detected = False
    if history:
        last_run = history[-1]
        if current_accuracy < last_run["accuracy"]:
            regression_detected = True
            
    history.append({
        "run_id": run_id,
        "accuracy": current_accuracy
    })
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(REGRESSION_FILE), exist_ok=True)
    with open(REGRESSION_FILE, "w") as f:
        json.dump(history, f, indent=4)
        
    return regression_detected
