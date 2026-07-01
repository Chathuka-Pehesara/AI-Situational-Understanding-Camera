import math

# Store history of center coordinates for each person
_person_histories = {}        

# Parameters for movement filtering
HISTORY_WINDOW = 15          # Number of frames to check movement over (~0.5 seconds at 30 FPS)
MOVEMENT_THRESHOLD = 15.0     # Minimum net displacement in pixels over the history window to classify as moving

def is_moving(person_id, current_bbox) -> bool:
   
    global _person_histories

    if not current_bbox or len(current_bbox) < 4:
        return False

    x1, y1, x2, y2 = current_bbox

    # 1. Calculate the center of the bounding box
    current_center_x = (x1 + x2) / 2.0
    current_center_y = (y1 + y2) / 2.0

    # 2. Initialize history list if new person
    if person_id not in _person_histories:
        _person_histories[person_id] = []

    history = _person_histories[person_id]
    history.append((current_center_x, current_center_y))

    # 3. Maintain history window size
    if len(history) > HISTORY_WINDOW:
        history.pop(0)

    # 4. If window is not full, assume stationary until enough data accumulates
    if len(history) < HISTORY_WINDOW:
        return False

    # 5. Compute Euclidean distance from the oldest point in the window to the current point
    oldest_x, oldest_y = history[0]
    distance = math.sqrt(
        (current_center_x - oldest_x) ** 2 +
        (current_center_y - oldest_y) ** 2
    )

    # 6. Flag movement if the net displacement exceeds the threshold
    movement_detected = distance > MOVEMENT_THRESHOLD
    return movement_detected

def reset_tracker():
    """
    Clears the stored tracking history.
    """
    global _person_histories
    _person_histories.clear()
