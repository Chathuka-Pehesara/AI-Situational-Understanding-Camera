import React from "react";
import { Activity, ShieldAlert } from "lucide-react";
import { getSeverity } from "../../lib/constants";

export default function GeminiPanel({ situation, risk, explanation, confidence, geminiVerified, detections = [] }) {
  const sev = getSeverity(situation, risk);
  const confidencePercent = confidence ? Math.round(confidence * 100) : 50;

  // Calculate some valuable local metrics from detections
  const peopleCount = detections.filter(d => d.label === "person").length;
  const objectCount = detections.filter(d => d.label !== "person").length;
  
  const objectLabels = detections.filter(d => d.label !== "person").map(d => d.label);
  const uniqueObjects = [...new Set(objectLabels)];

  return (
    <div className="bg-bg-surface border border-border rounded-card p-6 shadow-lg select-none animate-page-enter">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-5 border-b border-border/40 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-btn bg-accent-blue/20 border border-accent-blue/40 flex items-center justify-center text-accent-blue shadow-[0_0_10px_rgba(59,130,246,0.2)]">
            <Activity className="w-4 h-4 animate-pulse" />
          </div>
          <h2 className="text-sm font-bold text-text-primary uppercase tracking-wider">Local Scene Intelligence</h2>
        </div>
      </div>

      {/* Grid Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
        
        {/* Left/Middle (2/3): Explanation & Details */}
        <div className="lg:col-span-2 space-y-4">
          <div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-text-muted">Current Assessment</span>
            <p className="text-lg font-semibold text-text-primary mt-1">
              {explanation || "Awaiting frame stream analysis..."}
            </p>
          </div>

          {/* Active Entities Summary */}
          <div className="flex items-center gap-4 text-xs mt-3">
            <div className="bg-bg-base px-3 py-1.5 rounded-btn border border-border flex items-center gap-2">
              <span className="text-text-muted">People Tracked:</span>
              <span className="font-bold text-accent-cyan">{peopleCount}</span>
            </div>
            <div className="bg-bg-base px-3 py-1.5 rounded-btn border border-border flex items-center gap-2">
              <span className="text-text-muted">Other Objects:</span>
              <span className="font-bold text-accent-purple">
                {uniqueObjects.length > 0 ? uniqueObjects.join(", ") : "None"} ({objectCount})
              </span>
            </div>
          </div>
        </div>

        {/* Right (1/3): Risk Details / Badges */}
        <div className="bg-bg-base border border-border rounded-btn p-4 space-y-3.5">
          <div className="flex justify-between items-center text-xs">
            <span className="text-text-secondary font-medium">Category:</span>
            <span className="text-text-primary font-bold">{situation || "Normal Activity"}</span>
          </div>
          
          <div className="flex justify-between items-center text-xs">
            <span className="text-text-secondary font-medium">Risk Priority:</span>
            <span 
              style={{
                backgroundColor: sev.bgColor,
                color: sev.textColor,
                borderColor: sev.borderColor,
              }}
              className="text-[10px] font-black px-2.5 py-0.5 rounded-badge border uppercase tracking-wider"
            >
              {risk || "Low"}
            </span>
          </div>

          <div className="flex justify-between items-center text-xs">
            <span className="text-text-secondary font-medium">Rule Confidence:</span>
            <span className="text-text-primary font-mono font-bold">
              {confidencePercent}%
            </span>
          </div>
        </div>

      </div>

    </div>
  );
}
