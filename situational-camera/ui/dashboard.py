import streamlit as st
import pandas as pd
import os
import time
import sys
import datetime
import numpy as np
import plotly.express as px

# Ensure the situational-camera directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reasoning.rule_engine import evaluate_situation
from reasoning.explainer import generate_explanation, EXPLANATION_TEMPLATES
from reasoning.scorer import compute_scores
from custom_logging.event_logger import log_event
from detection.tracker import track_and_analyze_zones, reset_tracker

st.set_page_config(
    page_title="SituVision AI",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

# Custom Styling (Light Modern UI with Mint/Teal Theme + Original Metrics)
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Base Styles */
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif !important;
    background-color: #f0faf8 !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.stApp {
    background-color: #f0faf8 !important;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 95% !important;
}

div[data-testid="column"] {
    padding: 0.5rem !important;
}

/* Sidebar Custom Styling - Professional Dark Theme */
[data-testid="stSidebar"] {
    background-color: #0a0e1a !important;
    color: #e2e8f0 !important;
    border-right: none !important;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
    padding-top: 1.5rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}

/* Navigation (First radio group) */
[data-testid="stSidebar"] div[role="radiogroup"]:first-of-type > label {
    padding: 10px 15px !important;
    border-radius: 8px !important;
    margin-bottom: 5px !important;
    background-color: transparent !important;
    border-left: 3px solid transparent !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    animation: slideInLeft 0.4s ease-out forwards;
    opacity: 0;
}

[data-testid="stSidebar"] div[role="radiogroup"]:first-of-type > label p {
    color: #718096 !important;
    font-weight: 500 !important;
    font-size: 14px !important;
}

[data-testid="stSidebar"] div[role="radiogroup"]:first-of-type > label:hover {
    background-color: rgba(255, 255, 255, 0.05) !important;
}

[data-testid="stSidebar"] div[role="radiogroup"]:first-of-type > label:has(input:checked) {
    background-color: rgba(0, 201, 167, 0.15) !important;
    border-left: 3px solid #00c9a7 !important;
}

[data-testid="stSidebar"] div[role="radiogroup"]:first-of-type > label:has(input:checked) p {
    color: #00c9a7 !important;
    font-weight: 600 !important;
}

/* Staggered load animation for navigation items */
[data-testid="stSidebar"] div[role="radiogroup"]:first-of-type > label:nth-child(1) { animation-delay: 0.05s; }
[data-testid="stSidebar"] div[role="radiogroup"]:first-of-type > label:nth-child(2) { animation-delay: 0.1s; }
[data-testid="stSidebar"] div[role="radiogroup"]:first-of-type > label:nth-child(3) { animation-delay: 0.15s; }
[data-testid="stSidebar"] div[role="radiogroup"]:first-of-type > label:nth-child(4) { animation-delay: 0.2s; }
[data-testid="stSidebar"] div[role="radiogroup"]:first-of-type > label:nth-child(5) { animation-delay: 0.25s; }
[data-testid="stSidebar"] div[role="radiogroup"]:first-of-type > label:nth-child(6) { animation-delay: 0.3s; }

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-10px); }
    to   { opacity: 1; transform: translateX(0); }
}

/* Hide Radio Circles */
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

/* Monitoring Mode (Second radio group) - Pill button overrides */
[data-testid="stSidebar"] div[role="radiogroup"]:nth-of-type(2) {
    background: transparent !important;
    padding: 0 !important;
}

[data-testid="stSidebar"] div[role="radiogroup"]:nth-of-type(2) > label {
    display: flex !important;
    width: 100% !important;
    padding: 12px 20px !important;
    border-radius: 8px !important;
    background-color: #1a2035 !important;
    border: 1px solid #2d3748 !important;
    margin-bottom: 10px !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    box-sizing: border-box !important;
}

[data-testid="stSidebar"] div[role="radiogroup"]:nth-of-type(2) > label p {
    color: #e2e8f0 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: 0.05em !important;
}

/* Specific Monitoring Mode Option Styling (Default State) */
[data-testid="stSidebar"] div[role="radiogroup"]:nth-of-type(2) > label:nth-of-type(1) {
    border-left: 3px solid #ef4444 !important;
}
[data-testid="stSidebar"] div[role="radiogroup"]:nth-of-type(2) > label:nth-of-type(1):hover {
    background-color: rgba(239, 68, 68, 0.15) !important;
}

[data-testid="stSidebar"] div[role="radiogroup"]:nth-of-type(2) > label:nth-of-type(2) {
    border-left: 3px solid #6c63ff !important;
}
[data-testid="stSidebar"] div[role="radiogroup"]:nth-of-type(2) > label:nth-of-type(2):hover {
    background-color: rgba(108, 99, 255, 0.15) !important;
}

[data-testid="stSidebar"] div[role="radiogroup"]:nth-of-type(2) > label:nth-of-type(3) {
    border-left: 3px solid #00c9a7 !important;
}
[data-testid="stSidebar"] div[role="radiogroup"]:nth-of-type(2) > label:nth-of-type(3):hover {
    background-color: rgba(0, 201, 167, 0.15) !important;
}

/* Hide raw emojis and add icon markers */
[data-testid="stSidebar"] label:has(input[value*="LIVE MONITORING"]) p {
    font-size: 0 !important;
}
[data-testid="stSidebar"] label:has(input[value*="LIVE MONITORING"]) p::after {
    content: "LIVE MONITORING" !important;
    font-size: 13px !important;
}

[data-testid="stSidebar"] label:has(input[value*="SIMULATOR"]) p {
    font-size: 0 !important;
}
[data-testid="stSidebar"] label:has(input[value*="SIMULATOR"]) p::after {
    content: "🔧 SIMULATOR" !important;
    font-size: 13px !important;
}

[data-testid="stSidebar"] label:has(input[value*="UPLOAD VIDEO"]) p {
    font-size: 0 !important;
}
[data-testid="stSidebar"] label:has(input[value*="UPLOAD VIDEO"]) p::after {
    content: "📤 UPLOAD VIDEO" !important;
    font-size: 13px !important;
}

