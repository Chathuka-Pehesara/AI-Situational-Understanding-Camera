import os
import cv2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fallback templates (offline mode)
EXPLANATION_TEMPLATES = {
    "Distracted Walking": "Person is walking while using a phone.",
    "Working": "Person is working on a laptop.",
    "Resting": "Person is stationary and appears to be resting.",
    "Hurrying": "Person is moving quickly with belongings.",
    "Normal Activity": "Person is performing normal daily activity.",
    "Fall Detected": "Person has likely fallen down.",
    "Exam in Progress": "Student is actively taking the exam and facing the screen.",
    "Multiple People Detected": "More than one person detected in the frame. Potential cheating.",
    "Unauthorized Device": "An unauthorized device (e.g. phone) has been detected.",
    "Looking Away (Left)": "Student's head is turned away from the screen to the left.",
    "Looking Away (Right)": "Student's head is turned away from the screen to the right.",
    "Looking Away (Out of Bounds)": "Student's head has moved out of bounds or they are looking away.",
    "Suspicious Movement (Left)": "Student has leaned suspiciously to the left.",
    "Suspicious Movement (Right)": "Student has leaned suspiciously to the right.",
    "Prolonged Suspicious Movement": "Student has been making suspicious movements for a prolonged period."
}


def generate_explanation(frame, detections, situation, risk):
    """
    Generates a natural language explanation.

    Args:
        frame: OpenCV frame (numpy array)
        detections: List of detected objects.
        situation: Situation detected by the rule engine.
        risk: Risk level.

    Returns:
        str: Generated explanation.
    """
    try:
        labels = [d.get("label", "object") for d in detections] if detections else []
        det_summary = ", ".join(labels) if labels else "no notable objects"

        # Prefer short, natural sentences (<=2 sentences)
        if labels and "person" in labels:
            # Tailor message for person-centric scenes
            action = "appears to be moving normally"
            s_low = (situation or "").lower()
            if "distract" in s_low:
                action = "appears distracted, possibly using a phone"
            elif "hurr" in s_low:
                action = "is moving quickly and may be hurrying"
            elif "rest" in s_low:
                action = "appears stationary and resting"
            elif "work" in s_low:
                action = "appears engaged with a device or workstation"
            elif "trespass" in s_low:
                action = "has entered a highly restricted zone without authorization"
            elif "breach" in s_low:
                action = "has crossed the perimeter line"
            elif "loiter" in s_low:
                action = "has been loitering inside a restricted zone for a prolonged period"
            elif "fall" in s_low:
                action = "appears to have fallen down"
            elif "webcam" in s_low:
                action = "is sitting comfortably at the computer"
            elif "unsafe" in s_low:
                action = "has entered an unsafe zone"

            explanation_text = f"A person {action}. Objects: {det_summary}. Risk: {risk}."
        else:
            explanation_text = f"Detected: {det_summary}. Situation: {situation}. Risk: {risk}."

        return explanation_text
    except Exception:
        # Offline fallback
        return EXPLANATION_TEMPLATES.get(situation, "No explanation available.")
