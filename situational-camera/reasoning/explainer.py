from explanation.explanation_generator import get_explanation

def generate_explanation(situation: str) -> str:
    """
    Generates a human-readable explanation sentence explaining the current situation.

    Parameters:
        situation (str): The current classified situation.

    Returns:
        str: A human-readable sentence explaining the situation.
    """
    return get_explanation(situation)

