# Import all modules to establish project structure and verification
import cv2
import datetime
import sys
from detection.detector import detect_objects
from detection.tracker import is_moving
from reasoning.rule_engine import evaluate_situation
from reasoning.explainer import generate_explanation
from reasoning.scorer import compute_scores
from custom_logging.event_logger import log_event
from ui.opencv_view import render_overlay

def main():
    """
    Main entry point for the AI Situational Understanding Camera pipeline.
    
    This function initializes the physical camera feed and executes the
    real-time situational monitoring pipeline on each frame.
    """
    print("Initializing camera feed...")
    # Open the default system camera (webcam index 0)
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("Error: Could not open video source (webcam). Please check camera connection.")
        sys.exit(1)
        
    print("Camera feed active. Press 'q' in the window to quit.")
    
    last_situation = None
    
    try:
        while True:
            # Step 1: Capture frame from camera
            ret, frame = camera.read()
            if not ret or frame is None:
                print("Error: Failed to read frame from camera.")
                break
                
            # Step 2: Run object detection (YOLOv8 Small)
            detections = detect_objects(frame)
            
            # Step 3: Track movement (compare bbox centers across frames)
            movement_detected = False
            for detection in detections:
                if detection["label"] == "person":
                    # Pass a placeholder person track ID (0) to tracker
                    if is_moving(0, detection["bbox"]):
                        movement_detected = True
            
            # Step 4: Evaluate situation based on rules
            situation_data = evaluate_situation(detections, movement_detected)
            situation = situation_data["situation"]
            risk = situation_data["risk"]
            
            # Step 5: Generate explanation text
            explanation = generate_explanation(situation)
            
            # Step 6: Compute focus and safety scores
            scores = compute_scores(situation, risk, detections)
            
            # Step 7: Log events if situation changes
            if situation != last_situation:
                event = {
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "situation": situation,
                    "risk": risk,
                    "explanation": explanation,
                    "focus_score": scores["focus_score"],
                    "safety_score": scores["safety_score"]
                }
                log_event(event)
                last_situation = situation
                print(f"[{event['timestamp']}] Event logged: {situation} (Risk: {risk}, Focus: {scores['focus_score']}, Safety: {scores['safety_score']})")
            
            # Step 8: Render output overlays
            output_frame = render_overlay(frame, detections, situation, risk)
            
            # Step 9: Display or stream the processed frame
            if output_frame is not None:
                cv2.imshow("AI Situational Camera Feed", output_frame)
            
            # Check for termination key (press 'q' or 'ESC' to exit)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
                
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user.")
    finally:
        # Clean up camera and close windows
        camera.release()
        cv2.destroyAllWindows()
        print("Camera released. Pipeline shut down cleanly.")

if __name__ == "__main__":
    main()

