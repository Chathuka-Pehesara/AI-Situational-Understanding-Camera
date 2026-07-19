from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import os
import json
import cv2

router = APIRouter(prefix="/api/cameras", tags=["cameras"])
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMERAS_FILE = os.path.join(base_dir, "data", "cameras.json")

class CameraCreate(BaseModel):
    name: str
    source: str # "0", RTSP URL, or local video file path

def load_cameras():
    if not os.path.exists(CAMERAS_FILE):
        return []
    try:
        with open(CAMERAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_cameras(cameras):
    os.makedirs(os.path.dirname(CAMERAS_FILE), exist_ok=True)
    with open(CAMERAS_FILE, "w", encoding="utf-8") as f:
        json.dump(cameras, f, indent=2)

from fastapi import UploadFile, File
import shutil

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    uploads_dir = os.path.join(base_dir, "data", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    file_path = os.path.join(uploads_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"file_path": file_path}

@router.get("")
def list_cameras():
    return load_cameras()

@router.post("")
def add_camera(camera_data: CameraCreate):
    cameras = load_cameras()
    
    # Generate simple unique ID
    camera_id = f"cam_{len(cameras) + 1}"
    
    # Test connection
    source = camera_data.source
    if source.isdigit():
        actual_source = int(source)
    else:
        actual_source = source
        
    cap = cv2.VideoCapture(actual_source)
    is_live = cap.isOpened()
    
    resolution = "Unknown"
    fps = 30.0
    
    if is_live:
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        resolution = f"{width}x{height}"
        val_fps = cap.get(cv2.CAP_PROP_FPS)
        if val_fps > 0 and val_fps <= 60:
            fps = val_fps
        cap.release()
        status_text = "Live"
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to open video source: {actual_source}. Please ensure it is a valid MP4 file."
        )

    new_camera = {
        "id": camera_id,
        "name": camera_data.name,
        "source": camera_data.source,
        "status": status_text,
        "resolution": resolution,
        "fps": round(fps, 1),
        "alert_count_today": 0
    }
    
    cameras.append(new_camera)
    save_cameras(cameras)
    
    return new_camera

@router.delete("/{camera_id}")
def delete_camera(camera_id: str):
    cameras = load_cameras()
    filtered_cameras = [c for c in cameras if c["id"] != camera_id]
    
    if len(filtered_cameras) == len(cameras):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with ID {camera_id} not found."
        )
        
    save_cameras(filtered_cameras)
    return {"message": f"Camera {camera_id} removed successfully"}
