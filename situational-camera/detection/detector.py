import cv2
import numpy as np
from ultralytics import YOLO

# Initialize YOLOv8 Nano model globally to avoid loading it on every frame
_model = None

# Mappings from COCO class names / indices to the shared data-contract labels
CLASS_MAPPING = {
    0: "person",
    2: "car",
    24: "bag",       # backpack
    26: "bag",       # handbag
    28: "bag",       # suitcase
    39: "bottle",
    63: "laptop",
    67: "phone"      # cell phone
}

TARGET_CLASSES = list(CLASS_MAPPING.keys())
CONFIDENCE_THRESHOLD = 0.5

def _get_model():
    global _model
    if _model is None:
        # Load yolov8n.pt model (already present in the repository)
        _model = YOLO("yolov8n.pt")
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
    # Run prediction filtering for the target classes to optimize speed
    results = model.predict(source=frame, classes=TARGET_CLASSES, conf=CONFIDENCE_THRESHOLD, verbose=False)

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
                    detections.append({
                        "label": label,
                        "bbox": [float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])],
                        "confidence": conf,
                        "track_id": track_id
                    })

    return detections
