import sys
import os
import numpy as np

# Ensure the situational-camera directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detection.detector import detect_objects

def test_detector_with_empty_frame():
    print("Testing detector with empty/None frame...")
    detections = detect_objects(None)
    assert detections == [], f"Expected empty list for None frame, got {detections}"
    print("Success: None frame handled correctly.")

def test_detector_with_dummy_image():
    print("\nTesting detector with dummy black image (640x640x3)...")
    dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
    
    # Run detector
    detections = detect_objects(dummy_frame)
    
    print(f"Detections returned: {detections}")
    assert isinstance(detections, list), f"Expected list, got {type(detections)}"
    for det in detections:
        assert "label" in det, "Detection missing 'label' key"
        assert "bbox" in det, "Detection missing 'bbox' key"
        assert "confidence" in det, "Detection missing 'confidence' key"
        assert len(det["bbox"]) == 4, f"Expected 4 bounding box coordinates, got {len(det['bbox'])}"
        assert isinstance(det["label"], str), f"Expected string label, got {type(det['label'])}"
        assert isinstance(det["confidence"], float), f"Expected float confidence, got {type(det['confidence'])}"
        
    print("Success: Dummy image ran successfully, data contract verified.")

if __name__ == "__main__":
    try:
        test_detector_with_empty_frame()
        test_detector_with_dummy_image()
        print("\nAll detector verification tests passed successfully!")
    except Exception as e:
        print(f"\nVerification test failed: {e}")
        sys.exit(1)
