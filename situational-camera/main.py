from doctest import REPORT_NDIFF
import cv2
import sys
import argparse
from datetime import datetime
from detection.detector import detect_objects
from detection.tracker import is_moving, reset_tracker
from reasoning.rule_engine import evaluate_situation
from reasoning.explainer import generate_explanation
from reasoning.scorer import compute_scores
from ui.opencv_view import render_overlay
from custom_logging.event_logger import log_event
def main():

    # TODO: Initialize camera feed / video capture
    parser = argparse.ArugumentParser(description="AI Situational Understanding Camera Pipeline")
    parser.add_argument(
        "--source",
        type = str,
        default = "0",
        help = "Webcam index (e.g. 0) or path to a local video file (e.g. path/to/video.mp4)"   
    )
    args = parser.parse_args()

    # Determine input source
    source = args.source
    if source.isdigit():
        source = int(source)

    # Initialize video capture
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"Error: Could not open video source '{source}'")
        sys.exit(1)
    print(f"\n===========================================================")
    print(f"Pipeline started successfully on source: {source}")
    print(f"Press 'q' inside the video window to quit.")
    print(f"============================================================\n")

    reset_tracker()

    try: 
        while True:
            # Step 1: Capture frame
            ret, frame = cap.read()
            if not ret:
                print("End of video stream or failed to grab frame. Exiting...")
                break

            # Step 2: Run object detection (YOLOv8 wrapper)
            detections = detect_objects(frame)
     
            # Step 3: Track movement (compare bbox centers across frames)
            movement_detected = False
            for detection in detections:
                if detection["label"] == "person":
                    track_id = detection.get("track_id")

                    person_id = track_id if track_id is not None else 0

                    if is_moving(person_id, detection["bbox"]):
                        movement_detected = True
              
            # Step 4: Evaluate situation based on rules
            situation_data = evaluate_situation(detections, movement_detected)
            situation = situation_data.get("situation", "Normal Activity")
            risk = situation_data.get("risk", "Low")

            # Step 5: Generate explanation text
            explanation = generate_explanation(situation)

            # Step 6: Compute focus and safety scores
            scores = compute_scores(situation, risk, detections)
            
            # --- MOCK DATA FOR TESTING THE FLOW ---
            frame = None
            detections = [{"label": "person", "bbox": [100, 100, 200, 200]}, {"label": "cell phone", "bbox": [120, 120, 150, 150]}]
            movement_detected = True
            
            situation = "Walking while texting"
            risk = "Medium"
            explanation = "Person is moving while holding a mobile phone."
            scores = {
                "focus_score": 30,
                "safety_score": 5
            }
             # --------------------------------------
    
            # Step 7: Log events if situation changes
            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            objects_str = ", ".join([d["label"] for d in detections])
            score_logged = scores.get("safety_score")
            log_event({
                "timestamp": timestamp_str,
                "situation": situation,
                "objects": objects_str,
                "risk": risk,
                "explanation":explanation,
                "focus_score": scores.get("focus_score", 100),
                "safety_score": scores.get("safety_score", 10),
                "score": scores.get("safety_score", 10)  # Key fallback for backward compatibility
            })
            
            # Step 8: Render output overlays
            output_frame = render_overlay(frame, detections, situation, risk)
            if output_frame is None:
                output_frame =  frame

            # Step 9: Display or stream the processed frame
            cv2.imshow("AI Situational Camera Feed", output_frame)
            
            # Break loop if 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # CLean up response
        cap.release()
        cv2.destroyALlWindow()
        print("Pipeline shut down. Resources released cleanly.")

if __name__ == "__main__":
    main()
