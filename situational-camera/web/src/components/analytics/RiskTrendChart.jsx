import React from "react";
import { 
  PieChart, 
  Pie, 
  Cell, 
  Tooltip, 
  ResponsiveContainer, 
  Legend 
} from "recharts";

export default function RiskTrendChart({ data = [] }) {
  const COLORS = {
    High: "#F97316",    // Orange
    Medium: "#EAB308",  // Yellow
    Low: "#22C55E",     // Green
    None: "#64748B"     // Muted Blue
  };

  return (
    <div className="bg-bg-surface border border-border rounded-card p-5 h-[340px] flex flex-col shadow-lg select-none">
      <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-4">
        Threat Distribution
      </h3>

      <div className="flex-1 w-full text-xs">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="45%"
              innerRadius={60}
              outerRadius={85}
              paddingAngle={4}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={COLORS[entry.name] || COLORS.None} 
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "#0F1629",
                borderColor: "#1E3058",
                borderRadius: "10px",
                color: "#E8EEFF"
              }}
            />
            <Legend verticalAlign="bottom" height={36} iconType="circle" />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
