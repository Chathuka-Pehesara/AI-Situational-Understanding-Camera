def calculate_scores(situation, risk, detections=None):
    """
    Computes situational metrics, specifically a Focus Score and a Safety Score.

    Parameters:
        situation (str): The detected situation.
        risk (str): The risk level (Low, Medium, High).
        detections (list, optional): List of detected objects.

    Returns:
        dict: A dictionary containing:
            {
                "situation": str,
                "risk": str,
                "focus_score": int,
                "safety_score": int
            }
    """

    focus_score = 100
    safety_score = 10

    # Risk level base modifiers
    if risk == "High":
        focus_score -= 40
        safety_score -= 5
    elif risk == "Medium":
        focus_score -= 20
        safety_score -= 3
    elif risk == "Low":
        focus_score -= 5
        safety_score -= 1

    # Situation specific modifiers
    if situation == "Distracted Walking":
        focus_score -= 20
        safety_score -= 2
    elif situation == "Hurrying":
        focus_score -= 10
        safety_score -= 1
    elif situation == "Working":
        # Working is a highly focused and safe activity, offsetting the low risk deduction
        focus_score += 5
        safety_score += 1
    elif situation == "Resting":
        # Resting is safe, offsetting the low risk deduction
        focus_score += 5
        safety_score += 1

    # Object-specific modifiers
    if detections and isinstance(detections, list):
        labels = [item.get("label") for item in detections if isinstance(item, dict) and "label" in item]

        if "phone" in labels:
            focus_score -= 10

        if "car" in labels:
            safety_score -= 2

    # Clamp scores to their defined boundaries
    focus_score = max(0, min(100, focus_score))
    safety_score = max(0, min(10, safety_score))

    return {
        "situation": situation,
        "risk": risk,
        "focus_score": focus_score,
        "safety_score": safety_score
    }

if __name__ == "__main__":
    sample_detections = [
        {"label": "person"},
        {"label": "phone"}
    ]

    result = calculate_scores(
        situation="Distracted Walking",
        risk="High",
        detections=sample_detections
    )

    print("Situation:", result["situation"])
    print("Risk:", result["risk"])
    print("Focus Score:", result["focus_score"])
    print("Safety Score:", result["safety_score"])