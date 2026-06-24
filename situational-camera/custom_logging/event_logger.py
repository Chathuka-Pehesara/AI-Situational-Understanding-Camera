import os
import csv

_last_situation = None  # To store last logged situation

def log_event(event: dict):

    global _last_situation

    situation = event.get("situation")

    # step 1: Track last logged situation and only write if it chnages
    if situation == _last_situation:
        return
    
    _last_situation = situation

    # step 2: Ensure exits the data entry
    filepath = os.path.join("data", "events_log.csv")
    os.makedirs(os.path.dirname(filepath), exist_ok = True)
    
    # define headers for exact request order
    headers = ["timestamp", "situation", "objects", "risk", "score"]
    file_exists = os.path.exists(filepath) and os.path.getsize(filepath) > 0

    # step 3: Appened row to events_log.csv
    with open(filepath, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)

        # if the file is new or empty (write headers)
        if not file_exists:
            writer.writeheader()

        # Extract only the specified fields for the row
        writer.writerow({
            "timestamp": event.get("timestamp"),
            "objects": event.get("objects"),
            "situation": situation,
            "risk": event.get("risk"),
            "score": event.get("score")
        })


def reset_logger():

    global _last_situation
    _last_situation = None


