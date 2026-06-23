import math

_previous_centers = {}        # to store previous frame's centrer coordinates for each person
MOVEMENT_THRESHOLD = 5.0      # distance threshold in pixels above which movement is flagged as True

def is_moving(person_id, current_bbox) -> bool:

    global _previous_centers

    if not current_bbox or len(current_bbox) < 4:
        return False

    x1, y1, x2, y2 = current_bbox

    # step 1: calculate the center of the bounding box
    current_center_x = (x1 + x2) /2.0
    current_center_y = (y1 + y2) /2.0

    # step 2: check if have a previous record for this person
    if person_id in _previous_centers:
        prev_center_x, prev_center_y = _previous_centers[person_id]
        
        # step 3: Compute Eulidean disatance to the previous center
        distance = math.sqrt(
            (current_center_x - prev_center_x) ** 2 +
            (current_center_y - prev_center_y) ** 2
        )

        # flag movement if distance exeeds the threshold
        movement_detected = distance > MOVEMENT_THRESHOLD
    else:
        movement_detected = False  # new person
    
    # step 4: update the store center for this person
    _previous_centers[person_id] = (current_center_x, current_center_y)

    return movement_detected
 
# to clear stored tracking history for new video feeds or tests 
def reset_tracker():

    global _previous_centers
    _previous_centers.clear()
    

