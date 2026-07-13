import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import camera, stream, alerts, events, chat

app = FastAPI(
    title="SituVision AI API",
    description="Backend API for real-time situational understanding camera pipeline",
    version="1.0.0"
)

# CORS setup
origins = [
    "http://localhost:5173", # React Vite dev server
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(camera.router)
app.include_router(stream.router)
app.include_router(alerts.router)
app.include_router(events.router)
app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to SituVision AI API. Use WebSocket at /ws/stream/{camera_id} or REST at /api/."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
