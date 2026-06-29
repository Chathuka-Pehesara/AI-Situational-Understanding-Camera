from detection.detector import detect_objects
from rules.rule_engine import detect_situation
from explanation.explanation_generator import get_explanation
from scoring.scoring import calculate_scores

def main():
    # Pass None to detect_objects since it requires a frame argument
    detections=detect_objects(None)

    movement_detected=True

    result=detect_situation(detections,movement_detected)

    situation=result["situation"]
    risk=result["risk"]

    explanation=get_explanation(situation)

    scores=calculate_scores(
        situation=situation,
        risk=risk,
        detections=detections
    )

    print("\n========== RESULT ==========")
    print("Detections:",detections)
    print("Situation :", situation)
    print("Risk      :", risk)
    print("Explanation:", explanation)
    print("Focus Score :", scores["focus_score"])
    print("Safety Score:", scores["safety_score"])

if __name__=="__main__":
    main()