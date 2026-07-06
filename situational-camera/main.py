import cv2
import datetime
import sys

from detection.detector import detect_objects
from detection.tracker import is_moving, track_and_analyze_zones

from reasoning.rule_engine import evaluate_situation
from reasoning.explainer import generate_explanation
from reasoning.scorer import compute_scores

from custom_logging.event_logger import log_event
from ui.opencv_view import render_overlay

DEFAULT_ZONES = {
    "Restricted Zone A": [
        [30, 80],
        [250, 80],
        [220, 400],
        [10, 400]
    ],
    "Perimeter Gate": [
        [380, 120],
        [600, 120],
        [620, 450],
        [400, 450]
    ]
}


def main():
    """
    Main entry point for the AI Situational Understanding Camera pipeline.
    """

    print("Initializing camera feed...")

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Error: Could not open webcam.")
        sys.exit(1)

    print("Camera feed active. Press 'q' to quit.")

    last_situation = None

    try:
        while True:

            # Read frame
            ret, frame = camera.read()

            if not ret or frame is None:
                print("Error: Failed to capture frame.")
                break

            # Object detection
            detections = detect_objects(frame)

            # Spatial tracking and restricted zone monitoring
            detections = track_and_analyze_zones(detections, DEFAULT_ZONES, loitering_threshold=5.0)

            # Movement detection based on unique track IDs
            movement_detected = False

            for detection in detections:

                if (
                    detection.get("label") == "person"
                    and "bbox" in detection
                    and "track_id" in detection
                ):
                    if is_moving(detection["track_id"], detection["bbox"]):
                        movement_detected = True
                        break

            # Rule engine (with frame for Gemini verification)
            situation_data = evaluate_situation(
                detections,
                movement_detected,
                frame
            )

            situation = situation_data["situation"]
            risk = situation_data["risk"]
            gemini_confidence = situation_data.get("confidence", None)

            # Gemini explanation
            explanation = generate_explanation(
                frame,
                detections,
                situation,
                risk
            )

            # Scores (with Gemini confidence)
            scores = compute_scores(
                situation,
                risk,
                detections,
                gemini_confidence
            )

            # Log only when situation changes
            if situation != last_situation:

                event = {
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "situation": situation,
                    "risk": risk,
                    "explanation": explanation,
                    "focus_score": scores["focus_score"],
                    "safety_score": scores["safety_score"],
                    "gemini_confidence": scores.get("gemini_confidence", None),
                    "gemini_verified": situation_data.get("gemini_verified", False)
                }

                log_event(event)

                last_situation = situation

                print(
                    f"[{event['timestamp']}] "
                    f"{situation} | "
                    f"Risk: {risk} | "
                    f"Focus: {scores['focus_score']} | "
                    f"Safety: {scores['safety_score']} | "
                    f"Gemini Confidence: {gemini_confidence if gemini_confidence else 'N/A'}"
                )

            # Draw overlays
            output_frame = render_overlay(
                frame,
                detections,
                situation,
                risk,
                zones=DEFAULT_ZONES
            )

            if output_frame is not None:
                cv2.imshow(
                    "AI Situational Camera Feed",
                    output_frame
                )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q") or key == 27:
                break

    except KeyboardInterrupt:
        print("\nPipeline interrupted by user.")

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("Camera released. Pipeline shut down cleanly.")


if __name__ == "__main__":
    main()
