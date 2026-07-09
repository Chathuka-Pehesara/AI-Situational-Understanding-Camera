import React, { useState, useEffect } from "react";
import { ShieldAlert, Video, BrainCircuit, Activity } from "lucide-react";

// CountUp helper component using requestAnimationFrame
function CountUp({ end, duration = 1000, suffix = "" }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime = null;
    const endVal = parseFloat(end) || 0;

    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = timestamp - startTime;
      const rate = Math.min(progress / duration, 1);
      
      setCount(Math.floor(rate * endVal));

      if (rate < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [end, duration]);

  return <span>{count}{suffix}</span>;
}

export default function StatsRow({ alertsCount, activeCameras, riskLevel, avgConfidence }) {
  
  // Format risk level color
  const getRiskColor = (lvl) => {
    if (lvl === "High") return "text-severity-high shadow-[0_0_15px_rgba(249,115,22,0.15)]";
    if (lvl === "Medium") return "text-severity-medium shadow-[0_0_15px_rgba(234,179,8,0.15)]";
    if (lvl === "Low") return "text-severity-low shadow-[0_0_15px_rgba(34,197,94,0.15)]";
    return "text-text-secondary";
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 select-none animate-page-enter">
      
      {/* Total Alerts Today */}
      <div className="bg-bg-surface border border-border rounded-card p-5 flex items-center justify-between stat-card-hover group">
        <div className="space-y-1">
          <span className="text-xs text-text-secondary font-semibold uppercase tracking-wider">Alerts Today</span>
          <div className="text-3xl font-black text-text-primary">
            <CountUp end={alertsCount} />
          </div>
        </div>
        <div className="p-3 bg-severity-critical/10 border border-severity-critical/20 rounded-btn text-severity-critical group-hover:scale-110 transition-transform duration-200">
          <ShieldAlert className="w-6 h-6 animate-pulse" />
        </div>
      </div>

      {/* Current Risk Level */}
      <div className="bg-bg-surface border border-border rounded-card p-5 flex items-center justify-between stat-card-hover group">
        <div className="space-y-1">
          <span className="text-xs text-text-secondary font-semibold uppercase tracking-wider">System Threat Level</span>
          <div className={`text-2xl font-black ${getRiskColor(riskLevel)}`}>
            {riskLevel ? riskLevel.toUpperCase() : "LOW"}
          </div>
        </div>
        <div className="p-3 bg-accent-purple/10 border border-accent-purple/20 rounded-btn text-accent-purple group-hover:scale-110 transition-transform duration-200">
          <Activity className="w-6 h-6" />
        </div>
      </div>

      {/* Active Cameras */}
      <div className="bg-bg-surface border border-border rounded-card p-5 flex items-center justify-between stat-card-hover group">
        <div className="space-y-1">
          <span className="text-xs text-text-secondary font-semibold uppercase tracking-wider">Active Cameras</span>
          <div className="text-3xl font-black text-text-primary">
            <CountUp end={activeCameras} />
          </div>
        </div>
        <div className="p-3 bg-accent-cyan/10 border border-accent-cyan/20 rounded-btn text-accent-cyan group-hover:scale-110 transition-transform duration-200">
          <Video className="w-6 h-6" />
        </div>
      </div>

      {/* Gemini Confidence */}
      <div className="bg-bg-surface border border-border rounded-card p-5 flex items-center justify-between stat-card-hover group">
        <div className="space-y-1">
          <span className="text-xs text-text-secondary font-semibold uppercase tracking-wider">Avg AI Confidence</span>
          <div className="text-3xl font-black text-text-primary">
            <CountUp end={avgConfidence} suffix="%" />
          </div>
        </div>
        <div className="p-3 bg-accent-purple/10 border border-accent-purple/20 rounded-btn text-accent-purple group-hover:scale-110 transition-transform duration-200">
          <BrainCircuit className="w-6 h-6" />
        </div>
      </div>

    </div>
  );
}
