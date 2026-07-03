import time
from rule_engine import detect_situation

samples = [
    (
        "Trespassing",
        [
            {
                "label": "person",
                "bbox": [50, 150, 150, 380],
                "zone_info": {
                    "inside_zone": "Restricted Zone A",
                    "loitering_duration": 1.2,
                    "is_trespassing": True,
                    "is_perimeter_breach": False,
                    "is_loitering": False
                }
            }
        ],
        False
    ),
    (
        "Perimeter Breach",
        [
            {
                "label": "person",
                "bbox": [420, 200, 520, 420],
                "zone_info": {
                    "inside_zone": "Perimeter Gate",
                    "loitering_duration": 1.5,
                    "is_trespassing": False,
                    "is_perimeter_breach": True,
                    "is_loitering": False
                }
            }
        ],
        True
    ),
    (
        "Loitering",
        [
            {
                "label": "person",
                "bbox": [50, 150, 150, 380],
                "zone_info": {
                    "inside_zone": "Restricted Zone A",
                    "loitering_duration": 7.5,
                    "is_trespassing": True,
                    "is_perimeter_breach": False,
                    "is_loitering": True
                }
            }
        ],
        False
    )
]

for name, dets, movement in samples:
    result = detect_situation(dets, movement)
    print(f"Expected: {name} -> Detected: {result['situation']}, Risk: {result['risk']}")
