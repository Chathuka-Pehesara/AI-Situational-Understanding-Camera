import cv2
import numpy as np
from ultralytics import YOLO

# Initialize YOLOv8 models globally to avoid loading them on every frame
_model = None
_pose_model = None

def _get_pose_model():
    global _pose_model
    if _pose_model is None:
        _pose_model = YOLO("yolov8n-pose.pt")
    return _pose_model

def analyze_head_pose(frame, bbox=None):
    if frame is None or bbox is None:
        return "forward"
        
    try:
        x1, y1, x2, y2 = map(int, bbox)
        
        # Add safety boundaries
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        if x2 <= x1 or y2 <= y1:
            return "forward"
            
        crop = frame[y1:y2, x1:x2]
        pose_model = _get_pose_model()
        results = pose_model.predict(crop, verbose=False)
        
        if len(results) > 0 and results[0].keypoints is not None:
            xy = results[0].keypoints.xy
            if len(xy) > 0 and len(xy[0]) >= 5:
                # 0: nose, 1: left eye, 2: right eye, 3: left ear, 4: right ear
                nose_x = float(xy[0][0][0])
                left_ear_x = float(xy[0][3][0])
                right_ear_x = float(xy[0][4][0])
                
                if nose_x > 0:
                    # If one ear is hidden, head is turned
                    if left_ear_x > 0 and right_ear_x == 0:
                        return "left"
                    if right_ear_x > 0 and left_ear_x == 0:
                        return "right"
                    
                    # If both ears visible, compare distances to nose
                    if left_ear_x > 0 and right_ear_x > 0:
                        dist_l = abs(nose_x - left_ear_x)
                        dist_r = abs(nose_x - right_ear_x)
                        if dist_r > 0 and (dist_l / dist_r) > 2.0:
                            return "right"
                        if dist_l > 0 and (dist_r / dist_l) > 2.0:
                            return "left"
                            
        return "forward"
    except Exception as e:
        return "forward"

# Mappings from COCO class names / indices to the shared data-contract labels
CLASS_MAPPING = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    15: "animal",    # cat
    16: "animal",    # dog
    24: "bag",       # backpack
    26: "bag",       # handbag
    28: "bag",       # suitcase
    39: "bottle",
    43: "knife",     # knife / weapon
    63: "laptop",
    67: "phone"      # cell phone
}

TARGET_CLASSES = list(CLASS_MAPPING.keys())

def _get_model():
    global _model
    if _model is None:
        # Load yolov8s.pt model for higher accuracy (will download automatically if not present)
        _model = YOLO("yolov8s.pt")
    return _model

def enhance_low_light(frame):
    if frame is None:
        return None
    # Convert BGR to LAB color space to separate lightness from color
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Create and apply CLAHE filter (clipLimit=3.0, tileGridSize=(8,8))
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    
    # Merge back and convert to BGR
    enhanced_lab = cv2.merge((cl, a, b))
    enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    return enhanced_bgr

def detect_objects(frame):
    if frame is None:
        return []

    # 1. Detect if the frame is a dark/low-light scene
    # Compute mean pixel intensity of the grayscale version of the frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_brightness = gray.mean()

    # If average brightness is below 75, apply CLAHE night-vision enhancement
    if mean_brightness < 75:
        enhanced = enhance_low_light(frame)
        if enhanced is not None:
            # Modify frame in-place so subsequent pipeline steps (HUD overlay, display)
            # automatically use the enhanced frame.
            np.copyto(frame, enhanced)

    model = _get_model()
    # Run prediction filtering for the target classes with tuned thresholds to optimize accuracy
    results = model.predict(source=frame, classes=TARGET_CLASSES, conf=0.3, iou=0.45, verbose=False)

    detections = []
    
    if len(results) > 0:
        boxes = results[0].boxes
        if boxes is not None:
            for box in boxes:
                xyxy = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                conf = float(box.conf[0].item())
                cls_id = int(box.cls[0].item())

                # Get tracking ID assigned by YOLOv8 (if track_id is available/tracked)
                track_id = int(box.id[0].item()) if box.id is not None else None

                label = CLASS_MAPPING.get(cls_id)
                if label is not None:
                    bbox = [float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])]
                    det = {
                        "label": label,
                        "bbox": bbox,
                        "confidence": conf,
                        "track_id": track_id
                    }
                    if label == "person":
                        det["head_pose"] = analyze_head_pose(frame, bbox)
                    detections.append(det)

    return detections
