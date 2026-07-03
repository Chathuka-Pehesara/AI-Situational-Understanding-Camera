import os
import base64
import cv2
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GOOGLE_API_KEY")

# Configure Gemini if API key is available
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None

# Fallback templates (offline mode)
EXPLANATION_TEMPLATES = {
    "Distracted Walking": "Person is walking while using a phone.",
    "Working": "Person is working on a laptop.",
    "Resting": "Person is stationary and appears to be resting.",
    "Hurrying": "Person is moving quickly with belongings.",
    "Normal Activity": "Person is performing normal daily activity."
}


def encode_frame(frame):
    """
    Convert an OpenCV frame to a Base64-encoded JPEG string.
    """
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")


def generate_explanation(frame, detections, situation, risk):
    """
    Uses Gemini Vision to generate a natural language explanation.

    Args:
        frame: OpenCV frame (numpy array)
        detections: List of detected objects.
        situation: Situation detected by the rule engine.
        risk: Risk level.

    Returns:
        str: Generated explanation.
    """
    # Try Gemini API if available
    if model:
        try:
            image_base64 = encode_frame(frame)

            detection_text = (
                ", ".join(d["label"] for d in detections)
                if detections
                else "No objects detected"
            )

            prompt = f"""
You are an AI surveillance assistant.

Analyze the scene and generate a short explanation.

Context:
- Situation: {situation}
- Risk Level: {risk}
- Detected Objects: {detection_text}

Rules:
- Keep the explanation under 2 sentences.
- Be natural and human-readable.
- Describe what the person is doing.
"""


            response = model.generate_content(
                [
                    prompt,
                    {
                        "mime_type": "image/jpeg",
                        "data": image_base64,
                    },
                ]
            )

            return response.text

        except Exception as e:
            # Fallback: construct a concise, human-readable explanation when
            # the Gemini model or the requested API method is unavailable
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

                    explanation_text = f"A person {action}. Objects: {det_summary}. Risk: {risk}."
                else:
                    explanation_text = f"Detected: {det_summary}. Situation: {situation}. Risk: {risk}."

                return f"(fallback) {explanation_text} -- Gemini Error: {e}"
            except Exception:
                return f"Gemini API Error: {e}"
    
    # Offline fallback when no API key
    return EXPLANATION_TEMPLATES.get(situation, "No explanation available.")

    try:
        response = model.generate_content(
            [
                prompt,
                {
                    "mime_type": "image/jpeg",
                    "data": image_base64,
                },
            ]
        )

        return response.text

    except Exception as e:
        # Fallback: construct a concise, human-readable explanation when
        # the Gemini model or the requested API method is unavailable
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

                explanation_text = f"A person {action}. Objects: {det_summary}. Risk: {risk}."
            else:
                explanation_text = f"Detected: {det_summary}. Situation: {situation}. Risk: {risk}."

            return f"(fallback) {explanation_text} -- Gemini Error: {e}"
        except Exception:
            return f"Gemini API Error: {e}"