/* Red pulsing dot for LIVE MONITORING button */
[data-testid="stSidebar"] label:has(input[value*="LIVE MONITORING"]) p::before {
    content: "";
    display: inline-block;
    width: 8px;
    height: 8px;
    background-color: #ef4444;
    border-radius: 50%;
    margin-right: 8px;
    animation: pulse-red 1.5s infinite ease-in-out;
    vertical-align: middle;
}

@keyframes pulse-red {
    0%, 100% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
    }
    50% {
        transform: scale(1.1);
        box-shadow: 0 0 0 6px rgba(239, 68, 68, 0);
    }
}

/* Sidebar General Button Styling */
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    border-radius: 20px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background-color: #1a2035 !important;
    color: #ffffff !important;
    border: 1px solid #2d3748 !important;
}

[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background-color: #2d3748 !important;
    border-color: #00c9a7 !important;
    color: #00c9a7 !important;
}

/* Playback Control Buttons columns (Play = Deploy theme, Pause & Reset = Stop theme) */
[data-testid="stSidebar"] div[data-testid="column"]:nth-of-type(1) button {
    background-color: #00c9a7 !important;
    color: #ffffff !important;
    border: none !important;
}
[data-testid="stSidebar"] div[data-testid="column"]:nth-of-type(1) button:hover {
    background-color: #00b395 !important;
}

[data-testid="stSidebar"] div[data-testid="column"]:nth-of-type(2) button,
[data-testid="stSidebar"] div[data-testid="column"]:nth-of-type(3) button {
    background-color: transparent !important;
    color: #ef4444 !important;
    border: 1.5px solid #ef4444 !important;
}
[data-testid="stSidebar"] div[data-testid="column"]:nth-of-type(2) button:hover,
[data-testid="stSidebar"] div[data-testid="column"]:nth-of-type(3) button:hover {
    background-color: #fef2f2 !important;
    border-color: #e53e3e !important;
    color: #e53e3e !important;
}

/* Zone Configuration Card Styling (Contiguous styling of sidebar controls) */
[data-testid="stSidebar"] h3 {
    border-top: 1px solid #2d3748 !important;
    margin-top: 25px !important;
    padding-top: 20px !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: #00c9a7 !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    background-color: #111827 !important;
    border: 1px solid #1f2937 !important;
    border-bottom: none !important;
    border-radius: 10px 10px 0 0 !important;
    padding: 12px 12px 0 12px !important;
    margin-bottom: 0 !important;
    animation: zone-glow 3s infinite !important;
}

/* Checkboxes Card Center */
[data-testid="stSidebar"] .stCheckbox {
    background-color: #111827 !important;
    border-left: 1px solid #1f2937 !important;
    border-right: 1px solid #1f2937 !important;
    padding: 6px 12px !important;
    margin-bottom: 0 !important;
    animation: zone-glow 3s infinite !important;
}

/* Text Inputs Card Center */
[data-testid="stSidebar"] .stTextInput {
    background-color: #111827 !important;
    border-left: 1px solid #1f2937 !important;
    border-right: 1px solid #1f2937 !important;
    padding: 6px 12px !important;
    margin-bottom: 0 !important;
    animation: zone-glow 3s infinite !important;
}

/* Slider Card Bottom */
[data-testid="stSidebar"] .stSlider {
    background-color: #111827 !important;
    border: 1px solid #1f2937 !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
    padding: 4px 12px 12px 12px !important;
    margin-bottom: 25px !important;
    animation: zone-glow 3s infinite !important;
}

@keyframes zone-glow {
    0%, 100% { border-color: #1f2937; }
    50%       { border-color: rgba(0, 201, 167, 0.25); }
}

/* Checkboxes customization */
[data-testid="stSidebar"] .stCheckbox label span:first-of-type {
    border: 2px solid #4a5568 !important;
    background-color: #1a2035 !important;
    border-radius: 4px !important;
    transition: all 0.15s ease !important;
    width: 16px !important;
    height: 16px !important;
}

[data-testid="stSidebar"] .stCheckbox label:has(input:checked) span:first-of-type {
    background-color: #00c9a7 !important;
    border-color: #00c9a7 !important;
}

[data-testid="stSidebar"] .stCheckbox label p {
    color: #e2e8f0 !important;
    font-size: 13px !important;
}

/* Text Inputs (Vertices coordinates inputs) */
[data-testid="stSidebar"] .stTextInput label {
    color: #718096 !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    margin-bottom: 4px !important;
}

[data-testid="stSidebar"] .stTextInput input {
    background-color: #1a2035 !important;
    border: 1px solid #2d3748 !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-family: monospace !important;
    transition: all 0.2s ease !important;
    padding: 8px 12px !important;
}

[data-testid="stSidebar"] .stTextInput input:focus {
    border-color: #00c9a7 !important;
    box-shadow: 0 0 0 3px rgba(0,201,167,0.15) !important;
}

/* Slider (Loitering Threshold) customization */
[data-testid="stSidebar"] .stSlider [data-testid="stWidgetLabel"] label {
    color: #00c9a7 !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] > div {
    background-color: #2d3748 !important; /* rail track */
}

[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] > div > div {
    background-color: #00c9a7 !important; /* active range fill */
}

[data-testid="stSidebar"] .stSlider div[role="slider"] {
    background-color: #00c9a7 !important;
    border: 2px solid #ffffff !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}

[data-testid="stSidebar"] .stSlider div[role="slider"]:hover {
    transform: scale(1.15) !important;
    box-shadow: 0 0 8px rgba(0, 201, 167, 0.4) !important;
}

[data-testid="stSidebar"] .stSlider div[role="slider"]:focus,
[data-testid="stSidebar"] .stSlider div[role="slider"]:active {
    animation: thumb-pop 0.3s ease-out !important;
}

@keyframes thumb-pop {
    0%   { transform: scale(1); }
    50%  { transform: scale(1.3); }
    100% { transform: scale(1); }
}

/* Clear Event Log Button customization */
[data-testid="stSidebar"] div.element-container:has(~ .logout-anchor):not(:has(~ div.stButton)) button {
    width: 100% !important;
    background-color: transparent !important;
    border: 1px solid #e53e3e !important;
    color: #e53e3e !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 15px !important;
    transition: all 0.2s ease !important;
}

[data-testid="stSidebar"] div.element-container:has(~ .logout-anchor):not(:has(~ div.stButton)) button:hover {
    background-color: #e53e3e !important;
    color: #ffffff !important;
}

[data-testid="stSidebar"] div.element-container:has(~ .logout-anchor):not(:has(~ div.stButton)) button:active {
    transform: scale(0.97) !important;
}

/* Logout Button */
.logout-anchor { display: none; }
.logout-anchor + div.stButton > button {
    background-color: transparent !important;
    border: 1.5px solid #ef4444 !important;
    color: #ef4444 !important;
    border-radius: 20px !important;
    padding: 10px 15px !important;
    width: 100% !important;
    box-shadow: none !important;
}
.logout-anchor + div.stButton > button p {
    color: #ef4444 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}
.logout-anchor + div.stButton > button:hover {
    background-color: #fef2f2 !important;
}

/* Top Header */
.top-header {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    padding: 10px 0 !important;
    margin-bottom: 20px !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05) !important;
}

.search-bar {
    background-color: #ffffff !important;
    border: 1px solid rgba(0,0,0,0.1) !important;
    border-radius: 20px !important;
    padding: 8px 20px !important;
    width: 300px !important;
    color: #1a1a1a !important;
    font-size: 0.9rem !important;
    outline: none !important;
    transition: border-color 0.2s ease !important;
}

.search-bar:focus {
    border-color: #00c9a7 !important;
}

.notification-bell {
    position: relative !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 40px !important;
    height: 40px !important;
    background: #ffffff !important;
    border-radius: 50% !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
}

.notification-dot {
    position: absolute !important;
    top: 2px !important;
    right: 2px !important;
    background-color: #ef4444 !important;
    color: white !important;
    border-radius: 50% !important;
    width: 16px !important;
    height: 16px !important;
    font-size: 10px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-weight: bold !important;
    box-shadow: 0 0 0 2px #ffffff !important;
}

/* Authentication Page */
.auth-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 80vh;
}
.auth-box {
    background: white;
    padding: 3rem;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    text-align: center;
}

/* Camera Card / Main panels */
.camera-card {
    background-color: #ffffff !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    border: 1px solid rgba(0,0,0,0.05) !important;
    margin-bottom: 1.25rem !important;
}

.camera-card h4 {
    margin-top: 0 !important;
    margin-bottom: 15px !important;
    font-weight: 700 !important;
    color: #1a1a1a !important;
}

/* Live Camera Feed Panel */
.camera-container {
    background-color: #0d1117 !important;
    border-radius: 16px !important;
    box-shadow: inset 0 0 0 2px #00c9a7, 0 8px 24px rgba(0,0,0,0.15) !important;
    border: none !important;
    position: relative !important;
    overflow: hidden !important;
    height: 380px !important;
}

/* Pulsing REC badge */
.camera-container > div:first-of-type {
    background-color: #ef4444 !important;
    color: #ffffff !important;
    padding: 4px 12px !important;
    border-radius: 20px !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    animation: rec-badge-pulse 1s infinite ease-in-out !important;
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.4) !important;
}

