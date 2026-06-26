from torch._export.utils import _assign_new_node_names
from torch.fx.proxy import annotation_log
from sympy import continued_fraction
import cv2
import numpy as np

def render_overlay(frame, detections, situation, risk):

    if frame is None:
        return None

    # Avoiding modifying the original frame in place
    annotated_frame = frame.copy()
    
    # Color mapping for risk levels (BGR format)
    risk_colors = {
        "low" : (0, 255, 0), # Green
        "medium" : (0, 255, 255), # Yellow
        "high" : (0, 0, 255) # Red

    }

    # Normalize risk input and get coressponding color
    risk_lower = (risk or "").strip().lower()
    risk_color = risk_colors.get(risk_lower, (0, 255, 0))

    # Draw bounding boxes per detectionn
    for detection in detections:
        bbox = detection.get("bbox")
        if not bbox or len(bbox) < 4 :
            continue

        x1, y1, x2, y2 = map(int, bbox)
        label = detection.get("label", "unknown")
        confidence = detection.get("confidence")

        # Draw bounding box
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), risk_color=2)

        # Build detection label text
        label_text = label
        if confidence is not None:
            label_text += f"{confidence:.2f}"

        # Draw text label background 
        (text_width, text_height), baseline = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        tag_x1 = x1
        tag_y1 = max(0, y1 - text_height -6)
        tag_x2 = x1 + text_width + 2
        tag_y2 = y1

        cv2.rectangle(annotated_frame, (tag_x1, tag_y1), (tag_x2, tag_y2), risk_color =-1)

        # Decide text color based on background 
        text_color = (0, 0, 0) if risk_lower == "medium" else (255, 255, 255)
        cv2.putText(
            annotated_frame,
            label_text,
            (x1 + 3, y1 - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            text_color,
            cv2.LINE_AA
        )

        # Draw situation text + risk level banner at the top of the frame
        h, x, _ = annotated_frame.shape
        banner_height = 50

        overelay = annotated_frame.copy()
        cv2.rectangle(overelay, (0, 0, 0), (w, banner_height), (30, 30, 30), -1) 

        alpha = 0.7
        cv2.addWeight(overelay, alpha, annotated_frame, 1 - alpha, 0, annotated_frame)

        # Draw situational label and description
        situation_label = f"Situation: {situation}"
        cv2.putText(
            annotated_frame,
            situation_label,
            (15, 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        # Draw risk-level text (right-aligned)
        risk_label = f"Risk: {risk.upper()}"
        (r_width, r_height), _ = cv2.getTextSize(risk_label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.putText(
            annotated_frame,
            risk_label,
            (w - r_width - 15, 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            risk_color,
            2,
            cv2.LINE_AA
        ) 

        return annotated_frame 
