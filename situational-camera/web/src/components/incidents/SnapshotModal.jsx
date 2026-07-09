import React, { useState } from "react";
import { X, Download, ShieldCheck, Eye, EyeOff, Brain } from "lucide-react";
import { getSeverity } from "../../lib/constants";

export default function SnapshotModal({ isOpen, onClose, incident }) {
  const [showJson, setShowJson] = useState(false);
  
  if (!isOpen || !incident) return null;

  const sev = getSeverity(incident.situation, incident.risk);

  // Generate a mock surveillance frame drawing or static graphic representation
  const downloadSnapshot = () => {
    // Generate a simple dummy image download
    const canvas = document.createElement("canvas");
    canvas.width = 640;
    canvas.height = 480;
    const ctx = canvas.getContext("2d");
    
    // Draw background
    ctx.fillStyle = "#0A0E1A";
    ctx.fillRect(0, 0, 640, 480);
    
    // Draw scan line grid
    ctx.strokeStyle = "rgba(59, 130, 246, 0.1)";
    ctx.lineWidth = 1;
    for (let i = 0; i < 640; i += 30) {
      ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, 480); ctx.stroke();
    }
    for (let j = 0; j < 480; j += 30) {
      ctx.beginPath(); ctx.moveTo(0, j); ctx.lineTo(640, j); ctx.stroke();
    }
    
    // Draw metadata
    ctx.fillStyle = sev.color;
    ctx.font = "bold 20px sans-serif";
    ctx.fillText("SITUVISION AI INCIDENT LOG", 40, 60);
    
    ctx.fillStyle = "#8A9BC4";
    ctx.font = "14px monospace";
    ctx.fillText(`TIMESTAMP: ${incident.timestamp}`, 40, 100);
    ctx.fillText(`SITUATION: ${incident.situation}`, 40, 130);
    ctx.fillText(`SEVERITY:  ${sev.label}`, 40, 160);
    
    // Mock graphic bounding boxes
    ctx.strokeStyle = sev.color;
    ctx.lineWidth = 3;
    ctx.strokeRect(180, 120, 280, 260);
    ctx.fillStyle = sev.color;
    ctx.fillRect(180, 95, 120, 25);
    ctx.fillStyle = "#0A0E1A";
    ctx.font = "bold 12px monospace";
    ctx.fillText(incident.situation.toUpperCase(), 188, 112);

    const link = document.createElement("a");
    link.download = `incident-${incident.timestamp.replace(/[: ]/g, "-")}.png`;
    link.href = canvas.toDataURL("image/png");
    link.click();
  };

  const getScoreColor = (score, maxVal = 10) => {
    const ratio = score / maxVal;
    if (ratio >= 0.8) return "text-severity-low";
    if (ratio >= 0.5) return "text-severity-medium";
    return "text-severity-critical";
  };

  // Generate a mock raw json schema matching detection contracts
  const rawJson = {
    timestamp: incident.timestamp,
    situation: incident.situation,
    risk_level: incident.risk,
    gemini_verification: {
      verified: incident.gemini_verified,
      confidence: incident.gemini_confidence || 0.5
    },
    metrics: {
      safety_score: incident.safety_score,
      focus_score: incident.focus_score
    },
    inferred_detections: [
      {
        label: incident.situation.includes("Weapon") ? "knife" : "person",
        bbox: [180, 120, 460, 380],
        confidence: incident.gemini_confidence || 0.85
      }
    ]
  };

  return (
    <div className="fixed inset-0 bg-bg-base/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 select-none">
      
      {/* Modal Dialog Card */}
      <div className="bg-bg-surface border border-border rounded-card w-full max-w-3xl overflow-hidden shadow-2xl animate-page-enter flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-accent-blue" />
            <h2 className="text-sm font-bold text-text-primary uppercase tracking-wider">Incident Report</h2>
          </div>
          <button 
            onClick={onClose}
            className="p-1 text-text-muted hover:text-text-primary hover:bg-bg-elevated rounded-btn transition-colors duration-200"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Scroll area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* Main Visual Placeholder */}
          <div className="h-[280px] bg-bg-base rounded-btn border border-border flex flex-col items-center justify-center p-6 relative overflow-hidden group">
            <div className="absolute inset-0 bg-dot-grid opacity-30"></div>
            
            {/* Visual threat box rendering */}
            <div className="w-64 h-40 border-2 border-dashed border-border-bright rounded flex flex-col items-center justify-center text-center p-4 bg-bg-surface/50 relative z-10">
              <div 
                style={{ borderColor: sev.color }} 
                className="absolute inset-2 border-2 rounded flex flex-col items-center justify-center"
              >
                <span style={{ color: sev.color }} className="text-xs font-mono font-bold tracking-widest uppercase mb-1">
                  {incident.situation}
                </span>
                <span className="text-[10px] text-text-secondary font-mono">
                  {incident.timestamp}
                </span>
              </div>
            </div>

            <button 
              onClick={downloadSnapshot}
              className="absolute bottom-4 right-4 bg-bg-surface hover:bg-bg-elevated text-text-primary border border-border px-3 py-1.5 rounded-btn text-xs font-bold transition-all duration-200 flex items-center gap-1.5 cursor-pointer shadow-md"
            >
              <Download className="w-4 h-4" />
              <span>Download Snapshot</span>
            </button>
          </div>

          {/* Explanation Text */}
          <div className="space-y-2">
            <span className="text-[10px] uppercase font-bold tracking-wider text-text-muted">Gemini Verdict</span>
            <p className="text-text-primary text-sm leading-relaxed bg-bg-base border border-border/60 rounded-btn p-4">
              {incident.explanation || "No text description matches this incident entry."}
            </p>
          </div>

          {/* Metrics & Scores */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Focus Score */}
            <div className="bg-bg-base border border-border rounded-btn p-4 flex flex-col items-center justify-center text-center">
              <span className="text-[10px] uppercase font-bold tracking-wider text-text-muted mb-1">Focus Score</span>
              <span className={`text-2xl font-black ${getScoreColor(incident.focus_score, 100)}`}>
                {incident.focus_score}%
              </span>
            </div>

            {/* Safety Score */}
            <div className="bg-bg-base border border-border rounded-btn p-4 flex flex-col items-center justify-center text-center">
              <span className="text-[10px] uppercase font-bold tracking-wider text-text-muted mb-1">Safety Level</span>
              <span className={`text-2xl font-black ${getScoreColor(incident.safety_score, 10)}`}>
                {incident.safety_score}/10
              </span>
            </div>

            {/* Gemini Confidence */}
            <div className="bg-bg-base border border-border rounded-btn p-4 flex flex-col items-center justify-center text-center">
              <span className="text-[10px] uppercase font-bold tracking-wider text-text-muted mb-1">Gemini confidence</span>
              <span className="text-2xl font-black text-accent-purple font-mono">
                {incident.gemini_confidence ? incident.gemini_confidence.toFixed(2) : "0.50"}
              </span>
            </div>
          </div>

          {/* Raw JSON Collapse area */}
          <div className="border border-border rounded-btn overflow-hidden">
            <button
              onClick={() => setShowJson(!showJson)}
              className="w-full bg-bg-base/60 hover:bg-bg-base px-4 py-3 flex items-center justify-between text-xs font-semibold text-text-secondary transition-colors duration-200"
            >
              <div className="flex items-center gap-2">
                <Brain className="w-4 h-4 text-accent-purple" />
                <span>Raw Cognitive Frame Metadata</span>
              </div>
              {showJson ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
            {showJson && (
              <pre className="bg-bg-base p-4 overflow-x-auto text-[10px] text-accent-cyan font-mono border-t border-border select-text">
                {JSON.stringify(rawJson, null, 2)}
              </pre>
            )}
          </div>

        </div>

      </div>
      
    </div>
  );
}
