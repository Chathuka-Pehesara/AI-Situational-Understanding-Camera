import React, { useState, useEffect } from "react";
import StatsRow from "../components/dashboard/StatsRow";
import LiveFeed from "../components/dashboard/LiveFeed";
import AlertSidebar from "../components/dashboard/AlertSidebar";
import GeminiPanel from "../components/dashboard/GeminiPanel";
import { useCamera } from "../hooks/useCamera";
import { useWebSocket } from "../hooks/useWebSocket";
import { useAlerts } from "../hooks/useAlerts";

export default function Dashboard() {
  const { cameras, loading: camerasLoading, fetchCameras } = useCamera();
  const { alerts, clearAlerts, addLocalAlert } = useAlerts();
  
  const [selectedCameraId, setSelectedCameraId] = useState(null);
  const [streamData, setStreamData] = useState({
    frame: "",
    detections: [],
    situation: "Normal Activity",
    risk: "Low",
    explanation: "Awaiting video stream analysis...",
    safety_score: 10,
    focus_score: 100,
    gemini_confidence: 0.5,
    gemini_verified: false,
    fps: 0,
    resolution: "",
    timestamp: "",
    is_video_file: false,
    current_frame: 0,
    total_frames: 0
  });

  // Set default selected camera
  useEffect(() => {
    if (cameras.length > 0 && !selectedCameraId) {
      setSelectedCameraId(cameras[0].id);
    }
  }, [cameras, selectedCameraId]);

  // Handle incoming frames from WebSocket
  const handleFrameMessage = (data) => {
    setStreamData((prev) => ({ ...prev, ...data }));
    
    // If the frame represents an incident alert, trigger local visual alert immediately
    if (data.situation && data.risk && data.risk !== "Low") {
      addLocalAlert({
        id: `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        camera_id: data.camera_id,
        camera_name: data.camera_name,
        situation: data.situation,
        risk: data.risk,
        explanation: data.explanation,
        timestamp: new Date().toISOString(),
        safety_score: data.safety_score,
        focus_score: data.focus_score,
        status: "active"
      });
    }
  };

  const { status: wsStatus, connect: reconnectWS, sendMessage } = useWebSocket(selectedCameraId, handleFrameMessage);

  // Derive stats
  const activeCamerasCount = cameras.filter((c) => c.status === "Live" || c.id === selectedCameraId).length;
  const currentRisk = streamData.risk;
  const currentConfidencePercent = Math.round(streamData.gemini_confidence * 100);

  const handleCameraChange = (cameraId) => {
    setSelectedCameraId(cameraId);
    // Reset stream data when switching cameras
    setStreamData({
      frame: "",
      detections: [],
      situation: "Normal Activity",
      risk: "Low",
      explanation: "Switched camera. Connecting...",
      safety_score: 10,
      focus_score: 100,
      gemini_confidence: 0.5,
      gemini_verified: false,
      fps: 0,
      resolution: "",
      timestamp: "",
      is_video_file: false,
      current_frame: 0,
      total_frames: 0
    });
  };

  const currentCamera = cameras.find((c) => c.id === selectedCameraId);

  return (
    <div className="space-y-6 flex flex-col h-full min-w-0 animate-page-enter">
      
      {/* SECTION 1: Stats Summary Row */}
      <StatsRow 
        alertsCount={alerts.filter((a) => a.status === "active").length} 
        activeCameras={activeCamerasCount} 
        riskLevel={currentRisk} 
        avgConfidence={currentConfidencePercent} 
      />

      {/* SECTION 2: Live Video Stream and Alerts Sidebar (side by side) */}
      <div className="flex flex-col xl:flex-row gap-6 items-stretch flex-1 min-h-[420px] min-w-0">
        
        {/* Live Stream Panel */}
        <LiveFeed 
          frame={streamData.frame}
          detections={streamData.detections}
          cameraName={currentCamera ? currentCamera.name : "Main Webcam"}
          resolution={streamData.resolution}
          fps={streamData.fps}
          wsStatus={wsStatus}
          cameras={cameras}
          selectedCameraId={selectedCameraId}
          onCameraChange={handleCameraChange}
          onReconnect={reconnectWS}
          sendMessage={sendMessage}
          isVideoFile={streamData.is_video_file}
          currentFrame={streamData.current_frame}
          totalFrames={streamData.total_frames}
        />

        {/* Real-time Alerts Feed */}
        <AlertSidebar 
          alerts={alerts} 
          onClear={clearAlerts} 
        />
        
      </div>

      {/* SECTION 3: Detailed Gemini Reasoning logs */}
      <GeminiPanel 
        situation={streamData.situation}
        risk={streamData.risk}
        explanation={streamData.explanation}
        confidence={streamData.gemini_confidence}
        geminiVerified={streamData.gemini_verified}
      />

    </div>
  );
}
