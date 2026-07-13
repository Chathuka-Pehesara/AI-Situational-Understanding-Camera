import sys
import os
import datetime

# Ensure the parent directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from detection.detector import detect_objects
from detection.tracker import track_and_analyze_zones, is_moving
from reasoning.rule_engine import evaluate_situation
from reasoning.explainer import generate_explanation
from reasoning.scorer import compute_scores
from custom_logging.event_logger import log_event
from api.services.alert_manager import alert_manager

# Default zones for processing
DEFAULT_ZONES = {
    "Suspicious Movement (Left)": [
        [100, 150],
        [200, 150],
        [200, 350],
        [100, 350]
    ],
    "Suspicious Movement (Right)": [
        [440, 150],
        [540, 150],
        [540, 350],
        [440, 350]
    ],
    "Out of Bounds (Looking Away)": [
        [250, 50],
        [390, 50],
        [390, 150],
        [250, 150]
    ]
}

class PipelineService:
    def __init__(self):
        self.last_situations = {} # camera_id -> situation string

    def run_pipeline(self, frame, camera_id: str, camera_name: str) -> dict:
        """
        Runs the full detection, tracking, reasoning and logging pipeline for a single frame.
        """
        if frame is None:
            return {}

        # 1. Object detection
        detections = detect_objects(frame)

        # 2. Tracking and zone mapping
        detections = track_and_analyze_zones(detections, DEFAULT_ZONES, loitering_threshold=5.0)

        # 3. Determine if movement is detected
        movement_detected = False
        for det in detections:
            if (
                det.get("label") == "person"
                and "bbox" in det
                and "track_id" in det
            ):
                if is_moving(det["track_id"], det["bbox"]):
                    movement_detected = True
                    break

        # 4. Evaluate situation (with Gemini verification if rules confidence is low)
        situation_data = evaluate_situation(
            detections,
            movement_detected,
            frame
        )

        situation = situation_data["situation"]
        risk = situation_data["risk"]
        gemini_confidence = situation_data.get("confidence", 0.5)
        gemini_verified = situation_data.get("gemini_verified", False)

        # 5. Generate natural language explanation
        explanation = generate_explanation(
            frame,
            detections,
            situation,
            risk
        )

        # 6. Safety and Focus Scores
        scores = compute_scores(
            situation,
            risk,
            detections,
            gemini_confidence
        )

        focus_score = scores.get("focus_score", 100)
        safety_score = scores.get("safety_score", 10)

        # 7. Log event if situation changes for this camera
        last_situation = self.last_situations.get(camera_id)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if situation != last_situation:
            event = {
                "timestamp": timestamp,
                "camera_id": camera_id,
                "camera_name": camera_name,
                "situation": situation,
                "risk": risk,
                "explanation": explanation,
                "focus_score": focus_score,
                "safety_score": safety_score,
                "gemini_confidence": gemini_confidence,
                "gemini_verified": gemini_verified
            }
            log_event(event)
            self.last_situations[camera_id] = situation

            # 8. Add to active alerts if warning
            alert_manager.add_alert(
                camera_id=camera_id,
                camera_name=camera_name,
                situation=situation,
                risk=risk,
                explanation=explanation,
                safety_score=safety_score,
                focus_score=focus_score
            )

        return {
            "detections": detections,
            "situation": situation,
            "risk": risk,
            "explanation": explanation,
            "focus_score": focus_score,
            "safety_score": safety_score,
            "gemini_confidence": gemini_confidence,
            "gemini_verified": gemini_verified,
            "timestamp": timestamp
        }

# Global pipeline service instance
pipeline_service = PipelineService()
