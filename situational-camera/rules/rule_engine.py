def detect_situation(detections, movement_detected):

    if not detections or not isinstance(detections, list):
        labels = []
    else:
        labels = [item.get("label") for item in detections if isinstance(item, dict) and "label" in item]

    is_moving = bool(movement_detected)

    # 1. Zone Collision Alerts & High Priority Situations
    is_trespassing = False
    is_loitering = False
    is_perimeter_breach = False
    is_unsafe_zone = False
    is_fall = False
    is_webcam_user = False
    is_head_left = False
    is_head_right = False
    loitering_zone = None

    for item in detections:
        if isinstance(item, dict) and item.get("label") == "person":
            if item.get("head_pose") in ["left", "right", "away"]:
                is_head_left = True # We treat all 'away' as a generic 'Looking Away' alert
                
            # Fall detection logic based on bounding box proportions (width > height)
            if "bbox" in item:
                x1, y1, x2, y2 = item["bbox"]
                width = x2 - x1
                height = y2 - y1
                if width > height and height > 0:
                    # If the bounding box is very large, it's likely a person sitting close to a webcam
                    if width > 250 and height > 200:
                        is_webcam_user = True
                    else:
                        # Simple heuristic for fall detection
                        is_fall = True

            zone_info = item.get("zone_info")
            if zone_info:
                if zone_info.get("is_trespassing"):
                    is_trespassing = True
                if zone_info.get("is_loitering"):
                    is_loitering = True
                    loitering_zone = zone_info.get("inside_zone")
                if zone_info.get("is_perimeter_breach"):
                    is_perimeter_breach = True
                if zone_info.get("is_unsafe_zone_breach") or (zone_info.get("inside_zone") and "Unsafe" in zone_info.get("inside_zone")):
                    is_unsafe_zone = True

    # 1. High Priority Proctoring Rules
    if labels.count("person") > 1:
        return {"situation": "Multiple People Detected", "risk": "High"}
        
    if "cell phone" in labels or "phone" in labels:
        return {"situation": "Unauthorized Device", "risk": "High"}

    # Weapon Detected (just in case)
    if "knife" in labels:
        return {"situation": "Weapon Detected", "risk": "High"}

    # Zone Violations and Head Pose
    if is_head_left:
        return {"situation": "Looking Away", "risk": "High"}

    if is_loitering:
        return {"situation": "Prolonged Suspicious Movement", "risk": "High"}

    # Webcam / Fall detection
    if is_webcam_user:
        return {"situation": "Exam in Progress", "risk": "Low"}

    if is_fall:
        return {"situation": "Fall Detected", "risk": "High"}

    # Animal Intrusion (low/medium risk stray animal check)
    if "animal" in labels:
        return {"situation": "Animal Intrusion", "risk": "Medium" if is_moving else "Low"}

    # Vehicle Loitering (medium risk vehicle check)
    if "bicycle" in labels or "motorcycle" in labels:
        return {"situation": "Vehicle Loitering", "risk": "Medium"}

    # 2. Distracted Walking: person + phone while moving
    if (
        "person" in labels
        and "phone" in labels
        and is_moving
    ):
        return {"situation": "Distracted Walking", "risk": "High"}

    # 3. Working: person + laptop (always low risk for exams to allow typing)
    if (
        "person" in labels
        and "laptop" in labels
    ):
        return {"situation": "Working", "risk": "Low"}

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
