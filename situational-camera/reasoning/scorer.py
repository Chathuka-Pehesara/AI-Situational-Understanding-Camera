from scoring.scoring import calculate_scores


def compute_scores(situation: str, risk: str, detections=None, gemini_confidence: float = None) -> dict:
    """
    Computes situational metrics, specifically a Focus Score and a Safety Score.
    Incorporates Gemini's confidence response for score adjustment.

    Parameters:
        situation (str): The current situation description.
        risk (str): The current risk level.
        detections (list, optional): List of detected objects.
        gemini_confidence (float, optional): Gemini's confidence in the situation assessment (0.0 to 1.0).

    Returns:
        dict: A dictionary containing:
            {
                "situation": str,
                "risk": str,
                "focus_score": int,   # Focus Score (range 0 to 100)
                "safety_score": int,   # Safety Score (range 0 to 10)
                "gemini_confidence": float  # Confidence score from Gemini (if available)
            }
    """
    # Get base scores from the scoring module
    result = calculate_scores(situation, risk, detections)
    
    # If Gemini provided confidence, adjust scores
    if gemini_confidence is not None:
        # Adjust scores based on Gemini confidence
        # Lower confidence = more uncertainty = slightly lower scores
        confidence_factor = gemini_confidence
        
        # Apply confidence-based adjustments
        # If confidence is low (< 0.5), reduce scores to reflect uncertainty
        if confidence_factor < 0.5:
            result["focus_score"] = int(result["focus_score"] * 0.8)
            result["safety_score"] = int(result["safety_score"] * 0.8)
        elif confidence_factor < 0.7:
            result["focus_score"] = int(result["focus_score"] * 0.9)
            result["safety_score"] = int(result["safety_score"] * 0.9)
        
        # Clamp scores to their defined boundaries
        result["focus_score"] = max(0, min(100, result["focus_score"]))
        result["safety_score"] = max(0, min(10, result["safety_score"]))
    
    result["gemini_confidence"] = gemini_confidence
    
    return result