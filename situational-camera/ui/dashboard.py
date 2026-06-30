import streamlit as st
import pandas as pd
import os
import time
import sys
import datetime

# Ensure the situational-camera directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reasoning.rule_engine import evaluate_situation
from reasoning.explainer import generate_explanation
from reasoning.scorer import compute_scores
from custom_logging.event_logger import log_event

# HTML sanitization helper to prevent Streamlit from interpreting indented HTML as markdown code blocks
def clean_html(html_str):
    return "\n".join(line.strip() for line in html_str.split("\n") if line.strip())

# Configuration
CSV_FILE = "data/events_log.csv"

# Pre-defined presets for simulation matching rules/rule_engine.py logic
SIM_PRESETS = {
    "Normal Activity": {
        "detections": [{"label": "person", "bbox": [200, 100, 400, 500], "confidence": 0.95}],
        "movement": True
    },
    "Resting": {
        "detections": [{"label": "person", "bbox": [150, 120, 480, 480], "confidence": 0.92}],
        "movement": False
    },
    "Working": {
        "detections": [
            {"label": "person", "bbox": [220, 100, 380, 450], "confidence": 0.96},
            {"label": "laptop", "bbox": [300, 320, 450, 460], "confidence": 0.88}
        ],
        "movement": False
    },
    "Hurrying": {
        "detections": [
            {"label": "person", "bbox": [180, 80, 360, 520], "confidence": 0.94},
            {"label": "bag", "bbox": [340, 300, 420, 440], "confidence": 0.85}
        ],
        "movement": True
    },
    "Distracted Walking": {
        "detections": [
            {"label": "person", "bbox": [200, 100, 400, 500], "confidence": 0.97},
            {"label": "phone", "bbox": [290, 200, 340, 280], "confidence": 0.91}
        ],
        "movement": True
    }
}

st.set_page_config(
    page_title="AI Situational Understanding Camera",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark UI + Glassmorphism + Accent Neon Colors)
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

/* Main page styles */
.stApp {
    background: radial-gradient(circle at 50% 10%, #0d1225 0%, #040610 70%);
    color: #f1f5f9;
    font-family: 'Outfit', sans-serif;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #060914 !important;
    border-right: 1px solid rgba(0, 240, 255, 0.1);
}

/* Sidebar titles and text */
[data-testid="stSidebar"] .stMarkdown h1, 
[data-testid="stSidebar"] .stMarkdown h2, 
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #00f0ff !important;
    font-family: 'Outfit', sans-serif;
}

/* Modern Title bar */
.header-wrapper {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.25rem 2rem;
    background: rgba(10, 15, 30, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(0, 240, 255, 0.15);
    border-radius: 16px;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
}

.title-text {
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #00f0ff 30%, #ff0055 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.system-status {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #00ff66;
    background: rgba(0, 255, 102, 0.08);
    padding: 0.45rem 1rem;
    border-radius: 30px;
    border: 1px solid rgba(0, 255, 102, 0.2);
    box-shadow: 0 0 15px rgba(0, 255, 102, 0.1);
}

.status-dot {
    width: 8px;
    height: 8px;
    background-color: #00ff66;
    border-radius: 50%;
    animation: status-pulse 1.5s infinite alternate;
}

@keyframes status-pulse {
    0% { transform: scale(0.8); opacity: 0.5; box-shadow: 0 0 0 0 rgba(0, 255, 102, 0.7); }
    100% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 8px 3px rgba(0, 255, 102, 0.3); }
}

