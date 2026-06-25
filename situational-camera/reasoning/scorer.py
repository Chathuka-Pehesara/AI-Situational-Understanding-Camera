from scoring.scoring import calculate_scores

def compute_scores(situation: str, risk: str, detections=None) -> dict:
    """
    Computes situational metrics, specifically a Focus Score and a Safety Score.

    Parameters:
        situation (str): The current situation description.
        risk (str): The current risk level.
        detections (list, optional): List of detected objects.

    Returns:
        dict: A dictionary containing:
            {
                "situation": str,
                "risk": str,
                "focus_score": int,   # Focus Score (range 0 to 100)
                "safety_score": int   # Safety Score (range 0 to 10)
            }
    """
    return calculate_scores(situation, risk, detections)
