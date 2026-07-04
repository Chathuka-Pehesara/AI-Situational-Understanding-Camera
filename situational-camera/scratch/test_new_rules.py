import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rules.rule_engine import detect_situation
from scoring.scoring import calculate_scores

samples = [
    (
        "Weapon Detected",
        [
            {"label": "person"},
            {"label": "knife"}
        ],
        True
    ),
    (
        "Animal Intrusion (Moving)",
        [
            {"label": "animal"}
        ],
        True
    ),
    (
        "Animal Intrusion (Stationary)",
        [
            {"label": "animal"}
        ],
        False
    ),
    (
        "Vehicle Loitering",
        [
            {"label": "motorcycle"}
        ],
        False
    )
]

print("=== Testing New Rule Classifications ===")
for name, dets, movement in samples:
    rule_res = detect_situation(dets, movement)
    scores = calculate_scores(rule_res["situation"], rule_res["risk"], dets)
    print(f"Test: {name}")
    print(f"  -> Situation : {rule_res['situation']}")
    print(f"  -> Risk      : {rule_res['risk']}")
    print(f"  -> Focus     : {scores['focus_score']}%")
    print(f"  -> Safety    : {scores['safety_score']}/10")
    print()
