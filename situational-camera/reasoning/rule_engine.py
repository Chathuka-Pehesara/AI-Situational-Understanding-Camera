from rules.rule_engine import detect_situation

def evaluate_situation(detections, movement_detected) -> dict:
    """
    Evaluates situation rules (e.g., Person + Phone + Movement) to determine 
    the overall situation and risk level.

    Parameters:
        detections (list): List of detected objects with their labels and bounding boxes.
        movement_detected (bool): Whether significant movement is currently detected.

    Returns:
        dict: A dictionary containing:
            {
                "situation": str,  # Description of the situation (e.g., "Walking while texting")
                "risk": str        # Risk level (e.g., "Low", "Medium", "High")
            }
    """
    return detect_situation(detections, movement_detected)
