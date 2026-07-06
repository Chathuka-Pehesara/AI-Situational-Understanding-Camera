import os
import base64
import cv2
import google.generativeai as genai
from dotenv import load_dotenv
from rules.rule_engine import detect_situation

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GOOGLE_API_KEY")

# Configure Gemini if API key is available
if api_key:
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
else:
    gemini_model = None


def encode_frame(frame):
    """
    Convert an OpenCV frame to a Base64-encoded JPEG string.
    """
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")


def gemini_verify_situation(frame, detections, initial_situation, initial_risk):
    """
    Uses Gemini to verify or override the situation label when rule-based confidence is low.

    Args:
        frame: OpenCV frame (numpy array)
        detections: List of detected objects.
        initial_situation: Initial situation from rule engine.
        initial_risk: Initial risk level from rule engine.

    Returns:
        dict: A dictionary containing:
            {
                "situation": str,
                "risk": str,
                "confidence": float,  # Gemini's confidence in the assessment
                "gemini_verified": bool  # Whether Gemini confirmed or changed the situation
            }
    """
    if not gemini_model:
        return {
            "situation": initial_situation,
            "risk": initial_risk,
            "confidence": 0.5,
            "gemini_verified": False
        }
    
    try:
        image_base64 = encode_frame(frame)
        
        detection_text = (
            ", ".join(d["label"] for d in detections)
            if detections
            else "No objects detected"
        )
        
        prompt = f"""
You are an AI surveillance assistant analyzing a scene.

Context:
- Rule-based Situation: {initial_situation}
- Rule-based Risk Level: {initial_risk}
- Detected Objects: {detection_text}

Analyze the scene and determine:
1. What is the most accurate situation label? (Choose from: Distracted Walking, Working, Resting, Hurrying, Normal Activity)
2. What is the appropriate risk level? (Low, Medium, High)
3. How confident are you in this assessment? (0.0 to 1.0)

Format your response as JSON:
{{
    "situation": "situation_label",
    "risk": "risk_level",
    "confidence": 0.0-1.0
}}
"""
        
        response = gemini_model.generate_content(
            [
                prompt,
                {
                    "mime_type": "image/jpeg",
                    "data": image_base64,
                },
            ]
        )
        
        # Parse the response
        import json
        response_text = response.text.strip()
        
        # Try to extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        
        return {
            "situation": result.get("situation", initial_situation),
            "risk": result.get("risk", initial_risk),
            "confidence": float(result.get("confidence", 0.5)),
            "gemini_verified": True
        }
        
    except Exception as e:
        # Return original values on error
        return {
            "situation": initial_situation,
            "risk": initial_risk,
            "confidence": 0.0,
            "gemini_verified": False,
            "error": str(e)
        }


def evaluate_situation(detections, movement_detected, frame=None, confidence_threshold=0.6) -> dict:
    """
    Evaluates situation rules (e.g., Person + Phone + Movement) to determine 
    the overall situation and risk level.

    Parameters:
        detections (list): List of detected objects with their labels and bounding boxes.
        movement_detected (bool): Whether significant movement is currently detected.
        frame (numpy array, optional): OpenCV frame for Gemini verification.
        confidence_threshold (float): Minimum confidence to trust rule-based result.

    Returns:
        dict: A dictionary containing:
            {
                "situation": str,  # Description of the situation (e.g., "Walking while texting")
                "risk": str,       # Risk level (e.g., "Low", "Medium", "High")
                "confidence": float,  # Confidence score (0.0 to 1.0)
                "gemini_verified": bool  # Whether Gemini was used
            }
    """
    # Get initial rule-based assessment
    rule_result = detect_situation(detections, movement_detected)
    initial_situation = rule_result["situation"]
    initial_risk = rule_result["risk"]
    
    # Calculate rule-based confidence based on detection clarity
    # Higher confidence when clear patterns are detected
    confidence = 0.5  # Base confidence
    
    if detections and isinstance(detections, list):
        labels = [item.get("label") for item in detections if isinstance(item, dict) and "label" in item]
        
        # High confidence for clear patterns
        if "knife" in labels:
            confidence = 0.95  # Weapon detected is high priority and clear
        elif "animal" in labels:
            confidence = 0.8   # Animal detection is clear
        elif "bicycle" in labels or "motorcycle" in labels:
            confidence = 0.85  # Vehicle is clear
        elif "person" in labels and "phone" in labels and movement_detected:
            confidence = 0.9  # Distracted walking is very clear
        elif "person" in labels and "laptop" in labels:
            confidence = 0.85  # Working is clear
        elif "person" in labels and ("bag" in labels or "bottle" in labels) and movement_detected:
            confidence = 0.8  # Hurrying is clear
        elif "person" in labels and not movement_detected:
            confidence = 0.75  # Resting is clear
        elif "person" in labels:
            confidence = 0.7  # Normal activity
    
    # If confidence is below threshold and frame is available, use Gemini for verification
    if confidence < confidence_threshold and frame is not None:
        gemini_result = gemini_verify_situation(frame, detections, initial_situation, initial_risk)
        
        # Use Gemini's assessment if it has higher confidence
        if gemini_result["confidence"] > confidence:
            return {
                "situation": gemini_result["situation"],
                "risk": gemini_result["risk"],
                "confidence": gemini_result["confidence"],
                "gemini_verified": True
            }
    
    return {
        "situation": initial_situation,
        "risk": initial_risk,
        "confidence": confidence,
        "gemini_verified": False
    }
