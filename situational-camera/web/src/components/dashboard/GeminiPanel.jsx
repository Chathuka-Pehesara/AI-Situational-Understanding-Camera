import React from "react";
import { Brain, ShieldAlert, BadgeCheck } from "lucide-react";
import { getSeverity } from "../../lib/constants";

export default function GeminiPanel({ situation, risk, explanation, confidence, geminiVerified }) {
  const sev = getSeverity(situation, risk);
  const confidencePercent = confidence ? Math.round(confidence * 100) : 50;

  return (
    <div className="bg-bg-surface border border-border rounded-card p-6 shadow-lg select-none animate-page-enter">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-5 border-b border-border/40 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-btn bg-accent-purple/20 border border-accent-purple/40 flex items-center justify-center text-accent-purple shadow-[0_0_10px_rgba(139,92,246,0.2)]">
            <Brain className="w-4 h-4 animate-pulse" />
          </div>
          <h2 className="text-sm font-bold text-text-primary uppercase tracking-wider">Gemini Cognitive Insight</h2>
        </div>
        {geminiVerified && (
          <div className="flex items-center gap-1 bg-accent-purple/10 border border-accent- purple/30 text-accent-purple text-[10px] font-bold px-2 py-0.5 rounded-full select-none shadow-[0_0_10px_rgba(139,92,246,0.1)]">
            <BadgeCheck className="w-3.5 h-3.5" />
            <span>AI Verified</span>
          </div>
        )}
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

          {/* Confidence Slider Gauge */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="text-text-secondary font-medium">Assurance Level</span>
              <span className="font-mono text-accent-purple font-semibold">{confidencePercent}%</span>
            </div>
            <div className="h-2 w-full bg-bg-base border border-border rounded-full overflow-hidden">
              <div 
                style={{ width: `${confidencePercent}%` }}
                className="h-full bg-gradient-to-r from-accent-blue via-accent-purple to-accent-cyan rounded-full transition-all duration-1000 ease-out"
              />
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
            <span className="text-text-secondary font-medium">Confidence Score:</span>
            <span className="text-text-primary font-mono font-bold">
              {confidence ? confidence.toFixed(2) : "0.50"}
            </span>
          </div>
        </div>

      </div>

    </div>
  );
}
