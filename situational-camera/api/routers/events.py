from fastapi import APIRouter, Query
import os
import csv
import datetime

router = APIRouter(prefix="/api/events", tags=["events"])
CSV_FILE = "data/events_log.csv"

def load_all_events():
    if not os.path.exists(CSV_FILE):
        return []
    
    events = []
    try:
        with open(CSV_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                events.append({
                    "timestamp": row.get("timestamp", ""),
                    "situation": row.get("situation", ""),
                    "risk": row.get("risk", "Low"),
                    "explanation": row.get("explanation", ""),
                    "focus_score": int(row.get("focus_score")) if row.get("focus_score") else 100,
                    "safety_score": int(row.get("safety_score")) if row.get("safety_score") else 10,
                    "gemini_confidence": float(row.get("gemini_confidence")) if row.get("gemini_confidence") else None,
                    "gemini_verified": row.get("gemini_verified", "False") == "True"
                })
    except Exception as e:
        print(f"Error reading CSV logs: {e}")
        
    # Sort by timestamp descending (newest first)
    events.sort(key=lambda x: x["timestamp"], reverse=True)
    return events

@router.get("")
def list_events(page: int = 1, limit: int = 25):
    """
    Returns a list of paginated incidents from CSV logs.
    """
    events = load_all_events()
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    return {
        "page": page,
        "limit": limit,
        "total_count": len(events),
        "events": events[start_idx:end_idx]
    }

@router.get("/search")
def search_events(
    q: str = None,
    severity: str = None, # Low, Medium, High
    date_from: str = None, # YYYY-MM-DD
    date_to: str = None,   # YYYY-MM-DD
    page: int = 1,
    limit: int = 25
):
    """
    Search and filter incidents from the CSV logs.
    """
    events = load_all_events()
    filtered = events

    # Apply search keyword
    if q:
        q_lower = q.lower()
        filtered = [
            e for e in filtered
            if q_lower in e["situation"].lower() or q_lower in e["explanation"].lower()
        ]

    # Apply severity filter
    if severity:
        sev_lower = severity.lower()
        filtered = [e for e in filtered if e["risk"].lower() == sev_lower]

    # Apply date filters
    if date_from:
        try:
            from_dt = datetime.datetime.strptime(date_from, "%Y-%m-%d")
            filtered = [
                e for e in filtered
                if datetime.datetime.strptime(e["timestamp"][:10], "%Y-%m-%d") >= from_dt
            ]
        except ValueError:
            pass

    if date_to:
        try:
            to_dt = datetime.datetime.strptime(date_to, "%Y-%m-%d")
            filtered = [
                e for e in filtered
                if datetime.datetime.strptime(e["timestamp"][:10], "%Y-%m-%d") <= to_dt
            ]
        except ValueError:
            pass

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit

    return {
        "page": page,
        "limit": limit,
        "total_count": len(filtered),
        "events": filtered[start_idx:end_idx]
    }
