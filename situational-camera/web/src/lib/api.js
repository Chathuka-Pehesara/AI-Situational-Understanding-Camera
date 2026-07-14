import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const api = {
  // Alerts API
  getAlerts: async (severity = null, limit = 50) => {
    const params = {};
    if (severity) params.severity = severity;
    if (limit) params.limit = limit;
    const res = await apiClient.get("/api/alerts", { params });
    return res.data;
  },
  
  clearAlerts: async () => {
    const res = await apiClient.post("/api/alerts/clear");
    return res.data;
  },

  // Events/Incidents API
  getEvents: async (page = 1, limit = 25) => {
    const res = await apiClient.get("/api/events", {
      params: { page, limit },
    });
    return res.data;
  },

  searchEvents: async ({ q, severity, dateFrom, dateTo, page = 1, limit = 25 }) => {
    const params = { page, limit };
    if (q) params.q = q;
    if (severity) params.severity = severity;
    if (dateFrom) params.date_from = dateFrom;
    if (dateTo) params.date_to = dateTo;
    
    const res = await apiClient.get("/api/events/search", { params });
    return res.data;
  },

  // Cameras API
  getCameras: async () => {
    const res = await apiClient.get("/api/cameras");
    return res.data;
  },

  addCamera: async (name, source) => {
    const res = await apiClient.post("/api/cameras", { name, source });
    return res.data;
  },

  deleteCamera: async (cameraId) => {
    const res = await apiClient.delete(`/api/cameras/${cameraId}`);
    return res.data;
  },

  uploadVideo: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await apiClient.post("/api/cameras/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return res.data;
  },

  // Gemini Chat Q&A API
  askFootage: async ({ question, dateFrom, dateTo, cameraId }) => {
    const body = {
      question,
      date_from: dateFrom || null,
      date_to: dateTo || null,
      camera_id: cameraId || null,
    };
    const res = await apiClient.post("/api/chat", body);
    return res.data;
  },
  
  // WS Endpoint constructor helper
  getWSStreamUrl: (cameraId) => {
    const apiBase = import.meta.env.VITE_API_URL || "http://localhost:8000";
    // Auto-derive ws:// or wss:// from the API URL if VITE_WS_URL is missing
    const defaultWsUrl = apiBase.replace(/^http/, "ws");
    const wsBaseUrl = import.meta.env.VITE_WS_URL || defaultWsUrl;
    return `${wsBaseUrl}/ws/stream/${cameraId}`;
  }
};
