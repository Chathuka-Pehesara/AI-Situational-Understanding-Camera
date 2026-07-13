import math
import time
import cv2
import numpy as np

# Store history of center coordinates for each person (for movement detection)
_person_histories = {}        

# Parameters for movement filtering
HISTORY_WINDOW = 15          # Number of frames to check movement over (~0.5 seconds at 30 FPS)
MOVEMENT_THRESHOLD = 15.0     # Minimum net displacement in pixels over the history window to classify as moving

# Spatial tracker storage
_tracks = {}
_next_track_id = 1
MAX_UNSEEN_FRAMES = 15        # Keep track active for ~0.5s if person is temporarily occluded
MAX_TRACK_DISTANCE = 100.0    # Maximum pixel distance to match a person between consecutive frames

def is_moving(person_id, current_bbox) -> bool:
    """
    Checks if a person has moved significantly over the history window.
    """
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
    Clears the stored tracking history and spatial tracks.
    """
    global _person_histories, _tracks, _next_track_id
    _person_histories.clear()
    _tracks.clear()
    _next_track_id = 1


def track_and_analyze_zones(detections, zones=None, loitering_threshold=5.0):

    global _tracks, _next_track_id

    if zones is None:
        zones = {}

    current_time = time.time()
    
    # 1. Extract and process person detections
    person_dets = []
    other_dets = []
    
    for det in detections:
        if det.get("label") == "person" and "bbox" in det:
            bbox = det["bbox"]
            cx = (bbox[0] + bbox[2]) / 2.0
            cy = (bbox[1] + bbox[3]) / 2.0
            det_copy = det.copy()
            det_copy["centroid"] = (cx, cy)
            person_dets.append(det_copy)
        else:
            other_dets.append(det.copy())

    # 2. Match current persons to existing tracks
    matched_det_indices = set()
    matched_track_ids = set()

    if _tracks and person_dets:
        # Compute distances between all current centroids and active tracks
        track_items = list(_tracks.items())
        
        # Greedy matching based on distance
        associations = []
        for d_idx, det in enumerate(person_dets):
            cx, cy = det["centroid"]
            for t_id, track in track_items:
                tx, ty = track["centroid"]
                dist = math.sqrt((cx - tx) ** 2 + (cy - ty) ** 2)
                if dist < MAX_TRACK_DISTANCE:
                    associations.append((dist, d_idx, t_id))
        
        # Sort associations by distance
        associations.sort(key=lambda x: x[0])
        
        for dist, d_idx, t_id in associations:
            if d_idx not in matched_det_indices and t_id not in matched_track_ids:
                matched_det_indices.add(d_idx)
                matched_track_ids.add(t_id)
                
                # Update existing track
                det = person_dets[d_idx]
                _tracks[t_id]["centroid"] = det["centroid"]
                _tracks[t_id]["bbox"] = det["bbox"]
                _tracks[t_id]["frames_unseen"] = 0
                det["track_id"] = t_id

    # 3. Handle unmatched current detections (register new tracks)
    for d_idx, det in enumerate(person_dets):
        if d_idx not in matched_det_indices:
            t_id = _next_track_id
            _next_track_id += 1
            
            _tracks[t_id] = {
                "centroid": det["centroid"],
                "bbox": det["bbox"],
                "frames_unseen": 0,
                "zone_occupancies": {}  # zone_name -> enter_timestamp
            }
            det["track_id"] = t_id
            matched_track_ids.add(t_id)

    # 4. Handle unmatched tracks (increment unseen, delete if stale)
    stale_track_ids = []
    for t_id in list(_tracks.keys()):
        if t_id not in matched_track_ids:
            _tracks[t_id]["frames_unseen"] += 1
            if _tracks[t_id]["frames_unseen"] > MAX_UNSEEN_FRAMES:
                stale_track_ids.append(t_id)
                
    for t_id in stale_track_ids:
        del _tracks[t_id]

    # 5. Check zone collisions for each tracked person
    for det in person_dets:
        t_id = det["track_id"]
        bbox = det["bbox"]
        
        # Check center and corners of bounding box to make it very easy to trigger zones in webcam mode
        pts_to_test = [
            (int((bbox[0] + bbox[2]) / 2.0), int((bbox[1] + bbox[3]) / 2.0)), # center
            (int(bbox[0]), int(bbox[1])), # top-left
            (int(bbox[2]), int(bbox[1])), # top-right
            (int(bbox[0]), int(bbox[3])), # bottom-left
            (int(bbox[2]), int(bbox[3])), # bottom-right
        ]
        
        inside_zone = None
        loitering_duration = 0.0
        is_trespassing = False
        is_perimeter_breach = False
        is_unsafe_zone_breach = False
        is_loitering = False
        
        # Check all zones
        for zone_name, polygon in zones.items():
            if not polygon or len(polygon) < 3:
                continue
            
            # Format polygon for OpenCV pointPolygonTest
            poly_np = np.array(polygon, dtype=np.int32).reshape((-1, 1, 2))
            
            # Perform point-in-polygon test for all points (trigger if ANY point is inside)
            is_inside = any(cv2.pointPolygonTest(poly_np, pt, False) >= 0 for pt in pts_to_test)
            
            if is_inside:
                inside_zone = zone_name
                
                # Check occupancy duration
                occupancies = _tracks[t_id]["zone_occupancies"]
                if zone_name not in occupancies:
                    occupancies[zone_name] = current_time
                    
                duration = current_time - occupancies[zone_name]
                loitering_duration = max(loitering_duration, duration)
                
                if zone_name == "Suspicious Movement (Left)":
                    is_trespassing = True
                elif zone_name == "Suspicious Movement (Right)":
                    is_perimeter_breach = True
                elif "Looking Away" in zone_name or "out of bounds" in zone_name.lower():
                    is_unsafe_zone_breach = True
                    
                if duration >= loitering_threshold:
                    is_loitering = True
            else:
                # Remove if exited
                if zone_name in _tracks[t_id]["zone_occupancies"]:
                    del _tracks[t_id]["zone_occupancies"][zone_name]
                    
        # Populate zone_info
        det["zone_info"] = {
            "inside_zone": inside_zone,
            "loitering_duration": round(loitering_duration, 1),
            "is_trespassing": is_trespassing,
            "is_perimeter_breach": is_perimeter_breach,
            "is_unsafe_zone_breach": is_unsafe_zone_breach,
            "is_loitering": is_loitering
        }
        
        # Clean temporary centroid helper
        if "centroid" in det:
            del det["centroid"]

    # Recombine all detections
    return person_dets + other_dets
