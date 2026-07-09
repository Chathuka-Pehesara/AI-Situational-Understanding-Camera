import datetime
import uuid

class AlertManager:
    def __init__(self):
        # In-memory list of alerts
        # Each alert dict: { id, camera_id, camera_name, situation, risk, explanation, timestamp, safety_score, focus_score, status }
        self._alerts = []

    def get_alerts(self, limit: int = 50, filter_severity: str = None):
        """
        Retrieves the latest alerts, optionally filtered by severity.
        """
        # Filter active alerts first, sorted by newest
        filtered = [a for a in self._alerts if a["status"] == "active"]
        
        if filter_severity:
            filter_severity = filter_severity.upper()
            filtered = [a for a in filtered if a["risk"].upper() == filter_severity]
            
        filtered.sort(key=lambda x: x["timestamp"], reverse=True)
        return filtered[:limit]

    def add_alert(self, camera_id: str, camera_name: str, situation: str, risk: str, explanation: str, safety_score: int, focus_score: int):
        """
        Adds a new alert to the manager if it is a relevant warning situation (risk is Medium or High, or specific alert).
        Returns the alert dict if added, else None.
        """
        # Only alert for non-Normal/Resting/Working or if risk is Medium/High
        if situation in ["Normal Activity", "Resting", "Working"] and risk == "Low":
            return None

        # Check if we already have an active alert for the same situation and camera in the last 10 seconds to avoid spam
        now = datetime.datetime.now()
        for alert in self._alerts:
            if (
                alert["status"] == "active"
                and alert["camera_id"] == camera_id
                and alert["situation"] == situation
            ):
                alert_time = datetime.datetime.fromisoformat(alert["timestamp"])
                if (now - alert_time).total_seconds() < 10:
                    # Update explanation and scores rather than adding new card
                    alert["explanation"] = explanation
                    alert["safety_score"] = safety_score
                    alert["focus_score"] = focus_score
                    alert["timestamp"] = now.isoformat()
                    return alert

        alert_id = str(uuid.uuid4())
        alert = {
            "id": alert_id,
            "camera_id": camera_id,
            "camera_name": camera_name,
            "situation": situation,
            "risk": risk,          # Low, Medium, High
            "explanation": explanation,
            "timestamp": now.isoformat(),
            "safety_score": safety_score,
            "focus_score": focus_score,
            "status": "active"
        }
        self._alerts.append(alert)
        return alert

    def clear_alerts(self):
        """
        Marks all active alerts as cleared.
        """
        for alert in self._alerts:
            if alert["status"] == "active":
                alert["status"] = "cleared"
        return {"message": "All alerts cleared successfully"}

# Global alert manager instance
alert_manager = AlertManager()
