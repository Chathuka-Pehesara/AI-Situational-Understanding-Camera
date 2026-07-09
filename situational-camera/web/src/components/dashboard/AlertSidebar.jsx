import React from "react";
import { CheckCircle2, Trash2 } from "lucide-react";
import { getSeverity } from "../../lib/constants";

export default function AlertSidebar({ alerts = [], onClear, isClearing = false }) {
  const activeAlerts = alerts.filter((a) => a.status === "active");

  const formatTime = (isoString) => {
    try {
      const dt = new Date(isoString);
      return dt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="w-[350px] bg-bg-surface border border-border rounded-card flex flex-col h-full shadow-lg shrink-0">
      
      {/* Header */}
      <div className="px-5 py-4 border-b border-border flex items-center justify-between select-none">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-bold text-text-primary uppercase tracking-wider">Live Alerts</h2>
          {activeAlerts.length > 0 && (
            <span className="bg-severity-critical/15 text-severity-critical text-[10px] font-black px-2 py-0.5 rounded-full">
              {activeAlerts.length}
            </span>
          )}
        </div>
        
        {activeAlerts.length > 0 && (
          <button
            onClick={onClear}
            disabled={isClearing}
            className="flex items-center gap-1.5 text-xs text-text-muted hover:text-severity-critical hover:bg-severity-critical/10 px-2 py-1 rounded-btn transition-all duration-200"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear</span>
          </button>
        )}
      </div>

      {/* Alerts Content Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {activeAlerts.length > 0 ? (
          activeAlerts.map((alert) => {
            const sev = getSeverity(alert.situation, alert.risk);
            const isCritical = sev.label === "CRITICAL";

            return (
              <div
                key={alert.id}
                style={{ borderLeftColor: sev.color }}
                className={`bg-bg-base border border-border rounded-btn p-4 border-l-4 relative overflow-hidden transition-all duration-300 hover:border-border-bright hover:shadow-md animate-slide-in-right group ${
                  isCritical ? "animate-glow-critical" : ""
                }`}
              >
                {/* Alert Badge + Time */}
                <div className="flex items-center justify-between mb-2">
                  <span
                    style={{
                      backgroundColor: sev.bgColor,
                      color: sev.textColor,
                      borderColor: sev.borderColor,
                    }}
                    className="text-[9px] font-black tracking-widest px-2 py-0.5 rounded-badge border uppercase"
                  >
                    {sev.label}
                  </span>
                  <span className="text-[10px] text-text-muted font-mono">
                    {formatTime(alert.timestamp)}
                  </span>
                </div>

                {/* Situation */}
                <h3 className="text-sm font-extrabold text-text-primary mb-1">
                  {alert.situation}
                </h3>

                {/* Explanation */}
                <p className="text-xs text-text-secondary line-clamp-2 leading-relaxed">
                  {alert.explanation}
                </p>

                {/* Optional camera tags */}
                {alert.camera_name && (
                  <div className="mt-3 text-[9px] text-text-muted font-mono flex items-center gap-1">
                    <span className="h-1 w-1 bg-text-muted rounded-full"></span>
                    <span>FEED: {alert.camera_name.toUpperCase()}</span>
                  </div>
                )}
              </div>
            );
          })
        ) : (
          /* Empty All Clear state */
          <div className="h-full flex flex-col items-center justify-center text-center p-6 select-none animate-page-enter">
            <div className="w-12 h-12 bg-severity-low/10 border border-severity-low/20 text-severity-low rounded-full flex items-center justify-center mb-3 shadow-[0_0_15px_rgba(34,197,94,0.1)]">
              <CheckCircle2 className="w-6 h-6 animate-pulse" />
            </div>
            <h3 className="text-sm font-bold text-text-primary mb-1">System Secure</h3>
            <p className="text-xs text-text-muted">No active incidents detected. Monitor is clean.</p>
          </div>
        )}
      </div>

    </div>
  );
}
