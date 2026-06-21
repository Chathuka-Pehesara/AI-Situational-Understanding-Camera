def is_moving(person_id, current_bbox) -> bool:
    """
    Compares bounding box centers across frames for a specific person
    to determine if they are moving.

    Parameters:
        person_id (int/str): Unique identifier for the tracked person.
        current_bbox (list): Current bounding box coordinates [x1, y1, x2, y2].

    Returns:
        bool: True if significant movement is detected, False otherwise.
    """
    # TODO: implement movement detection comparing bbox centers across frames
    pass
