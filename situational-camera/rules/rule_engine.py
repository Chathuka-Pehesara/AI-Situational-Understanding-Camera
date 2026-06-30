def detect_situation(detections, movement_detected):
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
    if not detections or not isinstance(detections, list):
        labels = []
    else:
        labels = [item.get("label") for item in detections if isinstance(item, dict) and "label" in item]

    is_moving = bool(movement_detected)

    # 1. Distracted Walking: person + phone while moving
    if (
        "person" in labels
        and "phone" in labels
        and is_moving
    ):
        return {"situation": "Distracted Walking", "risk": "High"}

    # 2. Working: person + laptop (low risk if stationary, medium risk if moving)
    if (
        "person" in labels
        and "laptop" in labels
    ):
        return {"situation": "Working", "risk": "Medium" if is_moving else "Low"}

    # 3. Hurrying: person moving while carrying bag or bottle
    if (
        "person" in labels
        and is_moving
        and ("bag" in labels or "bottle" in labels)
    ):
        return {"situation": "Hurrying", "risk": "Medium"}

    # 4. Resting: person not moving and not engaged with phone/laptop
    if (
        "person" in labels
        and not is_moving
        and "phone" not in labels
        and "laptop" not in labels
    ):
        return {"situation": "Resting", "risk": "Low"}

    # Default fallback
    return {"situation": "Normal Activity", "risk": "Low"}

