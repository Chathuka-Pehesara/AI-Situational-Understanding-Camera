import React from "react";
import { 
  LayoutDashboard, 
  ShieldAlert, 
  BarChart3, 
  Video, 
  MessageSquareCode, 
  LogOut, 
  GraduationCap 
} from "lucide-react";

export default function Sidebar({ currentPage, setCurrentPage, onLogout, systemStatus }) {
  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "incidents", label: "Incidents", icon: ShieldAlert },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "cameras", label: "Cameras", icon: Video },
    { id: "ask-footage", label: "Ask Footage", icon: MessageSquareCode },
  ];

  return (
    <div className="w-[240px] h-screen bg-bg-surface border-r border-border flex flex-col justify-between select-none shrink-0">
      <div>
        {/* Logo Section */}
        <div className="h-[64px] border-b border-border flex items-center px-6 gap-3">
          <GraduationCap className="w-7 h-7 text-accent-blue" />
          <span className="font-extrabold text-lg bg-gradient-to-r from-accent-blue via-accent-purple to-accent-cyan bg-clip-text text-transparent">
            SituVision AI
          </span>
        </div>

        {/* Live System Indicator */}
        <div className="px-6 py-4 flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-severity-low opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-severity-low"></span>
          </span>
          <span className="text-xs text-text-secondary font-medium tracking-wide">
            System Status: <span className="text-severity-low font-bold">Active</span>
          </span>
        </div>

        {/* Navigation Menu */}
        <nav className="mt-2 px-3 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentPage(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-btn text-sm font-medium transition-all duration-200 relative group overflow-hidden ${
                  isActive
                    ? "bg-bg-elevated text-text-primary"
                    : "text-text-secondary hover:bg-bg-elevated/40 hover:text-text-primary"
                }`}
              >
                {/* Active left border indicator slide in */}
                {isActive && (
                  <span className="absolute left-0 top-0 w-1 h-full bg-accent-blue animate-[border-slide_0.2s_ease-out_forwards]" />
                )}
                
                <Icon className={`w-5 h-5 transition-transform duration-200 group-hover:scale-110 ${
                  isActive ? "text-accent-blue" : "text-text-muted group-hover:text-text-secondary"
                }`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* User Section at Bottom */}
      <div className="p-4 border-t border-border bg-bg-surface flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-accent-purple/20 border border-accent-purple/50 flex items-center justify-center font-bold text-accent-purple text-sm select-none shadow-[0_0_10px_rgba(139,92,246,0.15)]">
            OP
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-semibold text-text-primary leading-tight">Operator 01</span>
            <span className="text-[10px] text-text-muted leading-tight">Chief Proctor</span>
          </div>
        </div>
        <button
          onClick={onLogout}
          title="Sign Out"
          className="p-2 rounded-btn text-text-muted hover:text-severity-critical hover:bg-severity-critical/10 transition-colors duration-200"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
