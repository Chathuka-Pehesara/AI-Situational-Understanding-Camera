import os
import csv

def log_event(event: dict):
    """
    Logs situational changes or events to a CSV file.

    Parameters:
        event (dict): Event details to log (e.g. timestamp, situation, risk, score).

    Appends details to 'data/events_log.csv'.
    """
    CSV_FILE = "data/events_log.csv"
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)
    
    fieldnames = ["timestamp", "situation", "risk", "explanation", "focus_score", "safety_score"]
    file_exists = os.path.exists(CSV_FILE)
    
    try:
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "timestamp": event.get("timestamp", ""),
                "situation": event.get("situation", ""),
                "risk": event.get("risk", ""),
                "explanation": event.get("explanation", ""),
                "focus_score": event.get("focus_score", 100),
                "safety_score": event.get("safety_score", 10)
            })
    except Exception as e:
        print(f"Error logging event to CSV: {e}")

