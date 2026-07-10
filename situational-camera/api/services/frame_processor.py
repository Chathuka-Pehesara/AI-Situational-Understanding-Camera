import cv2
import base64
import time
import os
import asyncio
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
    async def get_video_stream(camera_id: str, source, name: str, stream_control: dict = None):
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
        
        # Retry logic: hardware takes a moment to release the lock when we reconnect quickly
        retries = 3
        while not cap.isOpened() and retries > 0:
            await asyncio.sleep(0.5)
            cap = cv2.VideoCapture(actual_source)
            retries -= 1

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
        is_video_file = isinstance(actual_source, str) and not str(actual_source).isdigit()

        try:
            last_result = None
            
            while cap.isOpened():
                if stream_control and stream_control.get("stop"):
                    break
                    
                if stream_control and stream_control.get("seek_to_frame") is not None:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, stream_control["seek_to_frame"])
                    stream_control["seek_to_frame"] = None
                    last_result = None
                    
                if stream_control and stream_control.get("paused"):
                    await asyncio.sleep(0.1)
                    if last_result:
                        yield last_result
                    continue

                start_time = time.time()
                ret, frame = cap.read()
                
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if is_video_file else 0
                current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) if is_video_file else 0

                if not ret:
                    if is_video_file:
                        # Pause video file at end instead of looping immediately
                        if stream_control:
                            stream_control["paused"] = True
                        else:
                            # Fallback if no control is provided
                            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
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
                
                # Yield metadata for video controls
                result["is_video_file"] = is_video_file
                result["current_frame"] = current_frame
                result["total_frames"] = total_frames
                
                last_result = result

                yield result

                # Throttle to match frame rate and yield to event loop
                elapsed = time.time() - start_time
                sleep_time = max(0.01, frame_delay - elapsed)
                await asyncio.sleep(sleep_time)

        finally:
            cap.release()
