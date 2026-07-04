
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
    "Normal Activity": "Person is performing normal daily activity.",
    "Trespassing": "Person has trespassed into a highly restricted zone.",
    "Perimeter Breach": "Person has breached the perimeter line.",
    "Loitering": "Person is loitering in a restricted zone for a prolonged period.",
    "Weapon Detected": "Critical Alert: A person carrying a weapon (knife) has been detected.",
    "Vehicle Loitering": "A vehicle (bicycle/motorcycle) has been detected parked or moving in the area.",
    "Animal Intrusion": "An animal (dog/cat) has breached the perimeter of the monitored area."
}


def encode_frame(frame):
    """
    Convert an OpenCV frame to a Base64-encoded JPEG string.
    """
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")


def get_explanation(situation, frame=None, detections=None, risk=None):
    """
    Returns a human-readable explanation for the detected situation.
    Uses Gemini Flash API for live generation, falls back to templates when unavailable.

    Parameters:
        situation (str): Detected situation name.
        frame (numpy array, optional): OpenCV frame for visual analysis.
        detections (list, optional): List of detected objects.
        risk (str, optional): Risk level.

    Returns:
        str: Explanation sentence.
    """
    # Try Gemini API if available and frame is provided
    if model and frame is not None:
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
            # Fall through to template fallback
            pass
    
    # Fallback to templates
    return EXPLANATION_TEMPLATES.get(
        situation,
        "No explanation available."
    )


if __name__ == "__main__":
    situations = [
        "Distracted Walking",
        "Working",
        "Resting",
        "Hurrying",
        "Normal Activity",
        "Trespassing",
        "Perimeter Breach",
        "Loitering"
    ]

    for situation in situations:
        print(f"{situation}: {get_explanation(situation)}")