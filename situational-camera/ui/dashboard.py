import streamlit as st
import pandas as pd
import os
import time
import sys
import datetime
import numpy as np

# Ensure the situational-camera directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reasoning.rule_engine import evaluate_situation
from reasoning.explainer import generate_explanation, EXPLANATION_TEMPLATES
from reasoning.scorer import compute_scores
from custom_logging.event_logger import log_event
from detection.tracker import track_and_analyze_zones, reset_tracker

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
    },
    "Trespassing": {
        "detections": [{"label": "person", "bbox": [50, 150, 150, 380], "confidence": 0.94}],
        "movement": False
    },
    "Perimeter Breach": {
        "detections": [{"label": "person", "bbox": [420, 200, 520, 420], "confidence": 0.93}],
        "movement": True
    },
    "Loitering": {
        "detections": [{"label": "person", "bbox": [50, 150, 150, 380], "confidence": 0.91}],
        "movement": False
    },
    "Weapon Detected": {
        "detections": [
            {"label": "person", "bbox": [220, 100, 380, 450], "confidence": 0.96},
            {"label": "knife", "bbox": [290, 250, 340, 310], "confidence": 0.88}
        ],
        "movement": True
    },
    "Animal Intrusion": {
        "detections": [
            {"label": "animal", "bbox": [150, 220, 320, 340], "confidence": 0.91}
        ],
        "movement": True
    },
    "Vehicle Loitering": {
        "detections": [
            {"label": "motorcycle", "bbox": [400, 200, 580, 400], "confidence": 0.89}
        ],
        "movement": False
    }
}


