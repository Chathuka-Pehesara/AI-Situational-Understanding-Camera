import React, { useState, useEffect } from "react";
import { Bell, ShieldAlert, Cpu } from "lucide-react";

export default function TopBar({ title, activeCameraCount = 0, unreadAlertCount = 0 }) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (dt) => {
    return dt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
  };

  const formatDate = (dt) => {
    return dt.toLocaleDateString([], { weekday: "short", month: "short", day: "numeric" });
  };

  return (
    <header className="h-[64px] bg-bg-surface border-b border-border flex items-center justify-between px-8 select-none shrink-0">
      {/* Page Title */}
      <div className="flex items-center gap-3">
        <h1 className="text-xl font-bold text-text-primary capitalize">{title}</h1>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-6">
        {/* Active Cameras chip */}
        <div className="flex items-center gap-2 bg-bg-elevated/60 border border-border px-3 py-1.5 rounded-btn text-xs text-text-secondary">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-cyan opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-cyan"></span>
          </span>
          <span>
            {activeCameraCount} {activeCameraCount === 1 ? "Camera" : "Cameras"} Active
          </span>
        </div>

        {/* Live Clock & Date */}
        <div className="flex items-baseline gap-2 bg-bg-elevated/40 border border-border/60 px-3 py-1.5 rounded-btn text-xs text-text-secondary font-medium">
          <span className="text-text-primary font-semibold">{formatDate(time)}</span>
          <span className="text-text-muted">|</span>
          <span className="font-mono text-accent-cyan tracking-wider font-semibold">{formatTime(time)}</span>
        </div>

        {/* Alerts Bell notification */}
        <div className="relative cursor-pointer group">
          <div className="p-2 bg-bg-elevated/40 hover:bg-bg-elevated border border-border hover:border-border-bright rounded-btn text-text-secondary hover:text-text-primary transition-all duration-200">
            <Bell className="w-5 h-5" />
          </div>
          {unreadAlertCount > 0 && (
            <span className="absolute -top-1.5 -right-1.5 bg-severity-critical text-text-primary text-[10px] font-bold px-1.5 py-0.5 rounded-full ring-2 ring-bg-surface animate-[pulse-live_1.5s_infinite]">
              {unreadAlertCount}
            </span>
          )}
        </div>
      </div>
    </header>
  );
}
