import { useState, useEffect, useCallback } from "react";
import { api } from "../lib/api";

export const useCamera = () => {
  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCameras = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getCameras();
      setCameras(data);
      setError(null);
    } catch (err) {
      console.error("Error loading cameras:", err);
      setError("Failed to load cameras");
    } finally {
      setLoading(false);
    }
  }, []);

  const addCamera = useCallback(async (name, source) => {
    setLoading(true);
    try {
      const newCam = await api.addCamera(name, source);
      setCameras((prev) => [...prev, newCam]);
      setError(null);
      return newCam;
    } catch (err) {
      console.error("Error adding camera:", err);
      setError("Failed to register new camera feed");
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteCamera = useCallback(async (cameraId) => {
    setLoading(true);
    try {
      await api.deleteCamera(cameraId);
      setCameras((prev) => prev.filter((c) => c.id !== cameraId));
      setError(null);
    } catch (err) {
      console.error("Error removing camera:", err);
      setError("Failed to delete camera feed");
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCameras();
  }, [fetchCameras]);

  return { cameras, loading, error, fetchCameras, addCamera, deleteCamera };
};
