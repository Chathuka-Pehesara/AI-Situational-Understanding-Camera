def detect_objects(frame):
    """
    Runs object detection on the input video frame using YOLOv8.

    Parameters:
        frame (numpy.ndarray): The input image frame.

    Returns:
        list: A list of dicts in the following exact format:
            [
                {
                    "label": str, 
                    "bbox": [x1, y1, x2, y2], 
                    "confidence": float
                },
                ...
            ]
    """
    # TODO: implement YOLOv8 object detection inference
    pass
