def detect_situation(detections,movement_detected):
    """
    detections:list of dictionaries
    Example:
    [
        {"label":"person"},
        {"label":"phone"},
        {"label":"bag"}
    ]
    movement_detected:True or False
    """
    labels=[item["label"] for item in detections]
    # 1. Working: person with laptop and not moving
    if (
        "person" in labels
        and "laptop" in labels
        and not movement_detected
    ):
        return {"situation": "Working", "risk": "High"}

    # 2. Distracted Walking: person + phone while moving
    if (
        "person" in labels
        and movement_detected
        and "phone" in labels
    ):
        return {"situation": "Distracted Walking", "risk": "High"}

    # 3. Hurrying: person moving while carrying bag or bottle
    if (
        "person" in labels
        and movement_detected
        and ("bag" in labels or "bottle" in labels)
    ):
        return {"situation": "Hurrying", "risk": "Medium"}

    # 4. Resting: person not moving and not engaged with phone/laptop
    if (
        "person" in labels
        and not movement_detected
        and "phone" not in labels
        and "laptop" not in labels
    ):
        return {"situation": "Resting", "risk": "Low"}

    # Default fallback
    return {"situation": "Normal Activity", "risk": "Low"}
