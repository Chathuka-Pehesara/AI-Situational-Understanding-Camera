EXPLANATION_TEMPLATES={
    "Distracted Walking":"Person is walking while using a phone.",
    "Working":"Person is working on a laptop.",
    "Resting":"Person is stationary and appears to be resting.",
    "Hurrying":"Person is moving quickly with belongings.",
    "Normal Activity":"Person is performing normal daily activity."
}

def get_explanation(situation):
    """
    Returns a human-readable explanation for the detected situation.

    Parameters:
        situation (str): Detected situation name.

    Returns:
        str: Explanation sentence.

    """

    return EXPLANATION_TEMPLATES.get(
        situation,
        "No explanation available."
    )

if __name__=="__main__":
    situations=[
        "Distracted Walking",
        "Working",
        "Resting",
        "Hurrying",
        "Normal Activity"
    ]

    for situation in situations:
        print(f"{situation}: {get_explanation(situation)}")