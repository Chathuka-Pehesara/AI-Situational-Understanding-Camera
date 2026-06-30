import os
import sys
import csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from custom_logging.event_logger import log_event, reset_logger

def run_logger_test():
    print("Logger event testing...")

    # Clean up old test runs
    log_file = os.path.join("data", "events_log.csv")
    if os.path.exists(log_file):
        os.remove(log_file)

    reset_logger()

    # Log first event
    event1 = {
        "timestamp": "2026-01-01 00:00:01",
        "objects": "person, cellphone",
        "situation": "Texting while walking",
        "risk": "Medium",
        "score": 4
    }
    log_event(event1)

    # Log identical situation
    event2 = {
        "timestamp": "2026-05-23 13:30:01",
        "objects": "person",
        "situation": "Texting while walking",
        "risk": "Low",
        "score": 2
    }
    log_event(event2)

    # Log a different situation
    event3 = {
        "timestamp": "2026-05-23 13:30:05",
        "objects": "person, cellphone, ",
        "situation": "Safe walking",
        "risk": "Medium",
        "score": 4
    }

    log_event(event3)

    # verify the results in CSV
    assert os.path.exists(log_file), "Log file was not created"

    with open(log_file, mode="r", newline="", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    print(f"Logged rows count: {len(reader)}")

    assert len(reader)  == 2, "Duplicate situation was not filtered out correctly"
    assert reader[0]["situation"] == "Texting while walking"
    assert reader[1]["situation"] == "Safe walking"

    print("Sucesss: Event Logger tests passed!")

if __name__ == "__main__":
    run_logger_test()
