import asyncio
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

    # State object to control stream playback
    stream_control = {
        "paused": False,
        "seek_to_frame": None,
        "stop": False
    }

    # Background task to listen for incoming websocket commands
    async def listen_for_commands():
        try:
            while True:
                data = await websocket.receive_json()
                if "command" in data:
                    cmd = data["command"]
                    if cmd == "pause":
                        stream_control["paused"] = True
                    elif cmd == "play":
                        stream_control["paused"] = False
                    elif cmd == "seek":
                        stream_control["seek_to_frame"] = data.get("frame_index")
        except WebSocketDisconnect:
            stream_control["stop"] = True
        except Exception:
            stream_control["stop"] = True
            
    listener_task = asyncio.create_task(listen_for_commands())

    # 2. Start frame stream generator
    stream_generator = FrameProcessor.get_video_stream(camera_id, source, name, stream_control)
    
    try:
        async for result in stream_generator:
            if stream_control["stop"]:
                break
                
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
        listener_task.cancel()
        # Clean shutdown (generator cleanup in finally block will release Capture)
        await stream_generator.aclose()
