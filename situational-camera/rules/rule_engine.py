def detect_situation(detections, movement_detected):

    if not detections or not isinstance(detections, list):
        labels = []
    else:
        labels = [item.get("label") for item in detections if isinstance(item, dict) and "label" in item]

    is_moving = bool(movement_detected)

    # 1. Zone Collision Alerts (highest priority)
    is_trespassing = False
    is_loitering = False
    is_perimeter_breach = False
    loitering_zone = None

    for item in detections:
        if isinstance(item, dict) and item.get("label") == "person":
            zone_info = item.get("zone_info")
            if zone_info:
                if zone_info.get("is_trespassing"):
                    is_trespassing = True
                if zone_info.get("is_loitering"):
                    is_loitering = True
                    loitering_zone = zone_info.get("inside_zone")
                if zone_info.get("is_perimeter_breach"):
                    is_perimeter_breach = True

    if is_loitering:
        risk = "High" if loitering_zone == "Restricted Zone A" else "Medium"
        return {"situation": "Loitering", "risk": risk}

    if is_trespassing:
        return {"situation": "Trespassing", "risk": "High"}

    if is_perimeter_breach:
        return {"situation": "Perimeter Breach", "risk": "Medium"}

    # 2. Distracted Walking: person + phone while moving
    if (
        "person" in labels
        and "phone" in labels
        and is_moving
    ):
        return {"situation": "Distracted Walking", "risk": "High"}

    # 3. Working: person + laptop (low risk if stationary, medium risk if moving)
    if (
        "person" in labels
        and "laptop" in labels
    ):
        return {"situation": "Working", "risk": "Medium" if is_moving else "Low"}

    # 4. Hurrying: person moving while carrying bag or bottle
    if (
        "person" in labels
        and is_moving
        and ("bag" in labels or "bottle" in labels)
    ):
        return {"situation": "Hurrying", "risk": "Medium"}

    # 5. Resting: person not moving and not engaged with phone/laptop
    if (
        "person" in labels
        and not is_moving
        and "phone" not in labels
        and "laptop" not in labels
    ):
        return {"situation": "Resting", "risk": "Low"}

    # Default fallback
    return {"situation": "Normal Activity", "risk": "Low"}


