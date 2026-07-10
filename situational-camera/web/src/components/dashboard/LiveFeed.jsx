import React, { useRef, useEffect, useState } from "react";
import { Play, Pause, Square, AlertCircle, RefreshCw } from "lucide-react";
import { DETECTOR_COLORS } from "../../lib/constants";

// The hardcoded zone coords matching the backend main.py setup
const ZONES = {
  "Restricted Zone A": [
    [30, 80],
    [250, 80],
    [220, 400],
    [10, 400]
  ],
  "Perimeter Gate": [
    [380, 120],
    [600, 120],
    [620, 450],
    [400, 450]
  ],
  "Unsafe Zone B": [
    [250, 10],
    [400, 10],
    [400, 100],
    [250, 100]
  ]
};

export default function LiveFeed({ 
  frame, 
  detections, 
  cameraName, 
  resolution, 
  fps, 
  wsStatus, 
  cameras = [], 
  onCameraChange, 
  selectedCameraId,
  onReconnect,
  sendMessage,
  isVideoFile,
  currentFrame,
  totalFrames
}) {
  const containerRef = useRef(null);
  const canvasRef = useRef(null);
  const imgRef = useRef(null);
  const [imgSize, setImgSize] = useState({ width: 0, height: 0 });
  const [isPaused, setIsPaused] = useState(false);

  const handleTogglePlay = () => {
    const newState = !isPaused;
    setIsPaused(newState);
    if (sendMessage) {
      sendMessage({ command: newState ? "pause" : "play" });
    }
  };

  const handleSeek = (e) => {
    const frame = parseInt(e.target.value, 10);
    if (sendMessage) {
      sendMessage({ command: "seek", frame_index: frame });
    }
  };

  // Update canvas size when container size or image size changes
  const updateCanvasSize = () => {
    if (imgRef.current && canvasRef.current) {
      const displayWidth = imgRef.current.clientWidth;
      const displayHeight = imgRef.current.clientHeight;
      canvasRef.current.width = displayWidth;
      canvasRef.current.height = displayHeight;
    }
  };

  useEffect(() => {
    window.addEventListener("resize", updateCanvasSize);
    return () => window.removeEventListener("resize", updateCanvasSize);
  }, []);

  const handleImageLoad = () => {
    if (imgRef.current) {
      setImgSize({
        width: imgRef.current.naturalWidth,
        height: imgRef.current.naturalHeight
      });
      updateCanvasSize();
    }
  };

  // Draw overlay whenever detections, frame size, or canvas size changes
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || imgSize.width === 0 || imgSize.height === 0) return;

    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const scaleX = canvas.width / imgSize.width;
    const scaleY = canvas.height / imgSize.height;

    // 1. Draw Zones (Polygons)
    Object.entries(ZONES).map(([zoneName, points]) => {
      if (points.length < 3) return;
      
      ctx.beginPath();
      // Move to first point
      ctx.moveTo(points[0][0] * scaleX, points[0][1] * scaleY);
      for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i][0] * scaleX, points[i][1] * scaleY);
      }
      ctx.closePath();

      // Color selection based on name
      let color = "rgba(59, 130, 246, 0.4)"; // Blue
      let fillColor = "rgba(59, 130, 246, 0.1)";
      if (zoneName === "Restricted Zone A" || zoneName === "Unsafe Zone B") {
        color = "rgba(239, 68, 68, 0.5)"; // Red
        fillColor = "rgba(239, 68, 68, 0.1)";
      } else if (zoneName === "Perimeter Gate") {
        color = "rgba(249, 115, 22, 0.5)"; // Orange
        fillColor = "rgba(249, 115, 22, 0.1)";
      }

      ctx.fillStyle = fillColor;
      ctx.fill();
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Draw label
      ctx.fillStyle = color;
      ctx.font = "bold 9px sans-serif";
      ctx.fillText(zoneName.toUpperCase(), points[0][0] * scaleX, points[0][1] * scaleY - 4);
    });

    // 2. Draw Bounding Boxes and Labels for Detections
    if (detections && Array.isArray(detections)) {
      detections.forEach((det) => {
        const { label, bbox, confidence, track_id, zone_info } = det;
        if (!bbox || bbox.length < 4) return;

        const x1 = bbox[0] * scaleX;
        const y1 = bbox[1] * scaleY;
        const x2 = bbox[2] * scaleX;
        const y2 = bbox[3] * scaleY;
        const width = x2 - x1;
        const height = y2 - y1;

        // Bounding Box Color logic (overridden if loitering/trespassing)
        let color = DETECTOR_COLORS[label] || DETECTOR_COLORS.default;
        let text = `${label.toUpperCase()} ${Math.round(confidence * 100)}%`;

        if (label === "person" && zone_info) {
          if (zone_info.is_trespassing) {
            color = "var(--severity-critical)";
            text = `TRESPASSER (${zone_info.loitering_duration}s)`;
          } else if (zone_info.is_loitering) {
            color = "var(--severity-high)";
            text = `LOITERING (${zone_info.loitering_duration}s)`;
          } else if (zone_info.is_perimeter_breach) {
            color = "var(--severity-medium)";
            text = `BREACH`;
          }
        } else if (label === "knife") {
          color = "var(--severity-critical)";
          text = `WEAPON [KNIFE]`;
        }

        // Draw Rect
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(x1, y1, width, height);

        // Draw Label Background
        ctx.fillStyle = color;
        ctx.font = "bold 10px monospace";
        const textWidth = ctx.measureText(text).width + 6;
        ctx.fillRect(x1 - 1, y1 - 16, textWidth, 16);

        // Draw Label Text
        ctx.fillStyle = "#0A0E1A"; // Dark text contrast
        ctx.fillText(text, x1 + 3, y1 - 4);
      });
    }
  }, [detections, imgSize, frame]);

  const getStatusColor = () => {
    if (wsStatus === "connected") return "bg-severity-low";
    if (wsStatus === "connecting") return "bg-severity-medium";
    return "bg-severity-critical";
  };

  return (
    <div className="bg-bg-surface border border-border rounded-card overflow-hidden flex flex-col flex-1 min-w-0 shadow-lg">
      
      {/* Top Header Controls */}
      <div className="shrink-0 px-5 py-3 border-b border-border bg-bg-surface/50 flex items-center justify-between select-none">
        <div className="flex items-center gap-3">
          <span className="flex h-2.5 w-2.5 relative">
            {wsStatus === "connected" && (
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-severity-critical opacity-75"></span>
            )}
            <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${getStatusColor()}`}></span>
          </span>
          <span className="text-xs uppercase font-extrabold tracking-widest text-text-primary">
            LIVE FEED
          </span>
        </div>

        {/* Camera Selector Dropdown */}
        <div className="flex items-center gap-3">
          {cameras.length > 0 && (
            <select
              value={selectedCameraId || ""}
              onChange={(e) => onCameraChange(e.target.value)}
              className="bg-bg-base border border-border focus:border-accent-blue text-xs text-text-primary rounded-btn px-3 py-1.5 focus:outline-none cursor-pointer hover:bg-bg-elevated transition-colors duration-200"
            >
              {cameras.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.status})
                </option>
              ))}
            </select>
          )}

          {wsStatus !== "connected" && (
            <button
              onClick={onReconnect}
              title="Reconnect Feed"
              className="p-1.5 bg-bg-elevated hover:bg-bg-overlay border border-border hover:border-border-bright rounded-btn text-text-secondary hover:text-text-primary transition-all duration-200"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Screen Frame Container */}
      <div ref={containerRef} className="bg-bg-base relative flex-1 min-h-0 flex items-center justify-center overflow-hidden">
        {frame ? (
          <div className="relative w-full h-full flex items-center justify-center">
            {/* Base64 frame image */}
            <img
              ref={imgRef}
              src={`data:image/jpeg;base64,${frame}`}
              alt="Stream Feed"
              onLoad={handleImageLoad}
              className="max-w-full max-h-full object-contain"
            />
            {/* Absolute overlay canvas */}
            <canvas ref={canvasRef} className="absolute pointer-events-none" />
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center gap-4 text-text-muted p-8 text-center select-none">
            {wsStatus === "connecting" ? (
              <>
                <RefreshCw className="w-12 h-12 text-accent-blue animate-spin" />
                <div>
                  <h3 className="text-sm font-semibold text-text-secondary mb-1">Connecting to Stream...</h3>
                  <p className="text-xs text-text-muted">Establishing WebSocket channel to source</p>
                </div>
              </>
            ) : (
              <>
                <AlertCircle className="w-12 h-12 text-severity-critical animate-bounce" />
                <div>
                  <h3 className="text-sm font-semibold text-text-secondary mb-1">Camera Stream Offline</h3>
                  <p className="text-xs text-text-muted">Check source configuration or API server status</p>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* Bottom Telemetry Bar */}
      <div className="shrink-0 px-5 py-2.5 border-t border-border bg-bg-surface/50 text-[10px] text-text-secondary font-mono flex items-center justify-between select-none">
        <div className="flex items-center gap-1.5">
          <span className="text-text-muted">CAMERA:</span>
          <span className="text-text-primary font-bold">{cameraName || "Unknown"}</span>
        </div>

        {isVideoFile && (
          <div className="flex-1 max-w-md mx-6 flex items-center gap-3">
            <button 
              onClick={handleTogglePlay}
              className="text-text-secondary hover:text-accent-blue transition-colors outline-none"
            >
              {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
            </button>
            <input 
              type="range" 
              min="0" 
              max={totalFrames > 0 ? totalFrames - 1 : 100} 
              value={currentFrame || 0} 
              onChange={handleSeek}
              className="flex-1 h-1 bg-bg-base rounded-lg appearance-none cursor-pointer accent-accent-blue"
            />
            <span className="text-text-muted text-[9px]">
              {Math.floor(currentFrame / fps || 0)}s / {Math.floor(totalFrames / fps || 0)}s
            </span>
          </div>
        )}

        <div className="flex items-center gap-4">
          <div>
            <span className="text-text-muted">RES:</span>{" "}
            <span className="text-accent-cyan font-bold">{resolution || "Unknown"}</span>
          </div>
          <div>
            <span className="text-text-muted">FPS:</span>{" "}
            <span className="text-severity-low font-bold">{fps ? fps.toFixed(1) : "0.0"}</span>
          </div>
        </div>
      </div>

    </div>
  );
}