@keyframes rec-badge-pulse {
    0% { opacity: 0.6; }
    50% { opacity: 1; }
    100% { opacity: 0.6; }
}

/* Real-Time Metrics Layout */
.metrics-container {
    display: grid !important;
    grid-template-columns: repeat(2, 1fr) !important;
    gap: 1.2rem !important;
}

.metric-card {
    background-color: #ffffff !important;
    border-radius: 12px !important;
    padding: 1.25rem !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08) !important;
    border-left: 4px solid var(--accent-color, #00c9a7) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards, value-flash 1s ease-out;
    opacity: 0;
    position: relative;
    overflow: hidden;
}

.metric-card:hover {
    transform: scale(1.02) !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.12) !important;
}

.metric-header {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    margin-bottom: 0.25rem !important;
}

.metric-label {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    color: #888888 !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
}

.metric-value {
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    color: #1a1a1a !important;
    margin: 0.5rem 0 !important;
}

.metric-desc {
    font-size: 0.75rem !important;
    color: #888888 !important;
    font-weight: 500 !important;
}

/* Staggered load animation */
.metrics-container .metric-card:nth-child(1) { animation-delay: 0s; }
.metrics-container .metric-card:nth-child(2) { animation-delay: 0.15s; }
.metrics-container .metric-card:nth-child(3) { animation-delay: 0.3s; }
.metrics-container .metric-card:nth-child(4) { animation-delay: 0.45s; }

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(15px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Metric Value Change Highlight Transition */
@keyframes value-flash {
    0% { background-color: #fffbeb; }
    100% { background-color: #ffffff; }
}

/* Behavior Explanation Block */
.explanation-block {
    background-color: #ffffff !important;
    border-left: 4px solid #00c9a7 !important;
    padding: 1.25rem !important;
    border-radius: 0 16px 16px 0 !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    margin-top: 1.25rem !important;
    animation: fadeIn 0.4s ease-out forwards;
}

.explanation-title {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    color: #888888 !important;
    font-weight: 700 !important;
    margin-bottom: 0.25rem !important;
}

.explanation-text {
    font-size: 1.05rem !important;
    color: #1a1a1a !important;
    font-weight: 500 !important;
    font-style: italic !important;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* Events Table Design */
.table-container {
    background-color: #ffffff !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    border: 1px solid rgba(0,0,0,0.05) !important;
    margin-top: 1.5rem !important;
}

.custom-table {
    width: 100% !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
    font-size: 0.85rem !important;
}

.custom-table th {
    color: #64748b !important;
    padding: 1rem 1.2rem !important;
    border-bottom: 2px solid #e2e8f0 !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em !important;
}

.custom-table td {
    padding: 1rem 1.2rem !important;
    border-bottom: 1px solid #f1f5f9 !important;
    color: #334155 !important;
    font-weight: 500 !important;
    transition: background-color 0.2s ease !important;
}

/* Alternating rows styling */
.custom-table tbody tr:nth-child(even) td {
    background-color: #f8fafc !important;
}

/* Row Hover state */
.custom-table tbody tr:hover td {
    background-color: #f1f5f9 !important;
}

/* Risk badge styled as pills */
.risk-badge {
    display: inline-block !important;
    padding: 4px 12px !important;
    border-radius: 20px !important;
    font-weight: 700 !important;
    font-size: 0.75rem !important;
    text-align: center !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    border: none !important;
}

.risk-low {
    background-color: #d4edda !important;
    color: #155724 !important;
}

.risk-medium {
    background-color: #fff3cd !important;
    color: #856404 !important;
}

.risk-high {
    background-color: #f8d7da !important;
    color: #721c24 !important;
}

.time-cell {
    color: #00c9a7 !important;
    font-weight: 600 !important;
}

.situation-badge {
    background-color: #f1f5f9 !important;
    color: #475569 !important;
    padding: 4px 10px !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.75rem !important;
}

.score-pill {
    display: inline-block !important;
    padding: 4px 10px !important;
    border-radius: 20px !important;
    font-weight: 700 !important;
    font-size: 0.75rem !important;
}

.score-pill.focus {
    background-color: #e0f2fe !important;
    color: #0369a1 !important;
}

.score-pill.safety {
    background-color: #f3e8ff !important;
    color: #6b21a8 !important;
}

/* Custom developer wrappers for Deploy/Stop buttons */
.deploy-btn div.stButton > button {
    background-color: #00c9a7 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 20px !important;
    font-weight: 600 !important;
    padding: 8px 24px !important;
}
.deploy-btn div.stButton > button:hover {
    background-color: #00b395 !important;
}

.stop-btn div.stButton > button {
    background-color: transparent !important;
    color: #ef4444 !important;
    border: 1.5px solid #ef4444 !important;
    border-radius: 20px !important;
    font-weight: 600 !important;
    padding: 8px 24px !important;
}
.stop-btn div.stButton > button:hover {
    background-color: #fef2f2 !important;
    border-color: #e53e3e !important;
    color: #e53e3e !important;
}
</style>
"""

def clean_html(html_str):
    return "\n".join(line.strip() for line in html_str.split("\n") if line.strip())

def hex_to_rgb(hex_str):
    h = hex_str.lstrip('#')
    return f"{int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}"

def render_metric_card(label, value, desc, color_theme, icon_svg):
    color_map = {
        "cyan": "#128292",
        "pink": "#ef4444",
        "yellow": "#f59e0b",
        "green": "#10b981",
        "purple": "#a855f7",
        "blue": "#3b82f6"
    }
    hex_color = color_map.get(color_theme, "#128292")
    
    return f"""
    <div class="metric-card" style="--accent-color: {hex_color};">
        <div class="metric-header">
            <span class="metric-label">{label}</span>
            <span class="metric-icon" style="color: {hex_color}">{icon_svg}</span>
        </div>
        <div class="metric-value">{value}</div>
        <div class="metric-desc">{desc}</div>
    </div>
    """

def get_situation_details(situation):
    details = {
        "Distracted Walking": ("Distracted Walking", "pink", "📱"),
        "Working": ("Working", "green", "💻"),
        "Resting": ("Resting", "cyan", "🛋️"),
        "Hurrying": ("Hurrying", "yellow", "🏃‍♂️"),
        "Normal Activity": ("Normal Activity", "blue", "🚶‍♂️"),
        "Weapon Detected": ("Weapon Detected", "pink", "🔪"),
        "Vehicle Loitering": ("Vehicle Loitering", "yellow", "🏎️"),
        "Animal Intrusion": ("Animal Intrusion", "green", "🐈")
    }
    return details.get(situation, (situation, "cyan", "🔍"))

def get_risk_details(risk):
    details = {
        "High": ("High Risk", "pink", "⚠️"),
        "Medium": ("Medium Risk", "yellow", "👀"),
        "Low": ("Low Risk", "green", "✅")
    }
    return details.get(risk, (risk, "cyan", "❔"))

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
        pct = min(1.0, frame_idx / total_frames)
        progress_bar.progress(pct)
        progress_text.text(f"Scanning: {int(pct*100)}%")
        
    cap.release()
    reset_tracker()
    progress_bar.empty()
    progress_text.empty()
    
    return incidents

def get_svg_zones_html(zones, active_alert_zone=None):
    polygons_svg = ""
    for zone_name, polygon in zones.items():
        if not polygon or len(polygon) < 3:
            continue
        pts_str = " ".join(f"{x},{y}" for x, y in polygon)
        
        if zone_name == "Restricted Zone A":
            stroke_color = "#ef4444" 
            fill_color = "rgba(239, 68, 68, 0.12)"
            if active_alert_zone == zone_name:
                fill_color = "rgba(239, 68, 68, 0.25)"
        elif zone_name == "Perimeter Gate":
            stroke_color = "#f59e0b"
            fill_color = "rgba(245, 158, 11, 0.08)"
            if active_alert_zone == zone_name:
                fill_color = "rgba(245, 158, 11, 0.20)"
        else:
            stroke_color = "#128292"
            fill_color = "rgba(18, 130, 146, 0.08)"
            
        dash = "stroke-dasharray='4' " if active_alert_zone == zone_name else ""
        polygons_svg += f'<polygon points="{pts_str}" style="fill:{fill_color};stroke:{stroke_color};stroke-width:2;{dash}" />'
        
        x, y = polygon[0]
        polygons_svg += f'<text x="{x}" y="{y-8}" fill="{stroke_color}" font-family="Inter" font-size="11" font-weight="600">{zone_name.upper()}</text>'
        
    return f"""
    <svg viewBox="0 0 640 480" style="position: absolute; top:0; left:0; width:100%; height:100%; z-index:2; pointer-events:none;">
        {polygons_svg}
    </svg>
    """

def render_camera_hud(situation, zones=None):
    active_alert_zone = None
    if situation == "Trespassing" or situation == "Loitering":
        active_alert_zone = "Restricted Zone A"
    elif situation == "Perimeter Breach":
        active_alert_zone = "Perimeter Gate"
        
    zones_svg = ""
    if zones:
        zones_svg = get_svg_zones_html(zones, active_alert_zone)

    return f"""
    <div class="camera-container">
        <div style="position:absolute; top:10px; right:10px; background:#ef4444; color:white; padding:2px 8px; border-radius:4px; font-size:0.7rem; font-weight:bold; z-index:5;">● {"REC" if situation != "Waiting..." else "STANDBY"}</div>
        {zones_svg}
    </div>
    """

def render_events_table(df):
    if df.empty:
        return "<div class='no-events'>No events recorded yet.</div>"
    
    rows_html = ""
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

def trigger_simulated_event(situation):
    preset = SIM_PRESETS.get(situation)
    if not preset:
        return None
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    active_zones = {}
    if st.session_state.get("enable_zone_a", True):
        active_zones["Restricted Zone A"] = parse_coords(st.session_state.get("coords_a_str", "30,80; 250,80; 220,400; 10,400"))
    if st.session_state.get("enable_zone_gate", True):
        active_zones["Perimeter Gate"] = parse_coords(st.session_state.get("coords_gate_str", "380,120; 600,120; 620,450; 400,450"))
        
    loit_thresh = st.session_state.get("loitering_thresh", 5.0)
    sim_detections = track_and_analyze_zones(preset["detections"], active_zones, loitering_threshold=loit_thresh)

    if situation == "Loitering":
        for det in sim_detections:
            if det.get("label") == "person":
                det["zone_info"] = {"inside_zone": "Restricted Zone A", "loitering_duration": 7.5, "is_trespassing": True, "is_perimeter_breach": False, "is_loitering": True}
    elif situation == "Trespassing":
        for det in sim_detections:
            if det.get("label") == "person":
                det["zone_info"] = {"inside_zone": "Restricted Zone A", "loitering_duration": 1.2, "is_trespassing": True, "is_perimeter_breach": False, "is_loitering": False}
    elif situation == "Perimeter Breach":
        for det in sim_detections:
            if det.get("label") == "person":
                det["zone_info"] = {"inside_zone": "Perimeter Gate", "loitering_duration": 1.5, "is_trespassing": False, "is_perimeter_breach": True, "is_loitering": False}
    
    eval_result = evaluate_situation(sim_detections, preset["movement"])
    sit_name = eval_result["situation"]
    risk_level = eval_result["risk"]
    gemini_confidence = eval_result.get("confidence", None)
    
    explanation = generate_explanation(frame, sim_detections, sit_name, risk_level)
    scores = compute_scores(sit_name, risk_level, sim_detections, gemini_confidence)
    
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
    
    log_event(event)
    return event

# Authentication logic
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None

def login_page():
    st.markdown(clean_html(css), unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown('<div class="auth-container"><div class="auth-box">', unsafe_allow_html=True)
        st.markdown('<h1 style="color:#128292; font-weight:800; margin-bottom: 5px;">SituVision AI</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color:#64748b; margin-bottom: 30px;">Sign in to your account</p>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin or user")
            password = st.text_input("Password", type="password", placeholder="password")
            submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit:
                if username and password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_role = "Admin" if username.lower() == "admin" else "User"
                    st.rerun()
                else:
                    st.error("Please enter both username and password.")
                    
        st.markdown('</div></div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    login_page()
    st.stop()

# Initialize session states for video processing
if "video_playing" not in st.session_state: st.session_state.video_playing = False
if "video_frame_index" not in st.session_state: st.session_state.video_frame_index = 0
if "temp_video_path" not in st.session_state: st.session_state.temp_video_path = None
if "current_processed_frame" not in st.session_state: st.session_state.current_processed_frame = None
if "video_incidents" not in st.session_state: st.session_state.video_incidents = []
if "video_metrics_history" not in st.session_state: st.session_state.video_metrics_history = pd.DataFrame(columns=["Frame", "Safety Score", "Focus Score"])
if "gemini_manual_insight" not in st.session_state: st.session_state.gemini_manual_insight = None

st.markdown(clean_html(css), unsafe_allow_html=True)

# SIDEBAR CONTROL PANEL
st.sidebar.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; padding-top: 10px;">
        <div style="display:flex; align-items:center; gap: 8px;">
            <span style="color:#008744; font-size:26px;">🌿</span>
            <span style="font-weight:700; font-size:20px; color:#0f172a;">SituVision</span>
        </div>
        <span style="color:#64748b; font-weight: bold; cursor:pointer;">&lt;</span>
    </div>
    <hr style="margin: 15px 0; border: none; border-top: 1px solid #e2e8f0;">
""", unsafe_allow_html=True)

# User Profile Area at the top
st.sidebar.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom: 5px;">
        <div style="width:42px; height:42px; border-radius:50%; background:#347c2c; color:white; display:flex; align-items:center; justify-content:center; font-weight:600; font-size: 18px;">
            {st.session_state.username[0].upper() if st.session_state.username else 'U'}
        </div>
        <div style="line-height: 1.2;">
            <div style="font-weight:600; font-size:15px; color:#1e293b;">{st.session_state.username.title() if st.session_state.username else 'User'}</div>
            <div style="font-size:13px; color:#64748b;">{st.session_state.user_role if st.session_state.user_role else 'Role'}</div>
        </div>
    </div>
    <hr style="margin: 15px 0 10px 0; border: none; border-top: 1px solid #e2e8f0;">
""", unsafe_allow_html=True)

# Styled Navigation Options
pages_map = {
    "㗊 Dashboard": "Dashboard",
    "📷 Cameras": "Cameras",
    "📈 Analytics": "Analytics",
    "📅 Events": "Events",
    "📑 Reports": "Reports",
    "⚙️ Settings": "Settings"
}
pages = list(pages_map.keys())
selection_raw = st.sidebar.radio("Navigation", pages, label_visibility="collapsed")
selection = pages_map[selection_raw]

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Keep Pipeline Controls below the navigation
st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color:#0b3d45; font-size:14px;'>⚙️ PIPELINE CONTROLS</h3>", unsafe_allow_html=True)

mode = st.sidebar.radio("Monitoring Mode", ["🔴 LIVE MONITORING", "🛠️ SIMULATOR", "📤 UPLOAD VIDEO"], index=0)

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
    st.session_state.gemini_manual_insight = None

st.sidebar.subheader("📐 Zone Configuration")
enable_zone_a = st.sidebar.checkbox("Enable Restricted Zone A", value=True, key="enable_zone_a")
coords_a_str = st.sidebar.text_input("Zone A Vertices (x,y)", value="30,80; 250,80; 220,400; 10,400", key="coords_a_str") if enable_zone_a else ""

enable_zone_gate = st.sidebar.checkbox("Enable Perimeter Gate", value=True, key="enable_zone_gate")
coords_gate_str = st.sidebar.text_input("Perimeter Gate Vertices (x,y)", value="380,120; 600,120; 620,450; 400,450", key="coords_gate_str") if enable_zone_gate else ""

loitering_thresh = st.sidebar.slider("Loitering Threshold (sec)", min_value=1.0, max_value=15.0, value=5.0, step=0.5, key="loitering_thresh")

active_zones = {}
if enable_zone_a: active_zones["Restricted Zone A"] = parse_coords(coords_a_str)
if enable_zone_gate: active_zones["Perimeter Gate"] = parse_coords(coords_gate_str)

frame_skip = 5
enable_gemini_vision = False

if mode == "🛠️ SIMULATOR":
    st.sidebar.subheader("Simulator Settings")
    sim_situation = st.sidebar.selectbox("Active Situation", ["Auto Cycle", "Normal Activity", "Resting", "Working", "Hurrying", "Distracted Walking", "Trespassing", "Perimeter Breach", "Loitering", "Weapon Detected", "Vehicle Loitering", "Animal Intrusion"], index=0)
    sim_interval = st.sidebar.slider("Simulation Interval (sec)", 2, 10, 3)
elif mode == "📤 UPLOAD VIDEO":
    st.sidebar.subheader("Video Upload & Playback")
    uploaded_file = st.sidebar.file_uploader("Select a surveillance video", type=["mp4", "avi", "mov", "mkv"])
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
            
        if not st.session_state.video_incidents:
            if st.sidebar.button("🔍 Scan Video for Key Incidents"):
                st.session_state.video_incidents = run_video_scan(st.session_state.temp_video_path, active_zones, loitering_thresh)
                st.rerun()
        else:
            if st.sidebar.button("🔄 Rescan Video"):
                st.session_state.video_incidents = []
                st.rerun()
                
        col1, col2, col3 = st.sidebar.columns(3)
        if col1.button("▶️ Play"):
            st.session_state.video_playing = True
            st.rerun()
        if col2.button("⏸️ Pause"):
            st.session_state.video_playing = False
            st.rerun()
        if col3.button("⏹️ Reset"):
            st.session_state.video_playing = False
            st.session_state.video_frame_index = 0
            st.session_state.video_metrics_history = pd.DataFrame(columns=["Frame", "Safety Score", "Focus Score"])
            st.session_state.current_processed_frame = None
            st.rerun()
            
        playback_speed = st.sidebar.selectbox("Playback Speed", [0.5, 1.0, 1.5, 2.0], index=1)
        frame_skip = st.sidebar.slider("Frame Skip", 1, 30, 5)
        enable_gemini_vision = st.sidebar.checkbox("Enable Gemini Vision (AI)", value=False)
    else:
        st.session_state.temp_video_path = None
        st.session_state.video_playing = False

if st.sidebar.button("🗑️ Clear Event Log"):
    if os.path.exists(CSV_FILE): os.remove(CSV_FILE)
    st.rerun()

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.markdown('<hr style="margin: 10px 0; border: none; border-top: 1px solid #e2e8f0;">', unsafe_allow_html=True)
st.sidebar.markdown('<div class="logout-anchor"></div>', unsafe_allow_html=True)
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()

# Top Header
header_html = f"""
<div class="top-header">
    <h2 style="margin:0; color:#0f172a; font-weight:700;">{selection}</h2>
    <div style="display:flex; align-items:center; gap:20px;">
        <input type="text" class="search-bar" placeholder="🔍 Global Search">
        <div class="notification-bell">
            <span style="font-size:1.2rem;">🔔</span>
            <div class="notification-dot">3</div>
        </div>
    </div>
</div>
"""
st.markdown(clean_html(header_html), unsafe_allow_html=True)

# Main Application Logic
if selection == "Dashboard":
    # Layout definition
    left_col, right_col = st.columns([1.2, 0.8])
    with left_col:
        st.markdown('<div class="camera-card">', unsafe_allow_html=True)
        st.markdown('<h4 style="margin:0 0 10px 0; color:#0f172a;">Live Camera Monitoring</h4>', unsafe_allow_html=True)
        camera_placeholder = st.empty()
        st.markdown('</div>', unsafe_allow_html=True)
        explanation_placeholder = st.empty()
        gemini_insights_placeholder = st.empty()
        gemini_btn_placeholder = st.empty()
        timeline_placeholder = st.empty()
        
    with right_col:
        metrics_placeholder = st.empty()
        st.markdown('<br>', unsafe_allow_html=True)
        chart_placeholder = st.empty()
        
    table_placeholder = st.empty()

    if mode == "📤 UPLOAD VIDEO" and st.session_state.video_incidents:
        inc_options = [f"Jump to {inc['time_str']} - {inc['situation']} ({inc['risk']} Risk)" for inc in st.session_state.video_incidents]
        selected_inc_str = timeline_placeholder.selectbox("📍 Jump to Incident Moment:", ["-- Select Flagged Moment --"] + inc_options)
        if selected_inc_str != "-- Select Flagged Moment --":
            if "last_jumped_incident" not in st.session_state or st.session_state.last_jumped_incident != selected_inc_str:
                st.session_state.last_jumped_incident = selected_inc_str
                sel_idx = inc_options.index(selected_inc_str)
                st.session_state.video_frame_index = st.session_state.video_incidents[sel_idx]["frame"]
                st.session_state.video_playing = False
                st.session_state.gemini_manual_insight = None
                
                import cv2
                cap = cv2.VideoCapture(st.session_state.temp_video_path)
                cap.set(cv2.CAP_PROP_POS_FRAMES, st.session_state.video_frame_index)
                ret, frame = cap.read()
                cap.release()
                if ret:
                    from detection.detector import detect_objects
                    from detection.tracker import is_moving
                    detections = detect_objects(frame)
                    detections = track_and_analyze_zones(detections, active_zones, loitering_threshold=loitering_thresh)
                    movement_detected = False
                    for d in detections:
                        if d.get("label") == "person" and "bbox" in d and "track_id" in d:
                            if is_moving(d["track_id"], d["bbox"]):
                                movement_detected = True; break
                    sit_data = evaluate_situation(detections, movement_detected, frame=None)
                    from ui.opencv_view import render_overlay
                    output_frame = render_overlay(frame, detections, sit_data["situation"], sit_data["risk"], zones=active_zones)
                    st.session_state.current_processed_frame = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB)
                st.rerun()

    if mode == "📤 UPLOAD VIDEO" and st.session_state.temp_video_path and not st.session_state.video_playing and st.session_state.current_processed_frame is not None:
        if gemini_btn_placeholder.button("🔮 Request On-Demand Gemini Vision Analysis"):
            import cv2
            from detection.detector import detect_objects
            from detection.tracker import is_moving
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
                            if is_moving(d["track_id"], d["bbox"]):
                                movement_detected = True; break
                    situation_data = evaluate_situation(detections, movement_detected, frame)
                    explanation = generate_explanation(frame, detections, situation_data["situation"], situation_data["risk"])
                    st.session_state.gemini_manual_insight = {
                        "situation": situation_data["situation"], "risk": situation_data["risk"], 
                        "explanation": explanation, "confidence": situation_data.get("confidence", 0.5), 
                        "gemini_verified": situation_data.get("gemini_verified", False)
                    }
                    scores = compute_scores(situation_data["situation"], situation_data["risk"], detections, situation_data.get("confidence", 0.5))
                    event = {
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "situation": situation_data["situation"], "risk": situation_data["risk"],
                        "explanation": explanation, "focus_score": scores["focus_score"], "safety_score": scores["safety_score"],
                        "gemini_confidence": scores.get("gemini_confidence", None), "gemini_verified": situation_data.get("gemini_verified", False)
                    }
                    log_event(event)
                    from ui.opencv_view import render_overlay
                    output_frame = render_overlay(frame, detections, situation_data["situation"], situation_data["risk"], zones=active_zones)
                    st.session_state.current_processed_frame = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB)
                st.rerun()

    # Core Logic Loop (only runs when Dashboard tab is open)
    while True:
        df = None
        if os.path.exists(CSV_FILE):
            try:
                df = pd.read_csv(CSV_FILE)
            except Exception:
                pass

        if mode == "🛠️ SIMULATOR":
            current_time = time.time()
            if "last_sim_time" not in st.session_state: st.session_state.last_sim_time = 0
            if current_time - st.session_state.last_sim_time >= sim_interval:
                st.session_state.last_sim_time = current_time
                if sim_situation == "Auto Cycle":
                    if "sim_index" not in st.session_state: st.session_state.sim_index = 0
                    situations_cycle = ["Normal Activity", "Resting", "Working", "Hurrying", "Distracted Walking", "Trespassing", "Perimeter Breach", "Loitering", "Weapon Detected", "Vehicle Loitering", "Animal Intrusion"]
                    active_sit = situations_cycle[st.session_state.sim_index]
                    st.session_state.sim_index = (st.session_state.sim_index + 1) % len(situations_cycle)
                else:
                    active_sit = sim_situation
                trigger_simulated_event(active_sit)
                if os.path.exists(CSV_FILE):
                    try: df = pd.read_csv(CSV_FILE)
                    except Exception: pass

        if mode == "📤 UPLOAD VIDEO" and st.session_state.get("temp_video_path") and st.session_state.get("video_playing"):
            import cv2
            from detection.detector import detect_objects
            from detection.tracker import is_moving
            cap = cv2.VideoCapture(st.session_state.temp_video_path)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_POS_FRAMES, st.session_state.video_frame_index)
                try:
                    while cap.isOpened() and st.session_state.get("video_playing", False):
                        for _ in range(frame_skip - 1):
                            cap.grab()
                            st.session_state.video_frame_index += 1
                        ret, frame = cap.read()
                        if not ret:
                            st.session_state.video_playing = False
                            st.session_state.video_frame_index = 0
                            break
                        st.session_state.video_frame_index += 1
                        st.session_state.gemini_manual_insight = None
                        
                        detections = detect_objects(frame)
                        detections = track_and_analyze_zones(detections, active_zones, loitering_threshold=loitering_thresh)
                        movement_detected = False
                        for detection in detections:
                            if detection.get("label") == "person" and "bbox" in detection and "track_id" in detection:
                                if is_moving(detection["track_id"], detection["bbox"]):
                                    movement_detected = True; break
                                    
                        situation_data = evaluate_situation(detections, movement_detected, frame if enable_gemini_vision else None)
                        situation = situation_data["situation"]
                        risk = situation_data["risk"]
                        gemini_confidence = situation_data.get("confidence", None)
                        
                        if enable_gemini_vision:
                            explanation = generate_explanation(frame, detections, situation, risk)
                        else:
                            labels = [d.get("label", "object") for d in detections] if detections else []
                            det_summary = ", ".join(labels) if labels else "no notable objects"
                            explanation = f"Detected: {det_summary}. Situation: {situation}. Risk: {risk}."
                        
                        scores = compute_scores(situation, risk, detections, gemini_confidence)
                        new_metric = pd.DataFrame([{"Frame": st.session_state.video_frame_index, "Safety Score": scores["safety_score"], "Focus Score": scores["focus_score"]}])
                        st.session_state.video_metrics_history = pd.concat([st.session_state.video_metrics_history, new_metric]).tail(100)
                        
                        event = {
                            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "situation": situation, "risk": risk, "explanation": explanation,
                            "focus_score": scores["focus_score"], "safety_score": scores["safety_score"],
                            "gemini_confidence": scores.get("gemini_confidence", None), "gemini_verified": situation_data.get("gemini_verified", False)
                        }
                        log_event(event)
                        
                        from ui.opencv_view import render_overlay
                        output_frame = render_overlay(frame, detections, situation, risk, zones=active_zones)
                        st.session_state.current_processed_frame = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB)
                        
                        camera_placeholder.image(st.session_state.current_processed_frame, channels="RGB", use_container_width=True)
                        explanation_placeholder.markdown(clean_html(f'<div class="explanation-block"><div class="explanation-title">Behavior Explanation</div><div class="explanation-text">{explanation}</div></div>'), unsafe_allow_html=True)
                        metrics_placeholder.markdown(clean_html(render_metrics_grid(situation, risk, scores["focus_score"], scores["safety_score"], gemini_confidence)), unsafe_allow_html=True)
                        
                        if not st.session_state.video_metrics_history.empty:
                            chart_df = st.session_state.video_metrics_history.set_index("Frame")
                            chart_placeholder.line_chart(chart_df)
                            
                        if os.path.exists(CSV_FILE):
                            try:
                                df_new = pd.read_csv(CSV_FILE)
                                table_placeholder.markdown(clean_html(render_events_table(df_new)), unsafe_allow_html=True)
                            except Exception: pass
                            
                        time.sleep(max(0.001, 0.05 / playback_speed))
                finally:
                    cap.release()
            if os.path.exists(CSV_FILE):
                try: df = pd.read_csv(CSV_FILE)
                except Exception: pass

        if df is not None and not df.empty:
            last_row = df.iloc[-1]
            current_situation = last_row.get("situation", "Unknown")
            current_risk = last_row.get("risk", "Unknown")
            current_focus = last_row.get("focus_score", 100)
            current_safety = last_row.get("safety_score", 10)
            current_explanation = last_row.get("explanation", "No explanation available.")
            gemini_confidence = last_row.get("gemini_confidence", None)
            
            if mode == "📤 UPLOAD VIDEO" and st.session_state.gemini_manual_insight is not None:
                insight = st.session_state.gemini_manual_insight
                current_situation = insight["situation"]
                current_risk = insight["risk"]
                current_explanation = insight["explanation"]
                scores = compute_scores(current_situation, current_risk, None, insight["confidence"])
                current_focus = scores["focus_score"]
                current_safety = scores["safety_score"]
                
            if mode == "📤 UPLOAD VIDEO":
                if "current_processed_frame" in st.session_state and st.session_state.current_processed_frame is not None:
                    camera_placeholder.image(st.session_state.current_processed_frame, channels="RGB", use_container_width=True)
                else:
                    camera_placeholder.markdown(clean_html(render_camera_hud("Waiting...", active_zones)), unsafe_allow_html=True)
            else:
                camera_placeholder.markdown(clean_html(render_camera_hud(current_situation, active_zones)), unsafe_allow_html=True)
            
            explanation_placeholder.markdown(clean_html(f'<div class="explanation-block"><div class="explanation-title">Behavior Explanation</div><div class="explanation-text">{current_explanation}</div></div>'), unsafe_allow_html=True)
            metrics_placeholder.markdown(clean_html(render_metrics_grid(current_situation, current_risk, current_focus, current_safety, gemini_confidence)), unsafe_allow_html=True)
            
            if mode == "📤 UPLOAD VIDEO" and not st.session_state.video_metrics_history.empty:
                chart_df = st.session_state.video_metrics_history.set_index("Frame")
                chart_placeholder.line_chart(chart_df)
                
            table_placeholder.markdown(clean_html(render_events_table(df)), unsafe_allow_html=True)
        else:
            camera_placeholder.markdown(clean_html(render_camera_hud("Waiting...", active_zones)), unsafe_allow_html=True)
            explanation_placeholder.markdown(clean_html('<div class="explanation-block"><div class="explanation-title">Behavior Explanation</div><div class="explanation-text">Waiting for events...</div></div>'), unsafe_allow_html=True)
            metrics_placeholder.markdown(clean_html(render_metrics_grid("Waiting...", "Unknown", 100, 10)), unsafe_allow_html=True)
            table_placeholder.markdown("<div class='no-events'>Waiting for camera events...</div>", unsafe_allow_html=True)

        time.sleep(1)

elif selection == "Analytics":
    st.markdown('<div class="camera-card"><h3 style="color:#0f172a; margin:0 0 10px 0;">Advanced Analytics</h3><p style="color:#64748b; margin-top:0;">Detailed breakdown of AI detection metrics and system performance over time.</p></div>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            if not df.empty:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown('<div class="camera-card"><div style="font-weight:700; color:#0f172a; margin-bottom:15px;">Events by Risk Level</div>', unsafe_allow_html=True)
                    risk_counts = df['risk'].value_counts().reset_index()
                    fig = px.pie(risk_counts, values='count', names='risk', hole=0.4, color_discrete_sequence=['#10b981', '#f59e0b', '#ef4444'])
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown('<div class="camera-card"><div style="font-weight:700; color:#0f172a; margin-bottom:15px;">Safety Score Trend</div>', unsafe_allow_html=True)
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df = df.sort_values('timestamp')
                    fig2 = px.line(df, x='timestamp', y='safety_score', color_discrete_sequence=['#3b82f6'])
                    st.plotly_chart(fig2, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Analytics will appear here once events are logged.")
        except Exception:
            st.error("Error reading events database.")
    else:
        st.info("Analytics will appear here once events are logged.")

elif selection == "Events":
    st.markdown('<div class="camera-card"><h3 style="color:#0f172a; margin:0 0 10px 0;">Event Log Database</h3><p style="color:#64748b; margin-top:0;">Search and filter historical event logs.</p></div>', unsafe_allow_html=True)
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            st.dataframe(df, use_container_width=True)
        except Exception:
            pass
    else:
        st.info("No events logged yet.")

elif selection == "Reports":
    st.markdown('<div class="camera-card"><h3 style="color:#0f172a; margin:0 0 10px 0;">Automated Reports</h3><p style="color:#64748b; margin-top:0;">Generate PDF or CSV reports for compliance and auditing.</p></div>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.button("📄 Generate Daily Summary (PDF)")
    c2.button("📊 Export Full Event Log (CSV)")
    c3.button("📈 Export Analytics Data (CSV)")

elif selection == "Settings":
    st.markdown('<div class="camera-card"><h3 style="color:#0f172a; margin:0 0 10px 0;">System Settings</h3></div>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    
    if st.session_state.user_role == "Admin":
        st.success("Admin privileges enabled. You can modify system configurations.")
        st.toggle("Enable Night Vision Enhancements (CLAHE)", value=True)
        st.toggle("Enable Gemini Vision API Fallback", value=True)
        st.text_input("Google API Key", type="password", value="********")
        st.button("Save Configurations", type="primary")
    else:
        st.warning("You have User privileges. Settings are view-only.")
        st.toggle("Enable Night Vision Enhancements (CLAHE)", value=True, disabled=True)
        st.text_input("Google API Key", type="password", value="********", disabled=True)

else:
    st.markdown(f'<div class="camera-card"><h3 style="color:#0f172a; margin:0;">{selection}</h3><p style="color:#64748b;">This module is under development.</p></div>', unsafe_allow_html=True)