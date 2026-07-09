import React, { useState } from "react";
import { Video, ShieldAlert, Plus, Trash2, Camera, AlertTriangle, CheckCircle, Wifi, RefreshCw } from "lucide-react";
import { useCamera } from "../hooks/useCamera";
import { api } from "../lib/api";
export default function Cameras() {
  const { cameras, loading, error, addCamera, deleteCamera, fetchCameras } = useCamera();
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Form states
  const [name, setName] = useState("");
  const [sourceType, setSourceType] = useState("webcam"); // webcam, rtsp, file
  const [source, setSource] = useState("0");
  const [isTesting, setIsTesting] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [testResult, setTestResult] = useState(null); // 'success', 'failed'
  const [selectedFile, setSelectedFile] = useState(null);
  
  const handleSourceTypeChange = (type) => {
    setSourceType(type);
    if (type === "webcam") {
      setSource("0");
    } else if (type === "rtsp") {
      setSource("rtsp://192.168.1.100:554/h264");
    } else {
      setSource("");
    }
    setSelectedFile(null);
    setTestResult(null);
  };

  const handleTestConnection = async () => {
    if (!name) {
      alert("Please enter a camera name.");
      return;
    }
    setIsTesting(true);
    setTestResult(null);

    try {
      let finalSource = source;
      if (sourceType === "file" && selectedFile) {
        setIsUploading(true);
        const res = await api.uploadVideo(selectedFile);
        finalSource = res.file_path;
        setSource(finalSource);
        setSelectedFile(null);
        setIsUploading(false);
      } else if (sourceType === "file" && !selectedFile && !source) {
         alert("Please select a file.");
         setIsTesting(false);
         return;
      }
      if (!finalSource) {
         alert("Please enter a source.");
         setIsTesting(false);
         return;
      }

      // Create a temporary connection test
      // In our backend, POST /api/cameras opens VideoCapture and tests it immediately
      const tempCam = await addCamera(name, finalSource);
      if (tempCam.status === "Live") {
        setTestResult("success");
      } else {
        setTestResult("failed");
      }
      
      // Since it was a test, immediately delete the temporary added camera so we don't duplicate
      await deleteCamera(tempCam.id);
      
    } catch (err) {
      setIsUploading(false);
      setTestResult("failed");
    } finally {
      setIsTesting(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!name) return;
    
    try {
      let finalSource = source;
      if (sourceType === "file" && selectedFile) {
        setIsUploading(true);
        const res = await api.uploadVideo(selectedFile);
        finalSource = res.file_path;
        setIsUploading(false);
      } else if (sourceType === "file" && !selectedFile && !source) {
         alert("Please select a file.");
         return;
      }
      if (!finalSource) return;

      await addCamera(name, finalSource);
      setIsModalOpen(false);
      // Reset form
      setName("");
      setSourceType("webcam");
      setSource("0");
      setSelectedFile(null);
      setTestResult(null);
    } catch (err) {
      setIsUploading(false);
      alert("Failed to save camera feed. Check connection parameters.");
    }
  };

  const handleDelete = async (cameraId) => {
    if (confirm("Are you sure you want to delete this camera feed?")) {
      try {
        await deleteCamera(cameraId);
      } catch (err) {
        alert("Failed to remove camera.");
      }
    }
  };

  return (
    <div className="space-y-6 flex flex-col h-full min-w-0 select-none animate-page-enter">
      
      {/* Page Header */}
      <div className="flex justify-between items-center bg-bg-surface border border-border rounded-card p-5 shadow-md">
        <div className="space-y-1">
          <h2 className="text-sm font-bold text-text-primary uppercase tracking-wider">Camera Management</h2>
          <p className="text-xs text-text-secondary">Register local webcams, RTSP streams, or local files for inference</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-1.5 px-4 py-2 bg-accent-blue hover:bg-accent-blue/80 text-text-primary text-xs font-bold rounded-btn cursor-pointer shadow-md hover:shadow-[0_0_15px_rgba(59,130,246,0.3)] transition-all duration-200"
        >
          <Plus className="w-4 h-4" />
          <span>Add Camera</span>
        </button>
      </div>

      {/* Grid of Cameras */}
      {loading && cameras.length === 0 ? (
        <div className="h-[300px] flex items-center justify-center text-text-muted">
          <span className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-blue"></span>
        </div>
      ) : cameras.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cameras.map((camera) => {
            const isLive = camera.status === "Live";
            
            return (
              <div 
                key={camera.id}
                className="bg-bg-surface border border-border hover:border-border-bright rounded-card overflow-hidden shadow-md flex flex-col justify-between transition-all duration-200 group"
              >
                {/* Mock Thumbnail Screen */}
                <div className="h-[160px] bg-bg-base relative flex items-center justify-center border-b border-border">
                  <div className="absolute inset-0 bg-dot-grid opacity-20 pointer-events-none"></div>
                  
                  {isLive ? (
                    <>
                      {/* Bouncing sonar radar visual */}
                      <div className="absolute top-4 left-4 flex items-center gap-2 bg-bg-surface/85 backdrop-blur-md px-2 py-1 rounded-btn text-[9px] font-mono tracking-widest text-severity-critical border border-severity-critical/20 select-none">
                        <span className="relative flex h-2 w-2">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-severity-critical opacity-75"></span>
                          <span className="relative inline-flex rounded-full h-2 w-2 bg-severity-critical"></span>
                        </span>
                        <span>FEED ACTIVE</span>
                      </div>
                      
                      <div className="flex flex-col items-center gap-2 text-text-muted text-center p-4">
                        <Camera className="w-10 h-10 text-border-bright group-hover:scale-110 transition-transform duration-200" />
                        <span className="text-[10px] uppercase font-bold tracking-wider text-text-secondary">
                          {camera.resolution} @ {camera.fps} FPS
                        </span>
                      </div>
                    </>
                  ) : (
                    <div className="flex flex-col items-center gap-2 text-severity-critical text-center p-4">
                      <AlertTriangle className="w-10 h-10 animate-bounce" />
                      <span className="text-[10px] uppercase font-bold tracking-widest">FEED OFFLINE</span>
                    </div>
                  )}
                </div>

                {/* Body details */}
                <div className="p-5 space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-extrabold text-text-primary truncate">
                      {camera.name}
                    </h3>
                    <span 
                      className={`text-[9px] font-black tracking-widest px-2 py-0.5 rounded-badge uppercase border ${
                        isLive 
                          ? "bg-severity-low/10 border-severity-low/30 text-severity-low" 
                          : "bg-severity-critical/10 border-severity-critical/30 text-severity-critical"
                      }`}
                    >
                      {camera.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-xs font-mono bg-bg-base/40 border border-border/40 rounded-btn p-3">
                    <div>
                      <span className="text-[10px] text-text-muted font-sans font-medium uppercase block">Source</span>
                      <span className="text-text-primary font-bold truncate block" title={camera.source}>
                        {camera.source.length > 15 ? `${camera.source.substr(0, 12)}...` : camera.source}
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-text-muted font-sans font-medium uppercase block">ID Tag</span>
                      <span className="text-accent-cyan font-bold block">{camera.id.toUpperCase()}</span>
                    </div>
                  </div>
                </div>

                {/* Footer Controls */}
                <div className="px-5 py-3.5 border-t border-border bg-bg-surface/50 flex justify-end gap-3">
                  <button
                    onClick={() => handleDelete(camera.id)}
                    className="flex items-center gap-1.5 text-xs text-text-muted hover:text-severity-critical hover:bg-severity-critical/10 px-3 py-1.5 rounded-btn border border-border hover:border-severity-critical/20 transition-all duration-200 cursor-pointer shadow-sm"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Delete</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* Empty grid list state */
        <div className="h-[300px] bg-bg-surface border border-border rounded-card flex flex-col items-center justify-center text-center p-6 select-none animate-page-enter">
          <Wifi className="w-12 h-12 text-text-muted mb-3" />
          <h3 className="text-sm font-bold text-text-primary mb-1">No Camera Feeds</h3>
          <p className="text-xs text-text-muted">Register a webcam or file stream to run inference pipelines.</p>
        </div>
      )}

      {/* ADD CAMERA MODAL OVERLAY */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-bg-base/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-bg-surface border border-border rounded-card w-full max-w-md overflow-hidden shadow-2xl animate-page-enter flex flex-col">
            
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-border flex items-center justify-between">
              <h2 className="text-sm font-bold text-text-primary uppercase tracking-wider">Register Camera Feed</h2>
              <button 
                onClick={() => setIsModalOpen(false)}
                className="text-text-muted hover:text-text-primary hover:bg-bg-elevated p-1 rounded-btn transition-colors duration-200"
              >
                ×
              </button>
            </div>

            {/* Modal Form */}
            <form onSubmit={handleSave} className="p-6 space-y-5">
              
              {/* Camera Name */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-text-secondary tracking-wide block">Camera Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-bg-base border border-border focus:border-accent-blue rounded-input py-2 px-3 text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-accent-blue transition-colors font-medium placeholder-text-muted"
                  placeholder="e.g. Front Gate Monitor"
                />
              </div>

              {/* Source Type Toggles */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-text-secondary tracking-wide block">Feed Source Type</label>
                <div className="grid grid-cols-3 gap-2 bg-bg-base border border-border p-1 rounded-btn text-center text-xs font-semibold select-none">
                  <button
                    type="button"
                    onClick={() => handleSourceTypeChange("webcam")}
                    className={`py-1.5 rounded-btn cursor-pointer transition-all duration-200 ${
                      sourceType === "webcam" ? "bg-bg-elevated text-accent-blue" : "text-text-secondary hover:text-text-primary"
                    }`}
                  >
                    Webcam
                  </button>
                  <button
                    type="button"
                    onClick={() => handleSourceTypeChange("rtsp")}
                    className={`py-1.5 rounded-btn cursor-pointer transition-all duration-200 ${
                      sourceType === "rtsp" ? "bg-bg-elevated text-accent-blue" : "text-text-secondary hover:text-text-primary"
                    }`}
                  >
                    RTSP URL
                  </button>
                  <button
                    type="button"
                    onClick={() => handleSourceTypeChange("file")}
                    className={`py-1.5 rounded-btn cursor-pointer transition-all duration-200 ${
                      sourceType === "file" ? "bg-bg-elevated text-accent-blue" : "text-text-secondary hover:text-text-primary"
                    }`}
                  >
                    Local File
                  </button>
                </div>
              </div>

              {/* Source Input */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-text-secondary tracking-wide block">
                  {sourceType === "file" ? "Upload Video File" : "Source Address / Index"}
                </label>
                {sourceType === "file" && !source ? (
                  <input
                    type="file"
                    accept="video/*"
                    required
                    onChange={(e) => {
                      if (e.target.files.length > 0) {
                        setSelectedFile(e.target.files[0]);
                      }
                      setTestResult(null);
                    }}
                    className="w-full bg-bg-base border border-border focus:border-accent-blue rounded-input py-2 px-3 text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-accent-blue transition-colors font-medium placeholder-text-muted"
                  />
                ) : (
                  <input
                    type="text"
                    required
                    value={source}
                    onChange={(e) => {
                      setSource(e.target.value);
                      setTestResult(null);
                    }}
                    className="w-full bg-bg-base border border-border focus:border-accent-blue rounded-input py-2 px-3 text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-accent-blue transition-colors font-medium font-mono placeholder-text-muted"
                    placeholder={
                      sourceType === "webcam" ? "0 or 1" : sourceType === "rtsp" ? "rtsp://..." : "path/to/video.mp4"
                    }
                  />
                )}
              </div>

              {/* Connection Test feedback */}
              {testResult && (
                <div className={`p-3 rounded-btn text-xs font-medium flex items-center gap-2 border ${
                  testResult === "success" 
                    ? "bg-severity-low/10 border-severity-low/30 text-severity-low" 
                    : "bg-severity-critical/10 border-severity-critical/30 text-severity-critical"
                }`}>
                  {testResult === "success" ? (
                    <>
                      <CheckCircle className="w-4 h-4 shrink-0" />
                      <span>Pipeline connection verified! Stream resolved.</span>
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="w-4 h-4 shrink-0" />
                      <span>Inference test failed. Check path address.</span>
                    </>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center justify-between border-t border-border/40 pt-4">
                <button
                  type="button"
                  onClick={handleTestConnection}
                  disabled={isTesting || isUploading}
                  className="flex items-center gap-1.5 text-xs text-text-secondary hover:text-text-primary border border-border hover:border-border-bright hover:bg-bg-elevated/40 px-3.5 py-2 rounded-btn transition-colors duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {(isTesting || isUploading) ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : null}
                  <span>{isUploading ? "Uploading..." : "Test Connection"}</span>
                </button>

                <div className="flex gap-2.5">
                  <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="px-3.5 py-2 border border-border text-xs text-text-secondary hover:text-text-primary rounded-btn hover:bg-bg-elevated/40 transition-colors duration-200 cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isTesting || isUploading}
                    className="px-5 py-2 bg-accent-blue text-text-primary text-xs font-bold rounded-btn cursor-pointer shadow-md hover:shadow-[0_0_15px_rgba(59,130,246,0.3)] transition-all duration-200 disabled:opacity-50"
                  >
                    {isUploading ? "Uploading..." : "Save Feed"}
                  </button>
                </div>
              </div>

            </form>
          </div>
        </div>
      )}

    </div>
  );
}
