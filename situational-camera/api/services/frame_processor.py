import cv2
import base64
import time
import os
from api.services.pipeline import pipeline_service

class FrameProcessor:
    @staticmethod
    def encode_frame_to_base64(frame) -> str:
        """
        Encodes an OpenCV frame to a base64 JPEG string.
        """
        _, buffer = cv2.imencode(".jpg", frame)
        return base64.b64encode(buffer).decode("utf-8")

    @staticmethod
    def get_video_stream(camera_id: str, source, name: str):
        """
        Generator function that captures frames from an OpenCV source,
        processes them through the pipeline, and yields JSON responses.
        Handles int sources (webcams) and string sources (RTSP / local MP4 files).
        Loops video files to provide continuous playback.
        """
        from api.services.pipeline import pipeline_service

        # Convert source to int if it represents a webcam
        actual_source = source
        if isinstance(source, str) and source.isdigit():
            actual_source = int(source)

        cap = cv2.VideoCapture(actual_source)
        if not cap.isOpened():
            # Yield error state
            yield {
                "error": f"Could not open camera source: {source}",
                "status": "Offline"
            }
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0 or fps > 60:
            fps = 30.0  # Default fallback

        frame_delay = 1.0 / fps
        is_video_file = isinstance(actual_source, str) and os.path.exists(actual_source)

        try:
            while cap.isOpened():
                start_time = time.time()
                ret, frame = cap.read()

                if not ret:
                    if is_video_file:
                        # Loop video file
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = cap.read()
                        if not ret:
                            break
                    else:
                        # Webcam or stream disconnected
                        break

                if frame is None:
                    continue

                # Run pipeline
                result = pipeline_service.run_pipeline(frame, camera_id, name)
                
                # Base64 encode the frame
                base64_frame = FrameProcessor.encode_frame_to_base64(frame)
                result["frame"] = base64_frame
                result["camera_name"] = name
                result["camera_id"] = camera_id

                yield result

                # Throttle to match frame rate
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_delay - elapsed)
                time.sleep(sleep_time)

        finally:
            cap.release()