/* Section Header */
.section-header {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    color: #94a3b8;
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Live camera feed styling */
.camera-card {
    background: rgba(8, 12, 24, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 20px;
    padding: 1.25rem;
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    backdrop-filter: blur(15px);
}

.camera-container {
    background: #020308;
    border: 2px solid rgba(0, 240, 255, 0.15);
    border-radius: 14px;
    height: 380px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 30px rgba(0, 240, 255, 0.05) inset, 0 8px 24px rgba(0,0,0,0.6);
}

.camera-grid {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: 
        linear-gradient(rgba(0, 240, 255, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 240, 255, 0.02) 1px, transparent 1px);
    background-size: 25px 25px;
    z-index: 1;
}

.camera-scanline {
    position: absolute;
    width: 100%;
    height: 4px;
    background: linear-gradient(to bottom, rgba(0, 240, 255, 0) 0%, rgba(0, 240, 255, 0.4) 50%, rgba(0, 240, 255, 0) 100%);
    opacity: 0.8;
    z-index: 2;
    animation: scan 8s linear infinite;
}

@keyframes scan {
    0% { top: -10px; }
    100% { top: 390px; }
}

.camera-rec-dot {
    position: absolute;
    top: 1.25rem;
    left: 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(3, 5, 10, 0.85);
    padding: 0.35rem 0.75rem;
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    color: #fff;
    z-index: 3;
    letter-spacing: 0.05em;
}

.rec-pulse {
    width: 8px;
    height: 8px;
    background-color: #ff0055;
    border-radius: 50%;
    animation: rec-blink 1s infinite alternate;
}

@keyframes rec-blink {
    0% { opacity: 0.3; }
    100% { opacity: 1; box-shadow: 0 0 8px #ff0055; }
}

.camera-hud-corners {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    z-index: 2;
    pointer-events: none;
}

.camera-hud-corners::before, .camera-hud-corners::after, 
.camera-hud-corners span::before, .camera-hud-corners span::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    border-color: rgba(0, 240, 255, 0.35);
    border-style: solid;
}

.camera-hud-corners::before { top: 12px; left: 12px; border-width: 2px 0 0 2px; }
.camera-hud-corners::after { top: 12px; right: 12px; border-width: 2px 2px 0 0; }
.camera-hud-corners span::before { bottom: 12px; left: 12px; border-width: 0 0 2px 2px; }
.camera-hud-corners span::after { bottom: 12px; right: 12px; border-width: 0 2px 2px 0; }

/* Bounding box design */
.camera-bounding-box {
    position: absolute;
    border: 2px solid;
    z-index: 2;
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
    box-shadow: 0 0 15px rgba(0,0,0,0.3);
}

.camera-bounding-box.person { border-color: #00f0ff; background: rgba(0, 240, 255, 0.02); }
.camera-bounding-box.phone { border-color: #ffb700; background: rgba(255, 183, 0, 0.02); }
.camera-bounding-box.laptop { border-color: #00ff66; background: rgba(0, 255, 102, 0.02); }
.camera-bounding-box.bag { border-color: #3b82f6; background: rgba(59, 130, 246, 0.02); }

.bbox-label {
    position: absolute;
    top: -20px;
    left: -2px;
    color: #000;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    padding: 1px 5px;
    border-radius: 2px 2px 0 0;
}

.camera-bounding-box.person .bbox-label { background: #00f0ff; }
.camera-bounding-box.phone .bbox-label { background: #ffb700; }
.camera-bounding-box.laptop .bbox-label { background: #00ff66; }
.camera-bounding-box.bag .bbox-label { background: #3b82f6; }

/* HUD Alert styles */
.hud-alert-overlay {
    position: absolute;
    top: 1.25rem;
    right: 1.25rem;
    background: rgba(255, 0, 85, 0.15);
    border: 1px solid #ff0055;
    color: #ff0055;
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    z-index: 3;
    animation: flash 1s infinite alternate;
}

@keyframes flash {
    0% { opacity: 0.5; }
    100% { opacity: 1; box-shadow: 0 0 12px rgba(255, 0, 85, 0.4); }
}

/* Radar scan styles */
.radar-scan {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 180px; height: 180px;
    z-index: 2;
}

.radar-circle-1, .radar-circle-2, .radar-circle-3 {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    border: 1px solid rgba(0, 240, 255, 0.15);
    border-radius: 50%;
    animation: radar-pulse 3s infinite linear;
}
.radar-circle-2 { animation-delay: 1s; }
.radar-circle-3 { animation-delay: 2s; }

@keyframes radar-pulse {
    0% { transform: scale(0.1); opacity: 0.8; }
    100% { transform: scale(1.2); opacity: 0; }
}

.hud-center-msg {
    position: absolute;
    top: 55%; left: 50%;
    transform: translate(-50%, -50%);
    font-family: 'JetBrains Mono', monospace;
    color: rgba(0, 240, 255, 0.6);
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    z-index: 3;
}

/* Explanation display block */
.explanation-block {
    background: rgba(15, 23, 42, 0.5);
    border-left: 4px solid #00f0ff;
    padding: 1.25rem;
    border-radius: 0 16px 16px 0;
    margin-top: 1.25rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.explanation-title {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748b;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

.explanation-text {
    font-size: 1.05rem;
    color: #e2e8f0;
    font-weight: 500;
    line-height: 1.5;
}

/* Metric card styling */
.metrics-container {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.2rem;
}

.metric-card {
    background: rgba(12, 18, 38, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 1.25rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    backdrop-filter: blur(12px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; width: 4px; height: 100%;
    background: var(--accent-color, #00f0ff);
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    border-color: var(--accent-color, rgba(0, 240, 255, 0.3));
    box-shadow: 0 12px 40px var(--shadow-color, rgba(0, 240, 255, 0.05));
}

.metric-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.25rem;
}

.metric-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    font-weight: 700;
}

.metric-icon {
    font-size: 1.2rem;
}

.metric-value {
    font-size: 1.55rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0.25rem 0;
    letter-spacing: -0.01em;
}

.metric-desc {
    font-size: 0.75rem;
    color: #475569;
    font-weight: 500;
}

/* Custom Table Styles */
.table-container {
    background: rgba(10, 16, 32, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    backdrop-filter: blur(15px);
    overflow-x: auto;
    margin-top: 1rem;
}

.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    text-align: left;
}

.custom-table th {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    color: #64748b;
    padding: 0.85rem 1.2rem;
    border-bottom: 2px solid rgba(255, 255, 255, 0.08);
    text-transform: uppercase;
    font-size: 0.7rem;
    letter-spacing: 0.08em;
}

.custom-table td {
    padding: 1rem 1.2rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    color: #cbd5e1;
    font-weight: 500;
}

.custom-table tr:hover {
    background: rgba(0, 240, 255, 0.02);
}

.time-cell {
    font-family: 'JetBrains Mono', monospace;
    color: #38bdf8 !important;
    font-size: 0.75rem;
}

.situation-badge {
    font-weight: 600;
    color: #f1f5f9;
}

.risk-badge {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 0.7rem;
    padding: 3px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    display: inline-block;
}

.risk-high {
    background: rgba(255, 0, 85, 0.1);
    color: #ff0055;
    border: 1px solid rgba(255, 0, 85, 0.25);
    box-shadow: 0 0 10px rgba(255, 0, 85, 0.05);
}

.risk-medium {
    background: rgba(255, 183, 0, 0.1);
    color: #ffb700;
    border: 1px solid rgba(255, 183, 0, 0.25);
    box-shadow: 0 0 10px rgba(255, 183, 0, 0.05);
}

.risk-low {
    background: rgba(0, 255, 102, 0.1);
    color: #00ff66;
    border: 1px solid rgba(0, 255, 102, 0.25);
    box-shadow: 0 0 10px rgba(0, 255, 102, 0.05);
}

.score-pill {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
}

.score-pill.focus {
    background: rgba(0, 240, 255, 0.08);
    color: #00f0ff;
    border: 1px solid rgba(0, 240, 255, 0.18);
}

.score-pill.safety {
    background: rgba(168, 85, 247, 0.08);
    color: #a855f7;
    border: 1px solid rgba(168, 85, 247, 0.18);
}

.no-events {
    font-family: 'JetBrains Mono', monospace;
    color: #475569;
    padding: 2.5rem;
    text-align: center;
    border: 1px dashed rgba(255,255,255,0.06);
    border-radius: 12px;
}
</style>
"""

# Helper function to convert Hex to RGB for glow effect shadows
def hex_to_rgb(hex_str):
    h = hex_str.lstrip('#')
    return f"{int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}"

# Helper function to render a custom metric card
def render_metric_card(label, value, desc, color_theme, icon_svg):
    color_map = {
        "cyan": "#00f0ff",
        "pink": "#ff0055",
        "yellow": "#ffb700",
        "green": "#00ff66",
        "purple": "#a855f7",
        "blue": "#3b82f6"
    }
    hex_color = color_map.get(color_theme, "#00f0ff")
    shadow_color = f"rgba({hex_to_rgb(hex_color)}, 0.08)"
    
    return f"""
    <div class="metric-card" style="--accent-color: {hex_color}; --shadow-color: {shadow_color};">
        <div class="metric-header">
            <span class="metric-label">{label}</span>
            <span class="metric-icon">{icon_svg}</span>
        </div>
        <div class="metric-value" style="text-shadow: 0 0 8px {hex_color}44; color: {hex_color};">{value}</div>
        <div class="metric-desc">{desc}</div>
    </div>
    """

# Dynamic formatting maps based on situation, risk, focus, safety
def get_situation_details(situation):
    details = {
        "Distracted Walking": ("Distracted Walking", "pink", "📱"),
        "Working": ("Working", "green", "💻"),
        "Resting": ("Resting", "cyan", "🛌"),
        "Hurrying": ("Hurrying", "yellow", "🏃‍♂️"),
        "Normal Activity": ("Normal Activity", "blue", "🚶‍♂️")
    }
    return details.get(situation, (situation, "cyan", "🔎"))

def get_risk_details(risk):
    details = {
        "High": ("High Risk", "pink", "⚠️"),
        "Medium": ("Medium Risk", "yellow", "🔔"),
        "Low": ("Low Risk", "green", "✅")
    }
    return details.get(risk, (risk, "cyan", "❓"))

def get_focus_details(score):
    try:
        val = int(score)
    except:
        val = 100
    if val >= 80:
        return (f"{val}%", "green", "🎯")
    elif val >= 50:
        return (f"{val}%", "yellow", "🎯")
    else:
        return (f"{val}%", "pink", "🎯")

def get_safety_details(score):
    try:
        val = int(score)
    except:
        val = 10
    if val >= 7:
        return (f"{val}/10", "green", "🛡️")
    elif val >= 4:
        return (f"{val}/10", "yellow", "🛡️")
    else:
        return (f"{val}/10", "pink", "🛡️")

# Metrics grid HTML compiler
def render_metrics_grid(situation, risk, focus, safety):
    sit_val, sit_theme, sit_icon = get_situation_details(situation)
    risk_val, risk_theme, risk_icon = get_risk_details(risk)
    focus_val, focus_theme, focus_icon = get_focus_details(focus)
    safety_val, safety_theme, safety_icon = get_safety_details(safety)
    
    card1 = render_metric_card("Situation", sit_val, "AI Classification", sit_theme, sit_icon)
    card2 = render_metric_card("Risk Level", risk_val, "Threat Assessment", risk_theme, risk_icon)
    card3 = render_metric_card("Focus Score", focus_val, "Target Attention Index", focus_theme, focus_icon)
    card4 = render_metric_card("Safety Score", safety_val, "Environment Hazard Index", safety_theme, safety_icon)
    
    return f"""
    <div class="metrics-container">
        {card1}
        {card2}
        {card3}
        {card4}
    </div>
    """

# Live camera feed graphics generator
def render_camera_hud(situation):
    bbox_html = ""
    if situation == "Distracted Walking":
        bbox_html = """
        <div class="camera-bounding-box person" style="top: 15%; left: 30%; width: 40%; height: 75%;">
            <span class="bbox-label">PERSON [96%]</span>
        </div>
        <div class="camera-bounding-box phone" style="top: 40%; left: 45%; width: 8%; height: 12%;">
            <span class="bbox-label">PHONE [91%]</span>
        </div>
        <svg class="connection-line" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 2; pointer-events: none;">
            <line x1="50%" y1="35%" x2="49%" y2="46%" stroke="#ff0055" stroke-width="2" stroke-dasharray="4" />
        </svg>
        <div class="hud-alert-overlay">DISTRACTED BEHAVIOR DETECTED</div>
        """
    elif situation == "Working":
        bbox_html = """
        <div class="camera-bounding-box person" style="top: 20%; left: 25%; width: 45%; height: 70%; border-color: #00ff66;">
            <span class="bbox-label" style="background: #00ff66;">PERSON [98%]</span>
        </div>
        <div class="camera-bounding-box laptop" style="top: 55%; left: 40%; width: 25%; height: 30%; border-color: #00f0ff;">
            <span class="bbox-label" style="background: #00f0ff;">LAPTOP [95%]</span>
        </div>
        """
    elif situation == "Resting":
        bbox_html = """
        <div class="camera-bounding-box person" style="top: 30%; left: 20%; width: 60%; height: 60%; border-color: #3b82f6;">
            <span class="bbox-label" style="background: #3b82f6;">PERSON [92%]</span>
        </div>
        """
    elif situation == "Hurrying":
        bbox_html = """
        <div class="camera-bounding-box person" style="top: 15%; left: 15%; width: 35%; height: 75%; border-color: #ffb700; transform: skewX(-5deg);">
            <span class="bbox-label" style="background: #ffb700;">PERSON (FAST) [94%]</span>
        </div>
        <div class="camera-bounding-box bag" style="top: 45%; left: 35%; width: 15%; height: 25%; border-color: #3b82f6;">
            <span class="bbox-label" style="background: #3b82f6;">BAG [87%]</span>
        </div>
        """
    elif situation == "Normal Activity":
        bbox_html = """
        <div class="camera-bounding-box person" style="top: 15%; left: 35%; width: 30%; height: 75%; border-color: #00f0ff;">
            <span class="bbox-label" style="background: #00f0ff;">PERSON [97%]</span>
        </div>
        """
    else:
        # Waiting / Loading / Unknown
        bbox_html = """
        <div class="radar-scan">
            <div class="radar-circle-1"></div>
            <div class="radar-circle-2"></div>
            <div class="radar-circle-3"></div>
        </div>
        <div class="hud-center-msg">ACQUIRING LIVE FEED...</div>
        """

    return f"""
    <div class="camera-container">
        <div class="camera-grid"></div>
        <div class="camera-scanline"></div>
        <div class="camera-hud-corners"><span></span></div>
        <div class="camera-rec-dot">
            <span class="rec-pulse"></span>
            <span>{"REC" if situation != "Waiting..." else "STANDBY"}</span>
        </div>
        {bbox_html}
    </div>
    """

# Custom table HTML generator
def render_events_table(df):
    if df.empty:
        return "<div class='no-events'>No events recorded yet.</div>"
    
    rows_html = ""
    # Display newest first
    df_recent = df.tail(10).iloc[::-1]
    
    for idx, row in df_recent.iterrows():
        risk_class = f"risk-{str(row['risk']).lower()}"
        rows_html += f"""
        <tr>
            <td class="time-cell">{row['timestamp']}</td>
            <td><span class="situation-badge">{row['situation']}</span></td>
            <td><span class="risk-badge {risk_class}">{row['risk']}</span></td>
            <td>{row['explanation']}</td>
            <td><span class="score-pill focus">{row['focus_score']}%</span></td>
            <td><span class="score-pill safety">{row['safety_score']}/10</span></td>
        </tr>
        """
        
    return f"""
    <div class="table-container">
        <table class="custom-table">
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Situation</th>
                    <th>Risk Level</th>
                    <th>Explanation</th>
                    <th>Focus Score</th>
                    <th>Safety Score</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """

# Helper to trigger simulator event
def trigger_simulated_event(situation):
    preset = SIM_PRESETS.get(situation)
    if not preset:
        return None
    
    # Evaluate situation rules using project modules
    eval_result = evaluate_situation(preset["detections"], preset["movement"])
    sit_name = eval_result["situation"]
    risk_level = eval_result["risk"]
    
    # Generate explanation
    explanation = generate_explanation(sit_name)
    
    # Compute focus/safety scores
    scores = compute_scores(sit_name, risk_level, preset["detections"])
    
    # Create event
    event = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "situation": sit_name,
        "risk": risk_level,
        "explanation": explanation,
        "focus_score": scores["focus_score"],
        "safety_score": scores["safety_score"]
    }
    
    # Log to CSV
    log_event(event)
    return event


# Render styling first
st.markdown(clean_html(css), unsafe_allow_html=True)

# SIDEBAR CONTROL PANEL
st.sidebar.title("⚙️ System Control")
st.sidebar.markdown("---")

mode = st.sidebar.radio(
    "Monitoring Mode",
    ["🔴 LIVE MONITORING", "🛠️ SIMULATOR"],
    index=0,
    help="🔴 LIVE MONITORING reads from the physical pipeline CSV log. 🛠️ SIMULATOR auto-generates test scenarios to verify scoring & reasoning logic."
)

st.sidebar.markdown("---")

if mode == "🛠️ SIMULATOR":
    st.sidebar.subheader("Simulator Settings")
    sim_situation = st.sidebar.selectbox(
        "Active Situation",
        ["Auto Cycle", "Normal Activity", "Resting", "Working", "Hurrying", "Distracted Walking"],
        index=0
    )
    
    sim_interval = st.sidebar.slider(
        "Simulation Interval (sec)",
        min_value=2,
        max_value=10,
        value=3,
        step=1
    )
    st.sidebar.info("The simulator will log events using the actual pipeline files (rules engine, scoring, and logger modules)!")
else:
    st.sidebar.subheader("Live Status")
    st.sidebar.success("Listening for live camera feed entries...")
    st.sidebar.markdown(f"**Target Log File:** `{CSV_FILE}`")

if st.sidebar.button("🗑️ Clear Event Log"):
    if os.path.exists(CSV_FILE):
        try:
            os.remove(CSV_FILE)
            st.sidebar.success("Log cleared successfully!")
            time.sleep(1)
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()
        except Exception as e:
            st.sidebar.error(f"Error clearing log: {e}")
    else:
        st.sidebar.warning("Log file does not exist.")

# MAIN PANEL
header_html = """
<div class="header-wrapper">
    <div class="title-text">
        <span>🎥</span> AI Situational Camera Dashboard
    </div>
    <div class="system-status">
        <span class="status-dot"></span>
        <span>SYSTEM ONLINE</span>
    </div>
</div>
"""
st.markdown(clean_html(header_html), unsafe_allow_html=True)

# Create layout grid placeholders
left_col, right_col = st.columns([1.2, 0.8])

with left_col:
    st.markdown('<div class="camera-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">🎥 Live Camera Monitoring</div>', unsafe_allow_html=True)
    camera_placeholder = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)
    
    explanation_placeholder = st.empty()

with right_col:
    st.markdown('<div class="section-header">📊 Real-Time Metrics</div>', unsafe_allow_html=True)
    metrics_placeholder = st.empty()

st.markdown('<div class="section-header" style="margin-top: 2rem;">📋 Recent System Events</div>', unsafe_allow_html=True)
table_placeholder = st.empty()


# Infinite UI loop
while True:
    df = None
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
        except Exception:
            pass # Skip temporary file locks

    # Trigger simulation events if active
    if mode == "🛠️ SIMULATOR":
        current_time = time.time()
        if "last_sim_time" not in st.session_state:
            st.session_state.last_sim_time = 0
            
        if current_time - st.session_state.last_sim_time >= sim_interval:
            st.session_state.last_sim_time = current_time
            
            if sim_situation == "Auto Cycle":
                if "sim_index" not in st.session_state:
                    st.session_state.sim_index = 0
                situations_cycle = ["Normal Activity", "Resting", "Working", "Hurrying", "Distracted Walking"]
                active_sit = situations_cycle[st.session_state.sim_index]
                st.session_state.sim_index = (st.session_state.sim_index + 1) % len(situations_cycle)
            else:
                active_sit = sim_situation
                
            trigger_simulated_event(active_sit)
            
            # Reload immediately
            if os.path.exists(CSV_FILE):
                try:
                    df = pd.read_csv(CSV_FILE)
                except Exception:
                    pass

    # Update UI Components
    if df is not None and not df.empty:
        last_row = df.iloc[-1]
        
        current_situation = last_row.get("situation", "Unknown")
        current_risk = last_row.get("risk", "Unknown")
        current_focus = last_row.get("focus_score", 100)
        current_safety = last_row.get("safety_score", 10)
        current_explanation = last_row.get("explanation", "No explanation available.")
        
        # 1. Update Camera HUD view
        camera_placeholder.markdown(clean_html(render_camera_hud(current_situation)), unsafe_allow_html=True)
        
        # 2. Update Explanation Card
        explanation_html = f"""
        <div class="explanation-block">
            <div class="explanation-title">💡 Behavior Explanation</div>
            <div class="explanation-text">{current_explanation}</div>
        </div>
        """
        explanation_placeholder.markdown(clean_html(explanation_html), unsafe_allow_html=True)
        
        # 3. Update Metrics Cards Grid
        metrics_placeholder.markdown(clean_html(render_metrics_grid(current_situation, current_risk, current_focus, current_safety)), unsafe_allow_html=True)
        
        # 4. Update Event Log table
        table_placeholder.markdown(clean_html(render_events_table(df)), unsafe_allow_html=True)
    else:
        # Default Offline/Waiting State
        camera_placeholder.markdown(clean_html(render_camera_hud("Waiting...")), unsafe_allow_html=True)
        
        default_explanation_html = """
        <div class="explanation-block" style="border-left-color: #475569;">
            <div class="explanation-title">💡 Behavior Explanation</div>
            <div class="explanation-text">System is active. Waiting for camera feed or pipeline logs.</div>
        </div>
        """
        explanation_placeholder.markdown(clean_html(default_explanation_html), unsafe_allow_html=True)
        
        metrics_placeholder.markdown(clean_html(render_metrics_grid("Waiting...", "Unknown", 100, 10)), unsafe_allow_html=True)
        
        no_events_html = """
        <div class="no-events">
            📡 Waiting for camera events...<br/>
            <span style="font-size: 0.8rem; color: #475569; margin-top: 0.5rem; display: block;">
                Run the main pipeline or switch to '🛠️ Simulator' in the sidebar to generate mock data.
            </span>
        </div>
        """
        table_placeholder.markdown(clean_html(no_events_html), unsafe_allow_html=True)

    # Sleep to pace the loop
    time.sleep(1)