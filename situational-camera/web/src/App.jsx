import React, { useState, useEffect } from "react";
import Layout from "./components/layout/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Incidents from "./pages/Incidents";
import Analytics from "./pages/Analytics";
import Cameras from "./pages/Cameras";
import AskFootage from "./pages/AskFootage";
import { useCamera } from "./hooks/useCamera";
import { useAlerts } from "./hooks/useAlerts";

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userEmail, setUserEmail] = useState("");
  const [currentPage, setCurrentPage] = useState("dashboard");

  // Keep camera and alerts stats loaded globally to feed TopBar badges
  const { cameras } = useCamera();
  const { alerts } = useAlerts(5000); // Poll alerts every 5 seconds globally

  // Local storage session check
  useEffect(() => {
    const savedUser = localStorage.getItem("soc_session_user");
    if (savedUser) {
      setUserEmail(savedUser);
      setIsLoggedIn(true);
    }
  }, []);

  const handleLogin = (email) => {
    localStorage.setItem("soc_session_user", email);
    setUserEmail(email);
    setIsLoggedIn(true);
    setCurrentPage("dashboard");
  };

  const handleLogout = () => {
    localStorage.removeItem("soc_session_user");
    setUserEmail("");
    setIsLoggedIn(false);
  };

  if (!isLoggedIn) {
    return <Login onLogin={handleLogin} />;
  }

  // Count active cameras and unread alerts
  const activeCameraCount = cameras.filter((c) => c.status === "Live").length;
  const unreadAlertCount = alerts.filter((a) => a.status === "active").length;

  const renderPage = () => {
    switch (currentPage) {
      case "dashboard":
        return <Dashboard />;
      case "incidents":
        return <Incidents />;
      case "analytics":
        return <Analytics />;
      case "cameras":
        return <Cameras />;
      case "ask-footage":
        return <AskFootage />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <Layout
      currentPage={currentPage}
      setCurrentPage={setCurrentPage}
      onLogout={handleLogout}
      activeCameraCount={activeCameraCount}
      unreadAlertCount={unreadAlertCount}
    >
      {renderPage()}
    </Layout>
  );
}
