import cv2
import numpy as np

def render_overlay(frame, detections, situation, risk, zones=None):

    if frame is None:
        return None

    out_frame = frame.copy()
    
    # 1. Define or use default zones
    if zones is None:
        zones = {
            "Restricted Zone A": [
                [30, 80],
                [250, 80],
                [220, 400],
                [10, 400]
            ],
            "Perimeter Gate": [
                [380, 120],
                [600, 120],
                [620, 450],
                [400, 450]
            ]
        }

    # 2. Draw semi-transparent zone polygons
    overlay = out_frame.copy()
    for zone_name, polygon in zones.items():
        if not polygon or len(polygon) < 3:
            continue
        poly_np = np.array(polygon, dtype=np.int32).reshape((-1, 1, 2))
        
        # Color based on zone
        if zone_name == "Restricted Zone A":
            color = (0, 0, 255)       # Red
        elif zone_name == "Perimeter Gate":
            color = (0, 165, 255)     # Orange/Yellow
        else:
            color = (255, 0, 0)       # Blue
            
        cv2.fillPoly(overlay, [poly_np], color)
        
    cv2.addWeighted(overlay, 0.15, out_frame, 0.85, 0, out_frame)

    # 3. Draw zone borders and text labels
    for zone_name, polygon in zones.items():
        if not polygon or len(polygon) < 3:
            continue
        poly_np = np.array(polygon, dtype=np.int32).reshape((-1, 1, 2))
        
        if zone_name == "Restricted Zone A":
            color = (0, 0, 255)
        elif zone_name == "Perimeter Gate":
            color = (0, 165, 255)
        else:
            color = (255, 0, 0)
            
        cv2.polylines(out_frame, [poly_np], True, color, 2)
        x, y = polygon[0]
        cv2.putText(out_frame, zone_name.upper(), (x, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)

    # Color palette (BGR format) - Vibrant neon colors matching web theme
    COLOR_MAP = {
        "person": (255, 240, 0),    # Neon Cyan
        "phone": (0, 183, 255),     # Neon Orange/Yellow
        "laptop": (102, 255, 0),    # Neon Green
        "bag": (246, 130, 59),      # Neon Blue
        "bottle": (168, 85, 247),   # Neon Purple
        "knife": (0, 0, 255),       # Crimson Red
        "bicycle": (0, 165, 255),   # Safety Orange
        "motorcycle": (0, 165, 255),# Safety Orange
        "animal": (0, 255, 128)     # Mint Green
    }
    DEFAULT_COLOR = (255, 255, 255)
    
    # 4. Draw detections with zone alert styling
    if detections:
        for det in detections:
            label = det.get("label", "unknown")
            bbox = det.get("bbox", [])
            conf = det.get("confidence", 0.0)
            
            if len(bbox) >= 4:
                x1, y1, x2, y2 = map(int, bbox)
                
                # Check for zone-specific styling
                color = COLOR_MAP.get(label, DEFAULT_COLOR)
                
                if label == "knife":
                    label_text = f"WEAPON [KNIFE] {conf:.2f}"
                elif label == "animal":
                    label_text = f"ANIMAL DETECTED {conf:.2f}"
                else:
                    label_text = f"{label.upper()} {conf:.2f}"
                
                if label == "person":
                    zone_info = det.get("zone_info")
                    if zone_info:
                        if zone_info.get("is_trespassing"):
                            color = (0, 0, 255) # Red Alert
                            dur = zone_info.get("loitering_duration", 0.0)
                            label_text = f"TRESPASSER {dur}s"
                        elif zone_info.get("is_loitering"):
                            color = (0, 165, 255) # Orange Alert
                            dur = zone_info.get("loitering_duration", 0.0)
                            label_text = f"LOITERING {dur}s"
                        elif zone_info.get("is_perimeter_breach"):
                            color = (0, 165, 255) # Orange Alert
                            label_text = f"BREACH"
                
                # Draw bounding box
                cv2.rectangle(out_frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw label background
                (w, h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
                cv2.rectangle(out_frame, (x1, y1 - 20), (x1 + w, y1), color, -1)
                
                # Draw text
                cv2.putText(out_frame, label_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)
 
    # 5. Draw HUD Overlay at the top left
    h, w, _ = out_frame.shape
    
    # Create overlay for semi-transparency
    overlay_hud = out_frame.copy()
    
    # HUD box coordinates
    hud_w, hud_h = 320, 90
    cv2.rectangle(overlay_hud, (10, 10), (10 + hud_w, 10 + hud_h), (10, 15, 30), -1)
    
    # Apply overlay with transparency alpha = 0.75
    cv2.addWeighted(overlay_hud, 0.75, out_frame, 0.25, 0, out_frame)
    
    # Draw HUD border (Red if weapon detected, otherwise Neon Cyan)
    hud_border_color = (0, 0, 255) if situation == "Weapon Detected" else (255, 240, 0)
    cv2.rectangle(out_frame, (10, 10), (10 + hud_w, 10 + hud_h), hud_border_color, 2 if situation == "Weapon Detected" else 1)
    
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


