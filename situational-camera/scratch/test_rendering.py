import sys
import os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.opencv_view import render_overlay

def test_render_overaly():
    print("tetsing render_overlay with dummy frame...")

    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    detections = [
        {"label": "person", "bbox": [100, 100, 200, 300], "confidence": 0.92},
        {"label": "phone", "bbox": [120, 120, 150, 180], "confidence": 0.85}
    ]

    output_high = render_overlay(dummy_frame, detections, "Distracted Walking", "High")
    assert output_high is not None, "Ouput frame should not be None"
    assert output_high.shape == dummy_frame.shape, f"Exceptde shape {dummy_frame.shape}, got {output_high.shape}"

    output_med = render_overlay(dummy_frame, detections, "Hurrying", "Medium")
    assert output_med is not None
    
    # Test Low risk (Green overlay & boxes)
    output_low = render_overlay(dummy_frame, detections, "Resting", "Low")
    assert output_low is not None

    assert render_overlay(None, detections, "Normal", "Low") is None

    print("Success: render_overlay verification completed successfully")


if __name__ == "__main__":
    test_render_overaly()
