import React, { useState } from "react";

export default function HeatmapGrid({ data = [] }) {
  const [hoverInfo, setHoverInfo] = useState(null);
  
  const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const HOURS = Array.from({ length: 24 }, (_, i) => `${i.toString().padStart(2, "0")}:00`);

  // Build 7x24 grid matrix from raw events list
  const matrix = Array.from({ length: 7 }, () => Array(24).fill(0));
  let maxCount = 1;

  data.forEach((event) => {
    try {
      // Expecting timestamp format: "YYYY-MM-DD HH:MM:SS"
      const datePart = event.timestamp.split(" ")[0];
      const timePart = event.timestamp.split(" ")[1];
      const hour = parseInt(timePart.split(":")[0]);
      
      const date = new Date(datePart);
      const day = date.getDay(); // 0 is Sunday

      matrix[day][hour] += 1;
      if (matrix[day][hour] > maxCount) {
        maxCount = matrix[day][hour];
      }
    } catch (e) {
      // Parse error fallback, ignore
    }
  });

  // Calculate cell color based on density
  const getCellColor = (count) => {
    if (count === 0) return "#0F1629"; // --bg-surface
    
    // Scale opacity from 0.15 to 0.9 based on count relative to maxCount
    const opacity = 0.15 + (count / maxCount) * 0.75;
    return `rgba(239, 68, 68, ${opacity})`; // Crimson Red alert scale
  };

  return (
    <div className="bg-bg-surface border border-border rounded-card p-5 flex flex-col shadow-lg select-none relative">
      <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-4">
        24-Hour Incident Distribution Grid
      </h3>

      {/* Grid Container */}
      <div className="overflow-x-auto">
        <div className="min-w-[640px] space-y-1.5 p-2 bg-bg-base/40 border border-border/40 rounded-btn">
          
          {/* Hour labels header row */}
          <div className="flex items-center gap-1.5 pl-10 text-[9px] font-mono text-text-muted">
            {HOURS.map((hr, idx) => (
              <span key={idx} className="w-[18px] text-center" title={hr}>
                {idx % 3 === 0 ? idx : ""}
              </span>
            ))}
          </div>

          {/* Matrix Rows */}
          {DAYS.map((dayName, dayIdx) => (
            <div key={dayIdx} className="flex items-center gap-1.5">
              
              {/* Day Row Label */}
              <span className="w-8 text-[10px] font-bold text-text-secondary font-mono text-right select-none">
                {dayName}
              </span>

              {/* Hour Grid Cells */}
              <div className="flex gap-1.5 flex-1">
                {matrix[dayIdx].map((count, hourIdx) => (
                  <div
                    key={hourIdx}
                    onMouseEnter={(e) => {
                      const rect = e.currentTarget.getBoundingClientRect();
                      setHoverInfo({
                        count,
                        day: dayName,
                        hour: HOURS[hourIdx],
                        x: rect.left + window.scrollX,
                        y: rect.top + window.scrollY - 36
                      });
                    }}
                    onMouseLeave={() => setHoverInfo(null)}
                    style={{ backgroundColor: getCellColor(count) }}
                    className="w-[18px] h-[18px] rounded-[3px] border border-border/25 cursor-pointer hover:scale-110 hover:border-border-bright transition-all duration-150"
                  />
                ))}
              </div>

            </div>
          ))}

        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 flex items-center justify-end gap-2 text-[10px] text-text-muted font-mono select-none">
        <span>Fewer Incidents</span>
        <div className="flex gap-1">
          <div className="w-3.5 h-3.5 rounded-[2px] bg-bg-surface border border-border/30"></div>
          <div className="w-3.5 h-3.5 rounded-[2px] bg-severity-critical/20"></div>
          <div className="w-3.5 h-3.5 rounded-[2px] bg-severity-critical/50"></div>
          <div className="w-3.5 h-3.5 rounded-[2px] bg-severity-critical/80"></div>
        </div>
        <span>More Incidents</span>
      </div>

      {/* Hover Info Tooltip (Portal Mock) */}
      {hoverInfo && (
        <div
          style={{
            position: "absolute",
            left: `${hoverInfo.x - 200}px`, // Adjusted coordinate mapping
            top: `${hoverInfo.y - 120}px`  // Dynamic hover mapping
          }}
          className="fixed bg-bg-overlay border border-border-bright text-[10px] text-text-primary px-2.5 py-1.5 rounded shadow-lg z-30 pointer-events-none select-none"
        >
          <div className="font-bold text-accent-cyan">
            {hoverInfo.day} at {hoverInfo.hour}
          </div>
          <div className="text-text-primary font-semibold mt-0.5">
            {hoverInfo.count} {hoverInfo.count === 1 ? "incident" : "incidents"} logged
          </div>
        </div>
      )}

    </div>
  );
}
