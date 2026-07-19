import React, { useState, useRef, useEffect } from "react";
import { 
  Send, 
  Brain, 
  HelpCircle, 
  Calendar, 
  Camera, 
  ShieldAlert, 
  MessageSquare,
  Sparkles
} from "lucide-react";
import { api } from "../lib/api";
import { useCamera } from "../hooks/useCamera";
import { getSeverity } from "../lib/constants";

export default function AskFootage() {
  const { cameras } = useCamera();
  const chatEndRef = useRef(null);
  const [messages, setMessages] = useState([
    {
      sender: "gemini",
      text: "Hello! I am your AI Proctor assistant. Ask me questions about today's exam incidents, focus scores, cheating attempts, or attention warnings. I will analyze the exam logs and provide details.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      relevantEvents: []
    }
  ]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(0);

  // Filters
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [selectedCameraId, setSelectedCameraId] = useState("");

  const suggestedQuestions = [
    "Was anyone near the restricted zone A?",
    "What was the highest risk event logged?",
    "Were there any loitering incidents?",
    "Is there any normal activity recorded?"
  ];

  // Fetch count of events in range for informational badge
  useEffect(() => {
    const fetchCount = async () => {
      try {
        const res = await api.searchEvents({
          dateFrom: dateFrom || null,
          dateTo: dateTo || null,
          limit: 1000
        });
        setTotalCount(res.total_count || 0);
      } catch (err) {
        console.error("Error loading search events count:", err);
      }
    };
    fetchCount();
  }, [dateFrom, dateTo]);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (textToSend) => {
    const query = textToSend || question;
    if (!query.trim()) return;

    // Add user message
    const userMsg = {
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      relevantEvents: []
    };
    setMessages((prev) => [...prev, userMsg]);
    setQuestion("");
    setLoading(true);

    try {
      const res = await api.askFootage({
        question: query,
        dateFrom: dateFrom || null,
        dateTo: dateTo || null,
        cameraId: selectedCameraId || null
      });

      // Add Gemini response
      const geminiMsg = {
        sender: "gemini",
        text: res.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        relevantEvents: res.relevant_events || []
      };
      setMessages((prev) => [...prev, geminiMsg]);

    } catch (err) {
      console.error("Error asking Gemini Q&A:", err);
      setMessages((prev) => [
        ...prev,
        {
          sender: "gemini",
          text: "I encountered an error querying the video logs. Please ensure the API server is active and the Google API key is configured.",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          relevantEvents: []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6 h-[calc(100vh-100px)] min-w-0 animate-page-enter select-none">
      
      {/* LEFT (30%): CONTEXT CONTROLS */}
      <div className="w-full lg:w-[30%] bg-bg-surface border border-border rounded-card p-5 flex flex-col justify-between shadow-lg shrink-0">
        <div className="space-y-6">
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-text-primary uppercase tracking-wider">Footage Context</h3>
            <p className="text-xs text-text-secondary">Constrain the search filters to optimize Q&A accuracy</p>
          </div>

          {/* Date filters */}
          <div className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-text-secondary tracking-wide flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-text-muted" />
                <span>Date Range</span>
              </label>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="bg-bg-base border border-border focus:border-accent-blue rounded-input py-1.5 px-2 text-[10px] text-text-secondary focus:outline-none focus:ring-1 focus:ring-accent-blue cursor-pointer"
                />
                <input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="bg-bg-base border border-border focus:border-accent-blue rounded-input py-1.5 px-2 text-[10px] text-text-secondary focus:outline-none focus:ring-1 focus:ring-accent-blue cursor-pointer"
                />
              </div>
            </div>

            {/* Camera Select */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-text-secondary tracking-wide flex items-center gap-1.5">
                <Camera className="w-3.5 h-3.5 text-text-muted" />
                <span>Target Camera Feed</span>
              </label>
              <select
                value={selectedCameraId}
                onChange={(e) => setSelectedCameraId(e.target.value)}
                className="w-full bg-bg-base border border-border focus:border-accent-blue rounded-input py-1.5 px-3 text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-accent-blue cursor-pointer"
              >
                <option value="">All Cameras</option>
                {cameras.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Stats Badge */}
          <div className="bg-bg-base/40 border border-border/40 rounded-btn p-3.5 flex items-center justify-between text-xs">
            <span className="text-text-secondary font-medium">Events in scope:</span>
            <span className="font-mono font-bold text-accent-cyan bg-bg-elevated px-2 py-0.5 border border-border rounded-full">
              {totalCount}
            </span>
          </div>
        </div>

        {/* Suggested Questions */}
        <div className="space-y-3 pt-6 border-t border-border/40">
          <span className="text-xs font-semibold text-text-secondary tracking-wide flex items-center gap-1.5">
            <HelpCircle className="w-3.5 h-3.5 text-text-muted" />
            <span>Suggested Queries</span>
          </span>
          <div className="flex flex-col gap-2">
            {suggestedQuestions.map((q, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSend(q)}
                disabled={loading}
                className="w-full text-left bg-bg-base hover:bg-bg-elevated hover:border-border-bright border border-border text-xs text-text-secondary hover:text-text-primary p-2.5 rounded-btn transition-all duration-200 cursor-pointer truncate"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

      </div>

      {/* RIGHT (70%): CHAT VIEW */}
      <div className="flex-1 bg-bg-surface border border-border rounded-card flex flex-col h-full overflow-hidden shadow-lg min-w-0">
        
        {/* Chat Header */}
        <div className="px-5 py-4 border-b border-border bg-bg-surface/50 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-accent-purple" />
            <h2 className="text-sm font-bold text-text-primary uppercase tracking-wider">Gemini Copilot Q&A</h2>
          </div>
          <span className="bg-accent-purple/10 border border-accent-purple/30 text-accent-purple text-[9px] font-black px-2 py-0.5 rounded-full flex items-center gap-1 select-none">
            <Brain className="w-3 h-3 animate-pulse" />
            <span>GEMINI FLASH</span>
          </span>
        </div>

        {/* Chat History Messages scroll container */}
        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          {messages.map((msg, idx) => {
            const isUser = msg.sender === "user";
            return (
              <div 
                key={idx} 
                className={`flex gap-3 max-w-[85%] ${isUser ? "ml-auto flex-row-reverse" : "mr-auto"}`}
              >
                {/* Avatar Icon */}
                <div className={`w-8 h-8 rounded-full border flex items-center justify-center shrink-0 shadow-sm ${
                  isUser 
                    ? "bg-accent-blue/10 border-accent-blue/40 text-accent-blue" 
                    : "bg-accent-purple/10 border-accent-purple/40 text-accent-purple"
                }`}>
                  {isUser ? "OP" : <Brain className="w-4 h-4" />}
                </div>

                {/* Message Bubble */}
                <div className="space-y-3">
                  <div className={`rounded-card p-4 text-sm leading-relaxed border select-text ${
                    isUser 
                      ? "bg-bg-elevated border-border-bright text-text-primary rounded-tr-none" 
                      : "bg-bg-base border-border text-text-secondary rounded-tl-none"
                  }`}>
                    {msg.text}
                    <div className={`text-[9px] mt-2 font-mono text-text-muted select-none ${isUser ? "text-right" : "text-left"}`}>
                      {msg.timestamp}
                    </div>
                  </div>

                  {/* Inline Reference incident cards */}
                  {!isUser && msg.relevantEvents.length > 0 && (
                    <div className="space-y-2 mt-2">
                      <div className="text-[10px] uppercase font-bold tracking-widest text-text-muted flex items-center gap-1 leading-none select-none">
                        <ShieldAlert className="w-3.5 h-3.5" />
                        <span>Referencing Exam Logs</span>
                      </div>
                      
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {msg.relevantEvents.map((evt, eIdx) => {
                          const s = getSeverity(evt.situation, evt.risk);
                          return (
                            <div key={eIdx} className="bg-bg-base border border-border/80 hover:border-border-bright rounded-btn p-3 space-y-1.5 shadow-sm transition-all duration-200">
                              <div className="flex items-center justify-between">
                                <span className="text-[10px] text-text-primary font-bold truncate pr-2">{evt.situation}</span>
                                <span 
                                  style={{ backgroundColor: s.bgColor, color: s.textColor, borderColor: s.borderColor }}
                                  className="text-[7px] font-black px-1.5 py-0.2 rounded-badge border uppercase tracking-wider"
                                >
                                  {s.label}
                                </span>
                              </div>
                              <p className="text-[11px] text-text-secondary line-clamp-1 leading-normal">{evt.explanation}</p>
                              <span className="text-[9px] text-text-muted font-mono block">{evt.timestamp}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {/* Typing Indicator loading state */}
          {loading && (
            <div className="flex gap-3 max-w-[80%] mr-auto items-center animate-page-enter">
              <div className="w-8 h-8 rounded-full border bg-accent-purple/10 border-accent-purple/40 text-accent-purple flex items-center justify-center shrink-0">
                <Brain className="w-4 h-4" />
              </div>
              <div className="bg-bg-base border border-border rounded-card rounded-tl-none p-4 flex gap-1 items-center shadow-sm">
                <span className="h-2 w-2 bg-accent-purple rounded-full animate-bounce-dot"></span>
                <span className="h-2 w-2 bg-accent-purple rounded-full animate-bounce-dot animation-delay-160"></span>
                <span className="h-2 w-2 bg-accent-purple rounded-full animate-bounce-dot animation-delay-320"></span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Bar sticky bottom */}
        <form 
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="p-4 border-t border-border bg-bg-surface/50 flex gap-3 shrink-0 items-center select-none"
        >
          <div className="relative flex-1">
            <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-text-muted pointer-events-none">
              <MessageSquare className="w-4 h-4" />
            </span>
            <input
              type="text"
              required
              disabled={loading}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="w-full bg-bg-base border border-border focus:border-accent-blue rounded-input py-3 pl-10 pr-4 text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-accent-blue transition-colors font-medium placeholder-text-muted"
              placeholder="Ask a question about your exam logs (e.g. 'was cheating detected?')..."
            />
          </div>

          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="p-3 bg-accent-blue hover:bg-accent-blue/80 disabled:opacity-40 disabled:hover:bg-accent-blue text-text-primary rounded-btn transition-all duration-200 cursor-pointer disabled:cursor-not-allowed shadow-md hover:shadow-[0_0_15px_rgba(59,130,246,0.35)] shrink-0"
          >
            <Send className="w-4.5 h-4.5" />
          </button>
        </form>

      </div>

    </div>
  );
}
