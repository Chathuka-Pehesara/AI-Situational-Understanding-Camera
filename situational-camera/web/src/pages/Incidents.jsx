import React, { useState, useEffect, useCallback } from "react";
import { Search, Filter, Calendar, ChevronLeft, ChevronRight, ShieldAlert, Eye, Image as ImageIcon } from "lucide-react";
import { api } from "../lib/api";
import { getSeverity } from "../lib/constants";
import SnapshotModal from "../components/incidents/SnapshotModal";

export default function Incidents() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const limit = 15; // Show 15 incidents per page
  
  // Filter states
  const [searchQuery, setSearchQuery] = useState("");
  const [severity, setSeverity] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  
  // Selected incident for modal details
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchIncidents = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.searchEvents({
        q: searchQuery,
        severity: severity || null,
        dateFrom: dateFrom || null,
        dateTo: dateTo || null,
        page,
        limit
      });
      setEvents(data.events || []);
      setTotalCount(data.total_count || 0);
    } catch (err) {
      console.error("Error loading incidents:", err);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, severity, dateFrom, dateTo, page]);

  useEffect(() => {
    fetchIncidents();
  }, [fetchIncidents]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchIncidents();
  };

  const handleResetFilters = () => {
    setSearchQuery("");
    setSeverity("");
    setDateFrom("");
    setDateTo("");
    setPage(1);
  };

  const handleOpenDetails = (incident) => {
    setSelectedIncident(incident);
    setIsModalOpen(true);
  };

  // Group events by date for rendering separators
  const groupEventsByDate = (items) => {
    const groups = {};
    items.forEach((event) => {
      const dateStr = event.timestamp.split(" ")[0]; // YYYY-MM-DD
      if (!groups[dateStr]) {
        groups[dateStr] = [];
      }
      groups[dateStr].push(event);
    });
    return groups;
  };

  const groupedIncidents = groupEventsByDate(events);
  const totalPages = Math.max(1, Math.ceil(totalCount / limit));

  return (
    <div className="space-y-6 flex flex-col h-full min-w-0 animate-page-enter select-none">
      
      {/* FILTER BAR HEADER */}
      <form onSubmit={handleSearchSubmit} className="bg-bg-surface border border-border rounded-card p-5 space-y-4 shadow-md">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          
          {/* Keyword Search Input */}
          <div className="relative">
            <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-text-muted">
              <Search className="w-4 h-4" />
            </span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-bg-base border border-border focus:border-accent-blue rounded-input py-2 pl-9 pr-4 text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-accent-blue transition-colors font-medium placeholder-text-muted"
              placeholder="Search situation description..."
            />
          </div>

          {/* Severity Dropdown */}
          <div className="relative">
            <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-text-muted">
              <Filter className="w-4 h-4" />
            </span>
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
              className="w-full bg-bg-base border border-border focus:border-accent-blue rounded-input py-2 pl-9 pr-4 text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-accent-blue cursor-pointer transition-colors font-medium"
            >
              <option value="">All Threat Levels</option>
              <option value="High">High Risk</option>
              <option value="Medium">Medium Risk</option>
              <option value="Low">Low Risk</option>
            </select>
          </div>

          {/* Date From Picker */}
          <div className="relative">
            <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-text-muted">
              <Calendar className="w-4 h-4" />
            </span>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="w-full bg-bg-base border border-border focus:border-accent-blue rounded-input py-2 pl-9 pr-4 text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-accent-blue cursor-pointer transition-colors font-medium text-text-secondary"
            />
          </div>

          {/* Date To Picker */}
          <div className="relative">
            <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-text-muted">
              <Calendar className="w-4 h-4" />
            </span>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="w-full bg-bg-base border border-border focus:border-accent-blue rounded-input py-2 pl-9 pr-4 text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-accent-blue cursor-pointer transition-colors font-medium text-text-secondary"
            />
          </div>

        </div>

        {/* Action Controls */}
        <div className="flex justify-end gap-3 select-none">
          <button
            type="button"
            onClick={handleResetFilters}
            className="px-4 py-2 border border-border text-xs text-text-secondary hover:text-text-primary rounded-btn hover:bg-bg-elevated/40 hover:border-border-bright transition-all duration-200 cursor-pointer"
          >
            Reset Filters
          </button>
          <button
            type="submit"
            className="px-5 py-2 bg-accent-blue text-text-primary text-xs font-bold rounded-btn cursor-pointer shadow-md hover:shadow-[0_0_15px_rgba(59,130,246,0.3)] hover:scale-[1.01] transition-all duration-200"
          >
            Apply Filters
          </button>
        </div>
      </form>

      {/* TIMELINE LIST */}
      <div className="flex-1 min-w-0">
        {loading ? (
          <div className="h-[400px] flex items-center justify-center text-text-muted">
            <span className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-blue"></span>
          </div>
        ) : events.length > 0 ? (
          <div className="space-y-8 relative pl-6 before:absolute before:left-2 before:top-4 before:bottom-4 before:w-0.5 before:bg-border select-none">
            
            {Object.entries(groupedIncidents).map(([dateStr, items]) => (
              <div key={dateStr} className="space-y-4">
                
                {/* Date Header Badge */}
                <div className="relative -left-4 flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-border-bright border border-bg-base z-10"></div>
                  <span className="text-[10px] uppercase font-bold tracking-widest text-accent-cyan bg-bg-elevated border border-border px-2.5 py-1 rounded-full shadow-sm">
                    {dateStr}
                  </span>
                </div>

                {/* Date's Incident Cards */}
                <div className="space-y-3.5">
                  {items.map((event, idx) => {
                    const sev = getSeverity(event.situation, event.risk);
                    return (
                      <div 
                        key={idx} 
                        className="bg-bg-surface border border-border hover:border-border-bright rounded-card p-5 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 transition-all duration-200 hover:shadow-md ml-3 relative"
                      >
                        {/* Timeline point indicator */}
                        <span 
                          style={{ backgroundColor: sev.color }} 
                          className="absolute -left-[27px] top-[26px] h-3.5 w-3.5 rounded-full border-[3px] border-bg-base z-10 shadow-sm"
                        />

                        {/* Text and context details */}
                        <div className="flex gap-4 items-start flex-1 min-w-0">
                          {/* Mini visual camera icon */}
                          <div className="p-3 bg-bg-base border border-border rounded-btn text-text-secondary shrink-0 hidden sm:block">
                            <ShieldAlert className="w-5 h-5 text-text-muted" />
                          </div>

                          <div className="space-y-1.5 min-w-0">
                            <div className="flex flex-wrap items-center gap-3">
                              <span className="text-sm font-extrabold text-text-primary leading-none">
                                {event.situation}
                              </span>
                              <span
                                style={{
                                  backgroundColor: sev.bgColor,
                                  color: sev.textColor,
                                  borderColor: sev.borderColor,
                                }}
                                className="text-[8px] font-black px-2 py-0.5 rounded-badge border uppercase tracking-wider leading-none"
                              >
                                {sev.label}
                              </span>
                            </div>
                            
                            <p className="text-xs text-text-secondary line-clamp-1 leading-relaxed">
                              {event.explanation}
                            </p>

                            <div className="text-[10px] text-text-muted font-mono flex flex-wrap items-center gap-x-3 gap-y-1">
                              <span>TIME: {event.timestamp.split(" ")[1]}</span>
                              <span>•</span>
                              <span>SAFETY: {event.safety_score}/10</span>
                              <span>•</span>
                              <span>ASSUR: {event.gemini_confidence ? Math.round(event.gemini_confidence * 100) : 50}%</span>
                            </div>
                          </div>
                        </div>

                        {/* View Snapshot trigger button */}
                        <button
                          onClick={() => handleOpenDetails(event)}
                          className="shrink-0 flex items-center gap-1.5 px-3.5 py-2 bg-bg-elevated hover:bg-bg-overlay text-text-secondary hover:text-text-primary border border-border hover:border-border-bright rounded-btn text-xs font-bold transition-all duration-200 cursor-pointer shadow-sm w-full md:w-auto justify-center"
                        >
                          <Eye className="w-4 h-4" />
                          <span>View Details</span>
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Empty timeline results state */
          <div className="h-[300px] bg-bg-surface border border-border rounded-card flex flex-col items-center justify-center text-center p-6 select-none animate-page-enter">
            <ShieldAlert className="w-12 h-12 text-text-muted mb-3" />
            <h3 className="text-sm font-bold text-text-primary mb-1">No Incidents Found</h3>
            <p className="text-xs text-text-muted">Adjust search keywords or expand filters to view logs.</p>
          </div>
        )}
      </div>

      {/* PAGINATION CONTROLS */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between select-none pt-4 border-t border-border/40">
          <span className="text-xs text-text-secondary font-medium">
            Showing page <span className="text-text-primary font-bold">{page}</span> of{" "}
            <span className="text-text-primary font-bold">{totalPages}</span> ({totalCount} total events)
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-2 border border-border hover:border-border-bright rounded-btn bg-bg-surface hover:bg-bg-elevated disabled:opacity-40 disabled:hover:bg-bg-surface disabled:hover:border-border text-text-secondary hover:text-text-primary transition-all duration-200 cursor-pointer disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="p-2 border border-border hover:border-border-bright rounded-btn bg-bg-surface hover:bg-bg-elevated disabled:opacity-40 disabled:hover:bg-bg-surface disabled:hover:border-border text-text-secondary hover:text-text-primary transition-all duration-200 cursor-pointer disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Detail snap reports Modal Overlay */}
      <SnapshotModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        incident={selectedIncident}
      />

    </div>
  );
}
