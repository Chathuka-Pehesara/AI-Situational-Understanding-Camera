# AI Situational Understanding Camera

This project implements an AI-driven camera processing pipeline designed to understand situational contexts in real-time, compute safety metrics, and log events.

## Project Structure

```text
situational-camera/
├── main.py               # Main pipeline sequence and imports
├── detection/
│   ├── __init__.py
│   ├── detector.py       # YOLOv8 wrapper, runs inference, returns detections
│   └── tracker.py        # Movement detection (compares bbox centers across frames)
├── reasoning/
│   ├── __init__.py
│   ├── rule_engine.py    # Situation rules (Person+Phone+Movement -> situation)
│   ├── explainer.py      # Maps situation -> human-readable sentence
│   └── scorer.py         # Focus Score (0-100) and Safety Score (0-10) logic
├── custom_logging/
│   ├── __init__.py
│   └── event_logger.py   # Writes situation changes to CSV
├── ui/
│   ├── __init__.py
│   ├── opencv_view.py    # Draws bounding boxes + situation/risk overlay
│   └── dashboard.py      # Streamlit dashboard: feed, situation, risk, event table
├── data/
│   └── .gitkeep          # Event log output directory
├── requirements.txt      # List of dependencies
└── README.md             # Project documentation
```

## Shared Data Contracts

### Object Detection (`detection/detector.py`)
`detect_objects(frame)` returns a list of dictionaries with the schema:
```python
[
  {
    "label": str,
    "bbox": [x1, y1, x2, y2],
    "confidence": float
  },
  ...
]
```

### Movement Tracking (`detection/tracker.py`)
`is_moving(person_id, current_bbox)` returns `bool`.

### Reasoning Engine (`reasoning/rule_engine.py`)
`evaluate_situation(detections, movement_detected)` returns:
```python
{
  "situation": str,
  "risk": str
}
```

### Explainer (`reasoning/explainer.py`)
`generate_explanation(situation)` returns a human-readable sentence (`str`).

### Metric Scorer (`reasoning/scorer.py`)
`compute_scores(situation, risk)` returns:
```python
{
  "focus_score": int,   # Scale 0-100
  "safety_score": int   # Scale 0-10
}
```

### Event Logging (`custom_logging/event_logger.py`)
`log_event(event)` logs a dictionary representation of the evaluated state to `data/events_log.csv`.

### Overlay Renderer (`ui/opencv_view.py`)
`render_overlay(frame, detections, situation, risk)` returns the frame with overlay graphics.

### Streamlit Dashboard (`ui/dashboard.py`)
Run the Streamlit web dashboard:
```bash
streamlit run ui/dashboard.py
```
