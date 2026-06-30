import math

# Store history of centers for each person: {person_id: [ (cx, cy), ... ]}
_history = {}
MAX_HISTORY_LEN = 10
MOVEMENT_THRESHOLD = 15.0  # pixels (displacement threshold to be considered moving)

def is_moving(person_id, current_bbox) -> bool:
    """
    Compares bounding box centers across frames for a specific person
    to determine if they are moving.

    Parameters:
        person_id (int/str): Unique identifier for the tracked person.
        current_bbox (list): Current bounding box coordinates [x1, y1, x2, y2].

    Returns:
        bool: True if significant movement is detected, False otherwise.
    """
    global _history
    if not current_bbox or len(current_bbox) < 4:
        return False

    # Calculate center of current bounding box
    cx = (current_bbox[0] + current_bbox[2]) / 2.0
    cy = (current_bbox[1] + current_bbox[3]) / 2.0
    current_center = (cx, cy)

    if person_id not in _history:
        _history[person_id] = [current_center]
        return False

    history = _history[person_id]
    
    # Calculate distance from the oldest recorded position in history to current position
    oldest_center = history[0]
    distance = math.sqrt((cx - oldest_center[0])**2 + (cy - oldest_center[1])**2)
    
    # Add new center to history and trim
    history.append(current_center)
    if len(history) > MAX_HISTORY_LEN:
        history.pop(0)

    # If the displacement is above threshold, person is moving
    return distance >= MOVEMENT_THRESHOLD

