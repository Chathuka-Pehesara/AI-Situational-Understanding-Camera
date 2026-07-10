import React, { useEffect, useState } from "react";
import { 
  BarChart, 
  Bar, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Cell 
} from "recharts";
import { ShieldCheck, Flame, PieChart, TrendingUp, Filter } from "lucide-react";
import { api } from "../lib/api";
import { useCamera } from "../hooks/useCamera";
import AlertsChart from "../components/analytics/AlertsChart";
import RiskTrendChart from "../components/analytics/RiskTrendChart";
import HeatmapGrid from "../components/analytics/HeatmapGrid";

export default function Analytics() {
  const [allEvents, setAllEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const { cameras } = useCamera();
  const [selectedCameraId, setSelectedCameraId] = useState("all");

  useEffect(() => {
    const loadData = async (isInitial = false) => {
      try {
        if (isInitial) setLoading(true);
        // Fetch up to 1000 logged events for analysis
        const res = await api.getEvents(1, 1000);
        setAllEvents(res.events || []);
      } catch (err) {
        console.error("Error loading analytics data:", err);
      } finally {
        if (isInitial) setLoading(false);
      }
    };
    
    loadData(true);
    const interval = setInterval(() => loadData(false), 3000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="h-[400px] flex items-center justify-center text-text-muted select-none">
        <span className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-blue"></span>
      </div>
    );
  }

  // Filter events based on selected camera
  const events = selectedCameraId === "all" 
    ? allEvents 
    : allEvents.filter(e => e.camera_id === selectedCameraId);

  // 1. KPI Calculations
  const totalIncidents = events.length;
  
  // Average risk score calculation
  const getRiskScore = (risk) => {
    const r = risk.toLowerCase();
    if (r === "high") return 8;
    if (r === "medium") return 5;
    return 2;
  };
  const averageRiskScore = totalIncidents > 0 
    ? (events.reduce((acc, e) => acc + getRiskScore(e.risk), 0) / totalIncidents).toFixed(1)
    : "0.0";

  // Most common situation
  const situationCounts = {};
  events.forEach((e) => {
    situationCounts[e.situation] = (situationCounts[e.situation] || 0) + 1;
  });
  const mostCommonSituation = Object.entries(situationCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || "None";

  // 2. Prep Area Chart (Last 7 days alert counts)
  const getRecent7DaysData = () => {
    const data = [];
    const dateMap = {};
    
    // Initialize last 7 days
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split("T")[0]; // YYYY-MM-DD
      const label = date.toLocaleDateString([], { weekday: "short", month: "short", day: "numeric" });
      
      dateMap[dateStr] = { date: label, High: 0, Medium: 0, Low: 0 };
    }

    events.forEach((e) => {
      const dateStr = e.timestamp.split(" ")[0];
      if (dateMap[dateStr]) {
        const risk = e.risk.charAt(0).toUpperCase() + e.risk.slice(1).toLowerCase(); // Normalize case
        if (risk === "High" || risk === "Medium" || risk === "Low") {
          dateMap[dateStr][risk] += 1;
        }
      }
    });

    return Object.values(dateMap);
  };
  const alertsOverTimeData = getRecent7DaysData();

  // 3. Prep Pie Chart (Risk distribution counts)
  const getRiskDistributionData = () => {
    const distribution = { High: 0, Medium: 0, Low: 0 };
    events.forEach((e) => {
      const risk = e.risk.charAt(0).toUpperCase() + e.risk.slice(1).toLowerCase();
      if (distribution[risk] !== undefined) {
        distribution[risk] += 1;
      }
    });
    return Object.entries(distribution).map(([name, value]) => ({ name, value }));
  };
  const riskDistributionData = getRiskDistributionData();

  // 4. Prep Bar Chart (Top 8 situations frequency)
  const getTopSituationsData = () => {
    const list = Object.entries(situationCounts)
      .map(([name, value]) => ({ name, count: value }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 8);
    return list;
  };
  const topSituationsData = getTopSituationsData();

  // 5. Prep Line Chart (Gemini confidence logs)
  const getConfidenceTrendData = () => {
    // Take the last 50 events in chronological order (so reverse from events)
    const confidenceLogs = [...events]
      .slice(0, 50)
      .reverse()
      .map((e, idx) => ({
        index: idx + 1,
        confidence: e.gemini_confidence ? Math.round(e.gemini_confidence * 100) : 50
      }));
    return confidenceLogs;
  };
  const confidenceTrendData = getConfidenceTrendData();

  return (
    <div className="space-y-6 flex flex-col h-full min-w-0 select-none animate-page-enter">
      
      {/* Header with Camera Filter */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-black text-text-primary uppercase tracking-widest">Analytics Overview</h1>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-text-secondary text-xs uppercase tracking-wider font-bold">
            <Filter className="w-4 h-4" />
            <span>Filter Feed:</span>
          </div>
          <select
            value={selectedCameraId}
            onChange={(e) => setSelectedCameraId(e.target.value)}
            className="bg-bg-surface border border-border focus:border-accent-blue text-sm text-text-primary rounded-btn px-4 py-2 focus:outline-none cursor-pointer hover:bg-bg-elevated transition-colors duration-200 shadow-sm font-semibold"
          >
            <option value="all">ALL CAMERAS</option>
            {cameras.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* ROW 1: KPI CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Total Incidents */}
        <div className="bg-bg-surface border border-border rounded-card p-5 flex items-center justify-between stat-card-hover group">
          <div className="space-y-1">
            <span className="text-xs text-text-secondary font-semibold uppercase tracking-wider">Total logged events</span>
            <div className="text-3xl font-black text-text-primary">
              {totalIncidents}
            </div>
          </div>
          <div className="p-3 bg-accent-blue/10 border border-accent-blue/20 rounded-btn text-accent-blue group-hover:scale-110 transition-transform duration-200">
            <ShieldCheck className="w-6 h-6" />
          </div>
        </div>

        {/* Avg Risk Score */}
        <div className="bg-bg-surface border border-border rounded-card p-5 flex items-center justify-between stat-card-hover group">
          <div className="space-y-1">
            <span className="text-xs text-text-secondary font-semibold uppercase tracking-wider">Average Threat Level</span>
            <div className="text-3xl font-black text-text-primary">
              {averageRiskScore} <span className="text-xs text-text-muted font-normal">/ 10</span>
            </div>
          </div>
          <div className="p-3 bg-severity-high/10 border border-severity-high/20 rounded-btn text-severity-high group-hover:scale-110 transition-transform duration-200">
            <Flame className="w-6 h-6" />
          </div>
        </div>

        {/* Most Common Situation */}
        <div className="bg-bg-surface border border-border rounded-card p-5 flex items-center justify-between stat-card-hover group">
          <div className="space-y-1 min-w-0">
            <span className="text-xs text-text-secondary font-semibold uppercase tracking-wider block truncate">Top Situation</span>
            <div className="text-lg font-black text-text-primary truncate">
              {mostCommonSituation}
            </div>
          </div>
          <div className="p-3 bg-accent-purple/10 border border-accent-purple/20 rounded-btn text-accent-purple group-hover:scale-110 transition-transform duration-200 shrink-0">
            <PieChart className="w-6 h-6" />
          </div>
        </div>

      </div>

      {/* ROW 2: AreaChart & PieChart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <AlertsChart data={alertsOverTimeData} />
        </div>
        <div>
          <RiskTrendChart data={riskDistributionData} />
        </div>
      </div>

      {/* ROW 3: Horizontal Bar Chart & Line Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Top Situations Horizontal Bar */}
        <div className="bg-bg-surface border border-border rounded-card p-5 h-[340px] flex flex-col shadow-lg">
          <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-4">
            Incident Frequency by Situation Type
          </h3>
          <div className="flex-1 w-full text-xs">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={topSituationsData}
                margin={{ top: 5, right: 10, left: 30, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1E3058" opacity={0.3} horizontal={false} />
                <XAxis type="number" stroke="#8A9BC4" fontSize={9} tickLine={false} />
                <YAxis dataKey="name" type="category" stroke="#8A9BC4" fontSize={9} tickLine={false} width={100} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0F1629",
                    borderColor: "#1E3058",
                    borderRadius: "10px",
                    color: "#E8EEFF"
                  }}
                />
                <Bar dataKey="count" fill="var(--accent-blue)" radius={[0, 4, 4, 0]}>
                  {topSituationsData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={index % 2 === 0 ? "var(--accent-blue)" : "var(--accent-purple)"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gemini Confidence Line Trend */}
        <div className="bg-bg-surface border border-border rounded-card p-5 h-[340px] flex flex-col shadow-lg">
          <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-4">
            Gemini Verification Confidence Trend (Last 50 Logs)
          </h3>
          <div className="flex-1 w-full text-xs">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={confidenceTrendData}
                margin={{ top: 10, right: 20, left: -20, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1E3058" opacity={0.3} />
                <XAxis dataKey="index" stroke="#8A9BC4" fontSize={9} tickLine={false} />
                <YAxis stroke="#8A9BC4" fontSize={9} tickLine={false} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0F1629",
                    borderColor: "#1E3058",
                    borderRadius: "10px",
                    color: "#E8EEFF"
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="confidence" 
                  stroke="var(--accent-cyan)" 
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* ROW 4: Heatmap grid */}
      <HeatmapGrid data={events} />

    </div>
  );
}
