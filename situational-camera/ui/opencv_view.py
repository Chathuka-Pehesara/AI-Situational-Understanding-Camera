import cv2
import numpy as np

def render_overlay(frame, detections, situation, risk):
    """
    Draws bounding boxes for detections, along with the situation and risk overlay, 
    onto the current video frame.

    Parameters:
        frame (numpy.ndarray): The input video frame to draw on.
        detections (list): List of detected objects with bounding boxes and labels.
        situation (str): Description of the current situation.
        risk (str): Current risk level (e.g. "Low", "Medium", "High").

    Returns:
        numpy.ndarray: The frame with overlay drawn.
    """
    if frame is None:
        return None

    # Copy frame to avoid modifying the original image
    out_frame = frame.copy()
    
    # Color palette (BGR format) - Vibrant neon colors matching web theme
    COLOR_MAP = {
        "person": (255, 240, 0),    # Neon Cyan
        "phone": (0, 183, 255),     # Neon Orange/Yellow
        "laptop": (102, 255, 0),    # Neon Green
        "bag": (246, 130, 59),      # Neon Blue
        "bottle": (168, 85, 247)    # Neon Purple
    }
    DEFAULT_COLOR = (255, 255, 255)
    
    # Draw detections
    if detections:
        for det in detections:
            label = det.get("label", "unknown")
            bbox = det.get("bbox", [])
            conf = det.get("confidence", 0.0)
            
            if len(bbox) >= 4:
                x1, y1, x2, y2 = map(int, bbox)
                color = COLOR_MAP.get(label, DEFAULT_COLOR)
                
                # Draw bounding box
                cv2.rectangle(out_frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw label background
                label_text = f"{label.upper()} {conf:.2f}"
                (w, h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(out_frame, (x1, y1 - 20), (x1 + w, y1), color, -1)
                
                # Draw text
                cv2.putText(out_frame, label_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    # Draw HUD Overlay at the top left
    h, w, _ = out_frame.shape
    
    # Create overlay for semi-transparency
    overlay = out_frame.copy()
    
    # HUD box coordinates
    hud_w, hud_h = 320, 90
    cv2.rectangle(overlay, (10, 10), (10 + hud_w, 10 + hud_h), (10, 15, 30), -1)
    
    # Apply overlay with transparency alpha = 0.75
    cv2.addWeighted(overlay, 0.75, out_frame, 0.25, 0, out_frame)
    
    # Draw HUD border (Neon Cyan)
    cv2.rectangle(out_frame, (10, 10), (10 + hud_w, 10 + hud_h), (255, 240, 0), 1)
    
    # Risk color mapping
    risk_colors = {
        "High": (85, 0, 255),      # Neon Red/Pink
        "Medium": (0, 183, 255),   # Neon Yellow
        "Low": (102, 255, 0)       # Neon Green
    }
    r_color = risk_colors.get(risk, (255, 255, 255))
    
    # Draw Text inside HUD
    cv2.putText(out_frame, "AI SITUATIONAL CAMERA", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(out_frame, f"SITUATION: {situation}", (20, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(out_frame, "RISK: ", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(out_frame, risk.upper(), (70, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, r_color, 2, cv2.LINE_AA)

    return out_frame

