import { useEffect, useRef, useState, useCallback } from "react";
import { api } from "../lib/api";

export const useWebSocket = (cameraId, onMessage) => {
  const [status, setStatus] = useState("disconnected");
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const onMessageRef = useRef(onMessage);

  // Keep callback reference updated to avoid triggering effects
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setStatus("disconnected");
  }, []);

  const connect = useCallback(() => {
    if (!cameraId) return;
    
    disconnect();
    setStatus("connecting");

    const url = api.getWSStreamUrl(cameraId);
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus("connected");
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (onMessageRef.current) {
          onMessageRef.current(data);
        }
      } catch (err) {
        console.error("WebSocket message parsing error:", err);
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
      setStatus("error");
    };

    ws.onclose = () => {
      setStatus("disconnected");
      // Try to reconnect in 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        console.log("Attempting to reconnect WebSocket...");
        connect();
      }, 3000);
    };
  }, [cameraId, disconnect]);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [cameraId, connect, disconnect]);

  return { status, connect, disconnect };
};
