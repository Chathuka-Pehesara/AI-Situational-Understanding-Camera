# AI Situational Understanding Camera

This project implements an AI-driven camera processing pipeline designed to understand situational contexts in real-time, compute safety metrics, and log events.

## Project Structure

```text
situational-camera/
├── main.py                # Main pipeline runner showing execution & call order
├── intergration_test.py   # Integration test script for the pipeline components
├── requirements.txt       # Project dependencies
├── yolov8n.pt             # YOLOv8 Nano model weights
├── detection/             # Perception Layer
│   ├── __init__.py
│   ├── detector.py        # YOLOv8 object detector wrapper
│   └── tracker.py         # Movement tracker & bounding box center tracking
├── reasoning/             # Intelligence Proxy Layer
│   ├── __init__.py
│   ├── rule_engine.py     # Situation rules proxy (calls rules/rule_engine.py)
│   ├── explainer.py       # Natural language explanation proxy (calls explanation/explanation_generator.py)
│   └── scorer.py          # Real-time safety and focus scoring proxy (calls scoring/scoring.py)
├── rules/                 # Intelligence Rules Layer
│   ├── __init__.py
│   ├── rule_engine.py     # Multi-variable situation classification rules
│   └── test_rules.py      # Test script for rules
├── explanation/           # Intelligence Explanation Layer
│   ├── __init__.py
│   └── explanation_generator.py # Natural language explanation templates
├── scoring/               # Intelligence Scoring Layer
│   ├── __init__.py
│   └── scoring.py         # Real-time safety (0-10) and focus (0-100) scoring logic
├── custom_logging/        # Storage Layer
│   ├── __init__.py
│   └── event_logger.py    # State change event logger (saves to CSV)
├── ui/                    # Interface Layer
│   ├── __init__.py
│   ├── opencv_view.py     # OpenCV HUD overlays (bounding boxes & telemetry)
│   └── dashboard.py       # Live Streamlit dashboard app (monitoring & simulator)
├── data/                  # Data Assets
│   ├── .gitkeep           # git placeholder
│   └── events_log.csv     # Automatically generated event log
└── scratch/               # Development Scratch scripts
    ├── test_detection.py
    ├── test_logger.py
    ├── test_rendering.py
    └── test_tracker.py
```

## Shared Data Contracts

### Object Detection (`detection/detector.py`)
`detect_objects(frame)` returns a list of dictionaries with the schema:
```python
[
  {
    "label": str,
    "bbox": [x1, y1, x2, y2],
    "confidence": float,
    "track_id": int or None
  },
  ...
]
```

### Movement Tracking (`detection/tracker.py`)
`is_moving(person_id, current_bbox)` returns `bool`.

### Reasoning Engine (`reasoning/rule_engine.py` / `rules/rule_engine.py`)
`evaluate_situation(detections, movement_detected)` returns:
```python
{
  "situation": str,
  "risk": str
}
```

### Explainer (`reasoning/explainer.py` / `explanation/explanation_generator.py`)
`generate_explanation(situation)` returns a human-readable sentence (`str`).

### Metric Scorer (`reasoning/scorer.py` / `scoring/scoring.py`)
`compute_scores(situation, risk, detections)` returns:
```python
{
  "situation": str,
  "risk": str,
  "focus_score": int,   # Scale 0-100
  "safety_score": int   # Scale 0-10
}
```

### Event Logging (`custom_logging/event_logger.py`)
`log_event(event)` logs a dictionary representation of the evaluated state containing `timestamp`, `situation`, `risk`, `explanation`, `focus_score`, and `safety_score` to `data/events_log.csv`.

### Overlay Renderer (`ui/opencv_view.py`)
`render_overlay(frame, detections, situation, risk)` returns the frame with overlay graphics.

### Streamlit Dashboard (`ui/dashboard.py`)
Run the Streamlit web dashboard:
```bash
streamlit run ui/dashboard.py
```
