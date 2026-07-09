import { useState, useEffect, useCallback } from "react";
import { api } from "../lib/api";

export const useAlerts = (pollInterval = 3000) => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAlerts = useCallback(async () => {
    try {
      const data = await api.getAlerts();
      setAlerts(data);
      setError(null);
    } catch (err) {
      console.error("Error fetching alerts:", err);
      setError("Failed to load alerts");
    }
  }, []);

  const addLocalAlert = useCallback((alert) => {
    setAlerts((prev) => {
      // Avoid duplicate alert cards with same situation & camera in last 10s (similar to backend)
      const now = new Date();
      const existingIdx = prev.findIndex(
        (a) => a.camera_id === alert.camera_id && a.situation === alert.situation
      );

      if (existingIdx !== -1) {
        const existing = prev[existingIdx];
        const existingTime = new Date(existing.timestamp);
        if (now - existingTime < 10000) {
          const updated = [...prev];
          updated[existingIdx] = { ...existing, ...alert };
          return updated;
        }
      }

      // Add to front of list (slide-in)
      return [alert, ...prev];
    });
  }, []);

  const clearAlerts = useCallback(async () => {
    setLoading(true);
    try {
      await api.clearAlerts();
      setAlerts([]);
      setError(null);
    } catch (err) {
      console.error("Error clearing alerts:", err);
      setError("Failed to clear alerts");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAlerts();
    if (pollInterval) {
      const interval = setInterval(fetchAlerts, pollInterval);
      return () => clearInterval(interval);
    }
  }, [fetchAlerts, pollInterval]);

  return { alerts, loading, error, fetchAlerts, addLocalAlert, clearAlerts };
};