st.set_page_config(
    page_title="AI Situational Understanding Camera",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded",
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

/* Gemini Insights Panel */
.gemini-insights-panel {
    background: rgba(25, 20, 45, 0.6);
    border-left: 4px solid #a855f7;
    padding: 1.25rem;
    border-radius: 0 16px 16px 0;
    margin-top: 1.25rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.gemini-title {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #a855f7;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

.gemini-text {
    font-size: 1.05rem;
    color: #e2e8f0;
    font-weight: 500;
    line-height: 1.5;
}

.gemini-badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-left: 0.5rem;
}

.gemini-verified {
    background: rgba(0, 255, 102, 0.1);
    color: #00ff66;
    border: 1px solid rgba(0, 255, 102, 0.25);
}

.gemini-rule-based {
    background: rgba(168, 85, 247, 0.1);
    color: #a855f7;
    border: 1px solid rgba(168, 85, 247, 0.25);
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

/* Weapon detection specific blinking animations */
@keyframes weapon-blink {
    0% { border-color: #ff0055; box-shadow: 0 0 5px rgba(255, 0, 85, 0.4); }
    100% { border-color: #ff5588; box-shadow: 0 0 20px rgba(255, 0, 85, 0.9); }
}

.weapon-alert {
    background: rgba(255, 0, 85, 0.25) !important;
    border: 2px solid #ff0055 !important;
    box-shadow: 0 0 25px rgba(255, 0, 85, 0.7) !important;
    animation: weapon-alert-pulse 0.8s infinite alternate !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1rem !important;
    color: #ffffff !important;
    font-weight: 800 !important;
}

@keyframes weapon-alert-pulse {
    0% { transform: translate(-50%, 0) scale(0.95); opacity: 0.85; }
    100% { transform: translate(-50%, 0) scale(1.05); opacity: 1; }
}

/* Floating animation for normal alerts */
@keyframes alert-float {
    0% { transform: translate(-50%, 0) translateY(0px); }
    50% { transform: translate(-50%, 0) translateY(-5px); }
    100% { transform: translate(-50%, 0) translateY(0px); }
}

/* Card hover glow and smooth zoom */
.metric-card {
    transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
}
.metric-card:hover {
    transform: translateY(-5px) scale(1.02) !important;
    box-shadow: 0 20px 40px var(--shadow-color, rgba(0, 240, 255, 0.15)) !important;
    border-color: var(--accent-color, rgba(0, 240, 255, 0.4)) !important;
}

/* Glassmorphism panel additions */
.camera-card, .table-container, .explanation-block, .gemini-insights-panel {
    background: rgba(10, 15, 30, 0.5) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.3s ease !important;
}

.camera-card:hover, .table-container:hover {
    border-color: rgba(0, 240, 255, 0.15) !important;
}

/* Pulse glow for situation cards */
.status-dot {
    box-shadow: 0 0 10px #00ff66;
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
        "Normal Activity": ("Normal Activity", "blue", "🚶‍♂️"),
        "Weapon Detected": ("Weapon Detected", "pink", "🔪"),
        "Vehicle Loitering": ("Vehicle Loitering", "yellow", "🏍️"),
        "Animal Intrusion": ("Animal Intrusion", "green", "🐈")
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
def render_metrics_grid(situation, risk, focus, safety, gemini_confidence=None):
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

# Coordinate parsing helper
def parse_coords(coords_str):
    try:
        points = []
        for pt in coords_str.split(";"):
            if not pt.strip(): continue
            x, y = map(int, pt.strip().split(","))
            points.append([x, y])
        return points
    except Exception:
        return []

def run_video_scan(video_path, active_zones, loitering_thresh):
    import cv2
    from detection.detector import detect_objects
    from detection.tracker import is_moving, reset_tracker
    
    reset_tracker()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []
        
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    
    # Sample every 0.5 seconds
    scan_skip = max(1, int(fps * 0.5)) 
    
    incidents = []
    frame_idx = 0
    
    progress_bar = st.sidebar.progress(0.0)
    progress_text = st.sidebar.empty()
    
    while cap.isOpened():
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            break
            
        detections = detect_objects(frame)
        detections = track_and_analyze_zones(detections, active_zones, loitering_threshold=loit_thresh)
        
        movement_detected = False
        for d in detections:
            if d.get("label") == "person" and "bbox" in d and "track_id" in d:
                if is_moving(d["track_id"], d["bbox"]):
                    movement_detected = True
                    break
                    
        situation_data = evaluate_situation(detections, movement_detected, frame=None)
        sit = situation_data["situation"]
        risk = situation_data["risk"]
        
        # Capture notable incidents
        if sit not in ["Normal Activity", "Waiting..."] or risk != "Low":
            timestamp_sec = frame_idx / fps
            mins = int(timestamp_sec // 60)
            secs = int(timestamp_sec % 60)
            time_str = f"{mins:02d}:{secs:02d}"
            
            incidents.append({
                "frame": frame_idx,
                "time_str": time_str,
                "situation": sit,
                "risk": risk,
                "objects": ", ".join(set(d.get("label") for d in detections if d.get("label")))
            })
            
        frame_idx += scan_skip
        
        # Update UI progress
        pct = min(1.0, frame_idx / total_frames)
        progress_bar.progress(pct)
        progress_text.text(f"Scanning: {int(pct*100)}%")
        
    cap.release()
    reset_tracker()
    progress_bar.empty()
    progress_text.empty()
    
    return incidents

# SVG zones drawing helper
def get_svg_zones_html(zones, active_alert_zone=None):
    polygons_svg = ""
    for zone_name, polygon in zones.items():
        if not polygon or len(polygon) < 3:
            continue
        pts_str = " ".join(f"{x},{y}" for x, y in polygon)
        
        if zone_name == "Restricted Zone A":
            stroke_color = "#ff0055"  # Neon Red/Pink
            fill_color = "rgba(255, 0, 85, 0.12)"
            if active_alert_zone == zone_name:
                stroke_color = "#ff0055"
                fill_color = "rgba(255, 0, 85, 0.25)"
        elif zone_name == "Perimeter Gate":
            stroke_color = "#ffb700"  # Neon Orange
            fill_color = "rgba(255, 183, 0, 0.08)"
            if active_alert_zone == zone_name:
                stroke_color = "#ffb700"
                fill_color = "rgba(255, 183, 0, 0.20)"
        else:
            stroke_color = "#00f0ff"
            fill_color = "rgba(0, 240, 255, 0.08)"
            
        dash = "stroke-dasharray='4' " if active_alert_zone == zone_name else ""
        polygons_svg += f'<polygon points="{pts_str}" style="fill:{fill_color};stroke:{stroke_color};stroke-width:2;{dash}" />'
        
        # Label text on the first node of the polygon
        x, y = polygon[0]
        polygons_svg += f'<text x="{x}" y="{y-8}" fill="{stroke_color}" font-family="Outfit" font-size="11" font-weight="600">{zone_name.upper()}</text>'
        
    return f"""
    <svg viewBox="0 0 640 480" style="position: absolute; top:0; left:0; width:100%; height:100%; z-index:2; pointer-events:none;">
        {polygons_svg}
    </svg>
    """

# Live camera feed graphics generator
def render_camera_hud(situation, zones=None):
    bbox_html = ""
    active_alert_zone = None
    
    if situation == "Trespassing" or situation == "Loitering":
        active_alert_zone = "Restricted Zone A"
    elif situation == "Perimeter Breach":
        active_alert_zone = "Perimeter Gate"
        
    zones_svg = ""
    if zones:
        zones_svg = get_svg_zones_html(zones, active_alert_zone)

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
    elif situation == "Trespassing":
        bbox_html = """
        <div class="camera-bounding-box person" style="top: 25%; left: 10%; width: 28%; height: 68%; border-color: #ff0055;">
            <span class="bbox-label" style="background: #ff0055;">INTRUDER - TRESPASSING</span>
        </div>
        <div class="hud-alert-overlay">CRITICAL BREACH: TRES-PASSING</div>
        """
    elif situation == "Perimeter Breach":
        bbox_html = """
        <div class="camera-bounding-box person" style="top: 30%; left: 68%; width: 24%; height: 65%; border-color: #ffb700;">
            <span class="bbox-label" style="background: #ffb700;">INTRUDER - BREACH</span>
        </div>
        <div class="hud-alert-overlay" style="background: rgba(255, 183, 0, 0.15); border-color: #ffb700; color: #ffb700;">PERIMETER BREACH DETECTED</div>
        """
    elif situation == "Loitering":
        bbox_html = """
        <div class="camera-bounding-box person" style="top: 25%; left: 12%; width: 28%; height: 68%; border-color: #ffb700;">
            <span class="bbox-label" style="background: #ffb700;">LOITERING [7.5s]</span>
        </div>
        <div class="hud-alert-overlay" style="background: rgba(255, 183, 0, 0.15); border-color: #ffb700; color: #ffb700;">LOITERING WARNING</div>
        """
    elif situation == "Weapon Detected":
        bbox_html = """
        <div class="camera-bounding-box person" style="top: 20%; left: 25%; width: 45%; height: 70%; border-color: #ff0055; animation: weapon-blink 0.5s infinite alternate;">
            <span class="bbox-label" style="background: #ff0055;">PERSON [96%]</span>
        </div>
        <div class="camera-bounding-box knife" style="top: 50%; left: 45%; width: 10%; height: 15%; border-color: #ff0055; animation: weapon-blink 0.5s infinite alternate;">
            <span class="bbox-label" style="background: #ff0055; color: white;">WEAPON [KNIFE] [88%]</span>
        </div>
        <div class="hud-alert-overlay weapon-alert">CRITICAL SAFETY THREAT: WEAPON DETECTED</div>
        """
    elif situation == "Animal Intrusion":
        bbox_html = """
        <div class="camera-bounding-box animal" style="top: 45%; left: 25%; width: 25%; height: 30%; border-color: #00ff66;">
            <span class="bbox-label" style="background: #00ff66; color: #020308;">ANIMAL [91%]</span>
        </div>
        <div class="hud-alert-overlay" style="background: rgba(0, 255, 102, 0.15); border-color: #00ff66; color: #00ff66; animation: alert-float 2s infinite ease-in-out;">ANIMAL INTRUSION DETECTED</div>
        """
    elif situation == "Vehicle Loitering":
        bbox_html = """
        <div class="camera-bounding-box vehicle" style="top: 40%; left: 55%; width: 35%; height: 50%; border-color: #ffb700;">
            <span class="bbox-label" style="background: #ffb700; color: #020308;">VEHICLE [89%]</span>
        </div>
        <div class="hud-alert-overlay" style="background: rgba(255, 183, 0, 0.15); border-color: #ffb700; color: #ffb700; animation: alert-float 2s infinite ease-in-out;">UNAUTHORIZED VEHICLE LOITERING</div>
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
        {zones_svg}
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
    

    # Create a dummy blank frame for the explainer and rule engine
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Evaluate situation rules using project modules (with frame for Gemini verification)
    eval_result = evaluate_situation(preset["detections"], preset["movement"], frame)

    # 1. Parse active zones from session state
    active_zones = {}
    if st.session_state.get("enable_zone_a", True):
        coords_a = st.session_state.get("coords_a_str", "30,80; 250,80; 220,400; 10,400")
        active_zones["Restricted Zone A"] = parse_coords(coords_a)
    if st.session_state.get("enable_zone_gate", True):
        coords_gate = st.session_state.get("coords_gate_str", "380,120; 600,120; 620,450; 400,450")
        active_zones["Perimeter Gate"] = parse_coords(coords_gate)
        
    loit_thresh = st.session_state.get("loitering_thresh", 5.0)

    # 2. Run spatial tracking and zone collision logic on the simulated preset detections
    sim_detections = track_and_analyze_zones(
        preset["detections"],
        active_zones,
        loitering_threshold=loit_thresh
    )

    # 3. Handle specific overrides for simulator alerts
    if situation == "Loitering":
        for det in sim_detections:
            if det.get("label") == "person":
                det["zone_info"] = {
                    "inside_zone": "Restricted Zone A",
                    "loitering_duration": 7.5,
                    "is_trespassing": True,
                    "is_perimeter_breach": False,
                    "is_loitering": True
                }
    elif situation == "Trespassing":
        for det in sim_detections:
            if det.get("label") == "person":
                det["zone_info"] = {
                    "inside_zone": "Restricted Zone A",
                    "loitering_duration": 1.2,
                    "is_trespassing": True,
                    "is_perimeter_breach": False,
                    "is_loitering": False
                }
    elif situation == "Perimeter Breach":
        for det in sim_detections:
            if det.get("label") == "person":
                det["zone_info"] = {
                    "inside_zone": "Perimeter Gate",
                    "loitering_duration": 1.5,
                    "is_trespassing": False,
                    "is_perimeter_breach": True,
                    "is_loitering": False
                }
    
    # Evaluate situation rules using project modules
    eval_result = evaluate_situation(sim_detections, preset["movement"])

    sit_name = eval_result["situation"]
    risk_level = eval_result["risk"]
    gemini_confidence = eval_result.get("confidence", None)
    

    # Generate explanation
    explanation = generate_explanation(frame, preset["detections"], sit_name, risk_level)
    
    # Compute focus/safety scores with Gemini confidence
    scores = compute_scores(sit_name, risk_level, preset["detections"], gemini_confidence)

    # Create a dummy blank frame for the explainer and generate explanation
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    explanation = generate_explanation(frame, sim_detections, sit_name, risk_level)
    
    # Compute focus/safety scores
    scores = compute_scores(sit_name, risk_level, sim_detections)
    
    # Create event
    event = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "situation": sit_name,
        "risk": risk_level,
        "explanation": explanation,
        "focus_score": scores["focus_score"],
        "safety_score": scores["safety_score"],
        "gemini_confidence": scores.get("gemini_confidence", None),
        "gemini_verified": eval_result.get("gemini_verified", False)
    }
    
    # Log to CSV
    log_event(event)
    return event


# Render styling first
st.markdown(clean_html(css), unsafe_allow_html=True)

# Initialize session states for video processing
if "video_playing" not in st.session_state:
    st.session_state.video_playing = False
if "video_frame_index" not in st.session_state:
    st.session_state.video_frame_index = 0
if "temp_video_path" not in st.session_state:
    st.session_state.temp_video_path = None
if "current_processed_frame" not in st.session_state:
    st.session_state.current_processed_frame = None
if "video_incidents" not in st.session_state:
    st.session_state.video_incidents = []
if "video_metrics_history" not in st.session_state:
    st.session_state.video_metrics_history = pd.DataFrame(columns=["Frame", "Safety Score", "Focus Score"])
if "video_scanning" not in st.session_state:
    st.session_state.video_scanning = False
if "gemini_manual_insight" not in st.session_state:
    st.session_state.gemini_manual_insight = None
if "gemini_manual_loading" not in st.session_state:
    st.session_state.gemini_manual_loading = False

# SIDEBAR CONTROL PANEL
st.sidebar.title("⚙️ System Control")
st.sidebar.markdown("---")

st.sidebar.subheader("📐 Zone Configuration")
enable_zone_a = st.sidebar.checkbox("Enable Restricted Zone A", value=True, key="enable_zone_a")
coords_a_str = "30,80; 250,80; 220,400; 10,400"
if enable_zone_a:
    coords_a_str = st.sidebar.text_input(
        "Zone A Vertices (x,y)",
        value="30,80; 250,80; 220,400; 10,400",
        help="Semicolon separated list of coordinates: x,y; x,y; ...",
        key="coords_a_str"
    )

enable_zone_gate = st.sidebar.checkbox("Enable Perimeter Gate", value=True, key="enable_zone_gate")
coords_gate_str = "380,120; 600,120; 620,450; 400,450"
if enable_zone_gate:
    coords_gate_str = st.sidebar.text_input(
        "Perimeter Gate Vertices (x,y)",
        value="380,120; 600,120; 620,450; 400,450",
        help="Semicolon separated list of coordinates: x,y; x,y; ...",
        key="coords_gate_str"
    )

loitering_thresh = st.sidebar.slider(
    "Loitering Threshold (sec)",
    min_value=1.0,
    max_value=15.0,
    value=5.0,
    step=0.5,
    key="loitering_thresh"
)

active_zones = {}
if enable_zone_a:
    active_zones["Restricted Zone A"] = parse_coords(coords_a_str)
if enable_zone_gate:
    active_zones["Perimeter Gate"] = parse_coords(coords_gate_str)

st.sidebar.markdown("---")

mode = st.sidebar.radio(
    "Monitoring Mode",
    ["🔴 LIVE MONITORING", "🛠️ SIMULATOR", "📤 UPLOAD VIDEO"],
    index=0,
    help="🔴 LIVE MONITORING reads from the physical pipeline CSV log. 🛠️ SIMULATOR auto-generates test scenarios. 📤 UPLOAD VIDEO processes an uploaded video frame-by-frame."
)

if "current_mode" not in st.session_state:
    st.session_state.current_mode = mode
elif st.session_state.current_mode != mode:
    st.session_state.current_mode = mode
    st.session_state.video_playing = False
    st.session_state.video_frame_index = 0
    reset_tracker()
    st.session_state.current_processed_frame = None
    st.session_state.video_incidents = []
    st.session_state.video_metrics_history = pd.DataFrame(columns=["Frame", "Safety Score", "Focus Score"])
    st.session_state.video_scanning = False
    st.session_state.gemini_manual_insight = None
    st.session_state.gemini_manual_loading = False

st.sidebar.markdown("---")

# Default playback config fallbacks
frame_skip = 5
enable_gemini_vision = False

if mode == "🛠️ SIMULATOR":
    st.sidebar.subheader("Simulator Settings")
    sim_situation = st.sidebar.selectbox(
        "Active Situation",
        ["Auto Cycle", "Normal Activity", "Resting", "Working", "Hurrying", "Distracted Walking", "Trespassing", "Perimeter Breach", "Loitering", "Weapon Detected", "Vehicle Loitering", "Animal Intrusion"],
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
elif mode == "📤 UPLOAD VIDEO":
    st.sidebar.subheader("Video Upload & Playback")
    uploaded_file = st.sidebar.file_uploader(
        "Select a surveillance video", 
        type=["mp4", "avi", "mov", "mkv"], 
        help="Upload a video to analyze situations and detect activities."
    )
    
    # Store video in session state
    if uploaded_file is not None:
        temp_dir = "scratch/temp_videos"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        
        if "temp_video_path" not in st.session_state or st.session_state.temp_video_path != temp_path:
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.temp_video_path = temp_path
            st.session_state.video_frame_index = 0
            st.session_state.video_playing = False
            reset_tracker()
            st.session_state.current_processed_frame = None
            st.session_state.video_incidents = []
            st.session_state.video_metrics_history = pd.DataFrame(columns=["Frame", "Safety Score", "Focus Score"])
            st.session_state.gemini_manual_insight = None
            st.session_state.gemini_manual_loading = False
            
        st.sidebar.success(f"Uploaded: {uploaded_file.name}")
        
        # 1. Scanning control
        if not st.session_state.video_incidents:
            if st.sidebar.button("🔍 Scan Video for Key Incidents", help="Perform a rapid background scan to populate the timeline."):
                st.session_state.video_incidents = run_video_scan(st.session_state.temp_video_path, active_zones, loitering_thresh)
                st.rerun()
        else:
            st.sidebar.info(f"Scan complete: {len(st.session_state.video_incidents)} incidents found.")
            if st.sidebar.button("🔄 Rescan Video"):
                st.session_state.video_incidents = []
                st.rerun()
                
        st.sidebar.markdown("---")
        st.sidebar.subheader("Playback Controls")
        
        # Playback Controls
        col1, col2, col3 = st.sidebar.columns(3)
        with col1:
            if st.button("▶️ Play"):
                st.session_state.video_playing = True
                st.rerun()
        with col2:
            if st.button("⏸️ Pause"):
                st.session_state.video_playing = False
                st.rerun()
        with col3:
            if st.button("⏹️ Reset"):
                st.session_state.video_playing = False
                st.session_state.video_frame_index = 0
                reset_tracker()
                st.session_state.current_processed_frame = None
                st.session_state.video_metrics_history = pd.DataFrame(columns=["Frame", "Safety Score", "Focus Score"])
                st.session_state.gemini_manual_insight = None
                st.session_state.gemini_manual_loading = False
                st.rerun()
                
        # Playback configuration
        playback_speed = st.sidebar.selectbox(
            "Playback Speed", 
            [0.5, 1.0, 1.5, 2.0], 
            index=1,
            help="Adjust the rendering and processing delay."
        )
        frame_skip = st.sidebar.slider(
            "Frame Skip (Speedup)", 
            min_value=1, 
            max_value=30, 
            value=5, 
            step=1, 
            help="Process every N-th frame to optimize speed and API costs."
        )
        enable_gemini_vision = st.sidebar.checkbox(
            "Enable Gemini Vision (AI)", 
            value=False, 
            help="Enable Gemini model for advanced verification and explanations (warning: uses API credits)."
        )
    else:
        st.session_state.temp_video_path = None
        st.session_state.video_playing = False
        st.session_state.current_processed_frame = None
        st.session_state.video_incidents = []
        st.session_state.video_metrics_history = pd.DataFrame(columns=["Frame", "Safety Score", "Focus Score"])
        st.session_state.gemini_manual_insight = None
        st.session_state.gemini_manual_loading = False
else:
    st.sidebar.subheader("Live Status")
    st.sidebar.success("Listening for live camera feed entries...")
    st.sidebar.markdown(f"**Target Log File:** `{CSV_FILE}`")

st.sidebar.markdown("---")

st.sidebar.markdown("---")
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
    gemini_insights_placeholder = st.empty()
    gemini_btn_placeholder = st.empty()
    timeline_placeholder = st.empty()

with right_col:
    st.markdown('<div class="section-header">📊 Real-Time Metrics</div>', unsafe_allow_html=True)
    metrics_placeholder = st.empty()
    chart_placeholder = st.empty()

st.markdown('<div class="section-header" style="margin-top: 2rem;">📋 Recent System Events</div>', unsafe_allow_html=True)
# Render static timeline jumper outside the loop to avoid StreamlitDuplicateElementId
if mode == "📤 UPLOAD VIDEO" and st.session_state.video_incidents:
    inc_options = [f"Jump to {inc['time_str']} - {inc['situation']} ({inc['risk']} Risk)" for inc in st.session_state.video_incidents]
    selected_inc_str = timeline_placeholder.selectbox(
        "📍 Jump to Incident Moment:",
        ["-- Select Flagged Moment --"] + inc_options,
        key="incident_jumper"
    )
    
    if selected_inc_str != "-- Select Flagged Moment --":
        if "last_jumped_incident" not in st.session_state or st.session_state.last_jumped_incident != selected_inc_str:
            st.session_state.last_jumped_incident = selected_inc_str
            sel_idx = inc_options.index(selected_inc_str)
            st.session_state.video_frame_index = st.session_state.video_incidents[sel_idx]["frame"]
            st.session_state.video_playing = False
            st.session_state.gemini_manual_insight = None  # Clear old manual insight
            
            # Fetch and render single frame
            import cv2
            cap = cv2.VideoCapture(st.session_state.temp_video_path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, st.session_state.video_frame_index)
            ret, frame = cap.read()
            cap.release()
            if ret:
                from detection.detector import detect_objects
                detections = detect_objects(frame)
                detections = track_and_analyze_zones(detections, active_zones, loitering_threshold=loitering_thresh)
                
                movement_detected = False
                for d in detections:
                    if d.get("label") == "person" and "bbox" in d and "track_id" in d:
                        from detection.tracker import is_moving
                        if is_moving(d["track_id"], d["bbox"]):
                            movement_detected = True
                            break
                sit_data = evaluate_situation(detections, movement_detected, frame=None)
                from ui.opencv_view import render_overlay
                output_frame = render_overlay(frame, detections, sit_data["situation"], sit_data["risk"], zones=active_zones)
                st.session_state.current_processed_frame = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB)
            st.rerun()

# Render static on-demand Gemini Vision request button outside the loop
if mode == "📤 UPLOAD VIDEO" and st.session_state.temp_video_path and not st.session_state.video_playing and st.session_state.current_processed_frame is not None:
    if gemini_btn_placeholder.button("🔮 Request On-Demand Gemini Vision Analysis", help="Audit the current paused frame using the Gemini Vision model to confirm the situation."):
        import cv2
        from detection.detector import detect_objects
        cap = cv2.VideoCapture(st.session_state.temp_video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, st.session_state.video_frame_index)
        ret, frame = cap.read()
        cap.release()
        if ret:
            with st.spinner("Analyzing frame with Gemini..."):
                detections = detect_objects(frame)
                detections = track_and_analyze_zones(detections, active_zones, loitering_threshold=loitering_thresh)
                movement_detected = False
                for d in detections:
                    if d.get("label") == "person" and "bbox" in d and "track_id" in d:
                        from detection.tracker import is_moving
                        if is_moving(d["track_id"], d["bbox"]):
                            movement_detected = True
                            break
                situation_data = evaluate_situation(detections, movement_detected, frame)
                explanation = generate_explanation(frame, detections, situation_data["situation"], situation_data["risk"])
                
                st.session_state.gemini_manual_insight = {
                    "situation": situation_data["situation"],
                    "risk": situation_data["risk"],
                    "explanation": explanation,
                    "confidence": situation_data.get("confidence", 0.5),
                    "gemini_verified": situation_data.get("gemini_verified", False)
                }
                
                # Log event
                scores = compute_scores(situation_data["situation"], situation_data["risk"], detections, situation_data.get("confidence", 0.5))
                event = {
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "situation": situation_data["situation"],
                    "risk": situation_data["risk"],
                    "explanation": explanation,
                    "focus_score": scores["focus_score"],
                    "safety_score": scores["safety_score"],
                    "gemini_confidence": scores.get("gemini_confidence", None),
                    "gemini_verified": situation_data.get("gemini_verified", False)
                }
                log_event(event)
                
                from ui.opencv_view import render_overlay
                output_frame = render_overlay(frame, detections, situation_data["situation"], situation_data["risk"], zones=active_zones)
                st.session_state.current_processed_frame = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB)
            st.rerun()

# Infinite UI loop
while True:
    df = None
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
        except Exception:
            pass # Skip temporary file locks

    # Parse active zones for UI overlay
    active_zones = {}
    if st.session_state.get("enable_zone_a", True):
        coords_a = st.session_state.get("coords_a_str", "30,80; 250,80; 220,400; 10,400")
        active_zones["Restricted Zone A"] = parse_coords(coords_a)
    if st.session_state.get("enable_zone_gate", True):
        coords_gate = st.session_state.get("coords_gate_str", "380,120; 600,120; 620,450; 400,450")
        active_zones["Perimeter Gate"] = parse_coords(coords_gate)

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
                situations_cycle = ["Normal Activity", "Resting", "Working", "Hurrying", "Distracted Walking", "Trespassing", "Perimeter Breach", "Loitering", "Weapon Detected", "Vehicle Loitering", "Animal Intrusion"]
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

    # Process video if active
    if mode == "📤 UPLOAD VIDEO" and st.session_state.get("temp_video_path") and st.session_state.get("video_playing"):
        import cv2
        from detection.detector import detect_objects
        from detection.tracker import is_moving
        
        cap = cv2.VideoCapture(st.session_state.temp_video_path)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_POS_FRAMES, st.session_state.video_frame_index)
            
            try:
                # We will process frame-by-frame inside a nested loop as long as video is playing
                while cap.isOpened() and st.session_state.get("video_playing", False):
                    # Skip frames
                    for _ in range(frame_skip - 1):
                        cap.grab()
                        st.session_state.video_frame_index += 1
                        
                    ret, frame = cap.read()
                    if not ret:
                        st.session_state.video_playing = False
                        st.session_state.video_frame_index = 0
                        break
                        
                    st.session_state.video_frame_index += 1
                    
                    # Clear manual insight on active playback
                    st.session_state.gemini_manual_insight = None
                    
                    # 1. Run detection
                    detections = detect_objects(frame)
                    
                    # 2. Track & Zone Analysis
                    loit_thresh = st.session_state.get("loitering_thresh", 5.0)
                    detections = track_and_analyze_zones(detections, active_zones, loitering_threshold=loit_thresh)
                    
                    # 3. Check movement
                    movement_detected = False
                    for detection in detections:
                        if (
                            detection.get("label") == "person"
                            and "bbox" in detection
                            and "track_id" in detection
                        ):
                            if is_moving(detection["track_id"], detection["bbox"]):
                                movement_detected = True
                                break
                    
                    # 4. Evaluate situation
                    if enable_gemini_vision:
                        situation_data = evaluate_situation(detections, movement_detected, frame)
                    else:
                        situation_data = evaluate_situation(detections, movement_detected, frame=None)
                        
                    situation = situation_data["situation"]
                    risk = situation_data["risk"]
                    gemini_confidence = situation_data.get("confidence", None)
                    
                    # 5. Generate explanation
                    if enable_gemini_vision:
                        explanation = generate_explanation(frame, detections, situation, risk)
                    else:
                        # Fallback local explanation
                        labels = [d.get("label", "object") for d in detections] if detections else []
                        det_summary = ", ".join(labels) if labels else "no notable objects"
                        
                        if "person" in labels:
                            action = "appears to be moving normally"
                            s_low = (situation or "").lower()
                            if "distract" in s_low:
                                action = "appears distracted, possibly using a phone"
                            elif "hurr" in s_low:
                                action = "is moving quickly and may be hurrying"
                            elif "rest" in s_low:
                                action = "appears stationary and resting"
                            elif "work" in s_low:
                                action = "appears engaged with a device or workstation"
                            elif "trespass" in s_low:
                                action = "has entered a highly restricted zone without authorization"
                            elif "breach" in s_low:
                                action = "has crossed the perimeter line"
                            elif "loiter" in s_low:
                                action = "has been loitering inside a restricted zone for a prolonged period"
                            explanation = f"A person {action}. Objects: {det_summary}. Risk: {risk}."
                        else:
                            explanation = f"Detected: {det_summary}. Situation: {situation}. Risk: {risk}."
                    
                    # 6. Compute scores
                    scores = compute_scores(situation, risk, detections, gemini_confidence)
                    
                    # Add to metrics history dataframe
                    new_metric = pd.DataFrame([{
                        "Frame": st.session_state.video_frame_index,
                        "Safety Score": scores["safety_score"],
                        "Focus Score": scores["focus_score"]
                    }])
                    st.session_state.video_metrics_history = pd.concat([st.session_state.video_metrics_history, new_metric]).tail(100)
                    
                    # 7. Log event to CSV
                    event = {
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "situation": situation,
                        "risk": risk,
                        "explanation": explanation,
                        "focus_score": scores["focus_score"],
                        "safety_score": scores["safety_score"],
                        "gemini_confidence": scores.get("gemini_confidence", None),
                        "gemini_verified": situation_data.get("gemini_verified", False)
                    }
                    log_event(event)
                    
                    # 8. Render overlay on the frame
                    from ui.opencv_view import render_overlay
                    output_frame = render_overlay(frame, detections, situation, risk, zones=active_zones)
                    
                    # 9. Store in session state as RGB
                    st.session_state.current_processed_frame = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB)
                    
                    # 10. Update placeholders immediately!
                    camera_placeholder.image(st.session_state.current_processed_frame, channels="RGB", use_container_width=True)
                    
                    explanation_html = f"""
                    <div class="explanation-block">
                        <div class="explanation-title">💡 Behavior Explanation</div>
                        <div class="explanation-text">{explanation}</div>
                    </div>
                    """
                    explanation_placeholder.markdown(clean_html(explanation_html), unsafe_allow_html=True)
                    
                    if gemini_confidence is not None:
                        confidence_pct = f"{float(gemini_confidence) * 100:.0f}%"
                        badge_class = "gemini-verified" if situation_data.get("gemini_verified", False) else "gemini-rule-based"
                        badge_text = "Gemini Verified" if situation_data.get("gemini_verified", False) else "Rule-Based"
                        
                        gemini_html = f"""
                        <div class="gemini-insights-panel">
                          <div class="gemini-title">
                            🔮 Gemini Insights
                            <span class="gemini-badge {badge_class}">{badge_text}</span>
                          </div>
                          <div class="gemini-text">
                            AI Confidence: {confidence_pct} | Situation confirmed by vision analysis.
                          </div>
                        </div>
                        """
                    else:
                        gemini_html = f"""
                        <div class="gemini-insights-panel">
                          <div class="gemini-title">
                            🔮 Gemini Insights
                            <span class="gemini-badge gemini-rule-based">Rule-Based</span>
                          </div>
                          <div class="gemini-text">
                            Using rule-based assessment. Enable Gemini Vision in the sidebar for AI analysis.
                          </div>
                        </div>
                        """
                    gemini_insights_placeholder.markdown(clean_html(gemini_html), unsafe_allow_html=True)
                    
                    metrics_placeholder.markdown(clean_html(render_metrics_grid(situation, risk, scores["focus_score"], scores["safety_score"], gemini_confidence)), unsafe_allow_html=True)
                    
                    # Real-time metrics history plotting
                    if not st.session_state.video_metrics_history.empty:
                        chart_df = st.session_state.video_metrics_history.set_index("Frame")
                        chart_placeholder.line_chart(chart_df)
                        
                    if os.path.exists(CSV_FILE):
                        try:
                            df_new = pd.read_csv(CSV_FILE)
                            table_placeholder.markdown(clean_html(render_events_table(df_new)), unsafe_allow_html=True)
                        except Exception:
                            pass
                            
                    # Throttling delay based on custom speed
                    time.sleep(max(0.001, 0.05 / playback_speed))
                    
            finally:
                cap.release()
                
        # Reload df to make sure external update checks work
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
        gemini_confidence = last_row.get("gemini_confidence", None)
        gemini_verified = last_row.get("gemini_verified", False)
        
        # Override values if an on-demand Gemini audit was requested on the current paused frame
        if mode == "📤 UPLOAD VIDEO" and st.session_state.gemini_manual_insight is not None:
            insight = st.session_state.gemini_manual_insight
            current_situation = insight["situation"]
            current_risk = insight["risk"]
            current_explanation = insight["explanation"]
            gemini_confidence = insight["confidence"]
            gemini_verified = insight["gemini_verified"]
            # Recalculate scores for display
            scores = compute_scores(current_situation, current_risk, None, gemini_confidence)
            current_focus = scores["focus_score"]
            current_safety = scores["safety_score"]
            
        # 1. Update Camera HUD view
        if mode == "📤 UPLOAD VIDEO":
            if "current_processed_frame" in st.session_state and st.session_state.current_processed_frame is not None:
                camera_placeholder.image(st.session_state.current_processed_frame, channels="RGB", use_container_width=True)
            else:
                camera_placeholder.markdown(clean_html(render_camera_hud("Waiting...", active_zones)), unsafe_allow_html=True)
        else:
            camera_placeholder.markdown(clean_html(render_camera_hud(current_situation, active_zones)), unsafe_allow_html=True)
        
        # 2. Update Explanation Card
        explanation_html = f"""
        <div class="explanation-block">
            <div class="explanation-title">💡 Behavior Explanation</div>
            <div class="explanation-text">{current_explanation}</div>
        </div>
        """
        explanation_placeholder.markdown(clean_html(explanation_html), unsafe_allow_html=True)
        
        # 3. Update Gemini Insights Panel
        if gemini_confidence is not None and not pd.isna(gemini_confidence):
            confidence_pct = f"{float(gemini_confidence) * 100:.0f}%"
            badge_class = "gemini-verified" if gemini_verified else "gemini-rule-based"
            badge_text = "Gemini Verified" if gemini_verified else "Rule-Based"
            
            gemini_html = f"""
            <div class="gemini-insights-panel">
                <div class="gemini-title">
                    🔮 Gemini Insights
                    <span class="gemini-badge {badge_class}">{badge_text}</span>
                </div>
                <div class="gemini-text">
                    AI Confidence: {confidence_pct} | Situation confirmed by vision analysis.
                </div>
            </div>
            """
            gemini_insights_placeholder.markdown(clean_html(gemini_html), unsafe_allow_html=True)
        else:
            gemini_html = f"""
            <div class="gemini-insights-panel">
                <div class="gemini-title">
                    🔮 Gemini Insights
                    <span class="gemini-badge gemini-rule-based">Rule-Based</span>
                </div>
                <div class="gemini-text">
                    Using rule-based assessment. Enable Gemini Vision or click "Request On-Demand Gemini Vision Analysis" for AI feedback.
                </div>
            </div>
            """
            gemini_insights_placeholder.markdown(clean_html(gemini_html), unsafe_allow_html=True)
        
        # 4. Update Metrics Cards Grid
        metrics_placeholder.markdown(clean_html(render_metrics_grid(current_situation, current_risk, current_focus, current_safety, gemini_confidence)), unsafe_allow_html=True)
        
        # Render static line chart when paused in video mode
        if mode == "📤 UPLOAD VIDEO" and not st.session_state.video_metrics_history.empty:
            chart_df = st.session_state.video_metrics_history.set_index("Frame")
            chart_placeholder.line_chart(chart_df)
            
        # 5. Update Event Log table
        table_placeholder.markdown(clean_html(render_events_table(df)), unsafe_allow_html=True)
    else:
        # Default Offline/Waiting State
        if mode == "📤 UPLOAD VIDEO":
            if "current_processed_frame" in st.session_state and st.session_state.current_processed_frame is not None:
                camera_placeholder.image(st.session_state.current_processed_frame, channels="RGB", use_container_width=True)
            else:
                camera_placeholder.markdown(clean_html(render_camera_hud("Waiting...", active_zones)), unsafe_allow_html=True)
        else:
            camera_placeholder.markdown(clean_html(render_camera_hud("Waiting...", active_zones)), unsafe_allow_html=True)
        
        default_explanation_html = """
        <div class="explanation-block" style="border-left-color: #475569;">
            <div class="explanation-title">💡 Behavior Explanation</div>
            <div class="explanation-text">System is active. Waiting for camera feed or pipeline logs.</div>
        </div>
        """
        explanation_placeholder.markdown(clean_html(default_explanation_html), unsafe_allow_html=True)
        
        default_gemini_html = """
        <div class="gemini-insights-panel" style="border-left-color: #475569;">
            <div class="gemini-title">🔮 Gemini Insights</div>
            <div class="gemini-text">System initializing. Gemini AI will provide insights when events are detected.</div>
        </div>
        """
        gemini_insights_placeholder.markdown(clean_html(default_gemini_html), unsafe_allow_html=True)
        
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