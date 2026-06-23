from rule_engine import detect_situation

samples = [
    ("Distracted Walking", [{"label": "person"}, {"label": "phone"}], True),
    ("Working", [{"label": "person"}, {"label": "laptop"}], False),
    ("Resting", [{"label": "person"}], False),
    ("Hurrying", [{"label": "person"}, {"label": "bag"}], True),
]

for name, dets, movement in samples:
    result = detect_situation(dets, movement)
    print(f"Expected: {name} -> Detected: {result['situation']}, Risk: {result['risk']}")