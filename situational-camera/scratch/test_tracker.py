import sys
import os

# add parent directry means situational-camera in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detection.tracker import is_moving, reset_tracker

def test_movement_detector():
    print("Movement Tracker running...")
    reset_tracker()

    # First frame: person 1 is detected. Should return Flase
    bbox_1 = [100, 100, 200, 200] # center: (150, 150)
    assert is_moving(1, bbox_1) is False, "First frame shoukd not flag movement"

    # Second frame: person 1 moves slightly
    bbox_2 = [101, 101, 201, 201] # center: (151, 151)  Distance: ~1.41
    assert is_moving(1, bbox_2) is False, "Slightly movement below threshold should not flag"
    
    # Third frame: person 1 moves significantly 
    bbox_3 = [110, 110, 210, 210] # center: (160, 160) -> Dist from (151, 151): ~12.72
    assert is_moving(1, bbox_3) is True, "Significant movement should not flag True"

    # Check that different person IDs do not interfere with each other
    bbox_person_2 = [300, 300, 400, 400]
    assert is_moving(2, bbox_person_2) is False, "First detection of person 2 should be Flase"

    print("Success: ALl tracker tests passed!")

if __name__ == "__main__":
    test_movement_detector()