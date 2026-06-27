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

def _get_model():
    global _model
    if _model is None:
        # Load yolov8n.pt model (will download automatically if not present)
        _model = YOLO("yolov8n.pt")
    return _model

def detect_objects(frame):
 
    if frame is None:
        return []

    model = _get_model()
    # Run prediction filtering for the target classes to optimize speed
    results = model.predict(source=frame, classes=TARGET_CLASSES, verbose=False)

    detections = []
    if len(results) > 0:
        boxes = results[0].boxes
        if boxes is not None:
            for box in boxes:
                xyxy = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                conf = float(box.conf[0].item())
                cls_id = int(box.cls[0].item())

                # Get tracking ID assigned by YOLOv8 
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

