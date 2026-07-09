import React from "react";
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Legend 
} from "recharts";

export default function AlertsChart({ data = [] }) {
  // Configured chart colors matching the dashboard CSS variables
  const colors = {
    High: "#F97316", // Orange
    Medium: "#EAB308", // Yellow
    Low: "#22C55E", // Green
  };

  return (
    <div className="bg-bg-surface border border-border rounded-card p-5 h-[340px] flex flex-col shadow-lg select-none">
      <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-4">
        Alerts Over Time (Last 7 Days)
      </h3>
      
      <div className="flex-1 w-full text-xs">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorHigh" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={colors.High} stopOpacity={0.2}/>
                <stop offset="95%" stopColor={colors.High} stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorMedium" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={colors.Medium} stopOpacity={0.2}/>
                <stop offset="95%" stopColor={colors.Medium} stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorLow" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={colors.Low} stopOpacity={0.2}/>
                <stop offset="95%" stopColor={colors.Low} stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E3058" opacity={0.3} />
            <XAxis 
              dataKey="date" 
              stroke="#8A9BC4" 
              fontSize={10}
              tickLine={false}
            />
            <YAxis 
              stroke="#8A9BC4" 
              fontSize={10}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0F1629",
                borderColor: "#1E3058",
                borderRadius: "10px",
                color: "#E8EEFF"
              }}
            />
            <Legend verticalAlign="top" height={36} iconType="circle" />
            <Area
              type="monotone"
              dataKey="High"
              stackId="1"
              stroke={colors.High}
              fillOpacity={1}
              fill="url(#colorHigh)"
            />
            <Area
              type="monotone"
              dataKey="Medium"
              stackId="1"
              stroke={colors.Medium}
              fillOpacity={1}
              fill="url(#colorMedium)"
            />
            <Area
              type="monotone"
              dataKey="Low"
              stackId="1"
              stroke={colors.Low}
              fillOpacity={1}
              fill="url(#colorLow)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
