from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.services.frame_processor import FrameProcessor
from api.routers.camera import load_cameras

router = APIRouter(tags=["streaming"])

@router.websocket("/ws/stream/{camera_id}")
async def websocket_stream(websocket: WebSocket, camera_id: str):
    await websocket.accept()
    
    # 1. Fetch camera details
    cameras = load_cameras()
    camera = next((c for c in cameras if c["id"] == camera_id), None)
    
    if not camera:
        await websocket.send_json({"error": f"Camera with ID {camera_id} not found."})
        await websocket.close()
        return

    source = camera["source"]
    name = camera["name"]

    # 2. Start frame stream generator
    stream_generator = FrameProcessor.get_video_stream(camera_id, source, name)
    
    try:
        async for result in stream_generator:
            # Check for error state in stream
            if "error" in result:
                await websocket.send_json(result)
                break
                
            # Send base64 frame and detection metadata to frontend client
            await websocket.send_json(result)
            
    except WebSocketDisconnect:
        # Client closed connection
        pass
    except Exception as e:
        # Log or send other errors
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
    finally:
        # Clean shutdown (generator cleanup in finally block will release Capture)
        await stream_generator.aclose()
