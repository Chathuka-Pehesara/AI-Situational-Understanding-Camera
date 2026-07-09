from fastapi import APIRouter
from api.services.alert_manager import alert_manager

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("")
def get_active_alerts(severity: str = None, limit: int = 50):
    """
    Returns a list of active alerts, optionally filtered by severity (Low, Medium, High).
    """
    return alert_manager.get_alerts(limit=limit, filter_severity=severity)

@router.post("/clear")
def clear_active_alerts():
    """
    Clears all currently active alerts.
    """
    return alert_manager.clear_alerts()
