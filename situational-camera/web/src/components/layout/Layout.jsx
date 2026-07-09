import React from "react";
import Sidebar from "./Sidebar";
import TopBar from "./TopBar";

export default function Layout({ 
  children, 
  currentPage, 
  setCurrentPage, 
  onLogout, 
  activeCameraCount = 0, 
  unreadAlertCount = 0 
}) {
  
  // Format page titles nicely
  const getPageTitle = (page) => {
    if (page === "ask-footage") return "Ask Gemini AI";
    return page;
  };

  return (
    <div className="flex w-screen h-screen bg-bg-base overflow-hidden">
      {/* Sidebar Navigation */}
      <Sidebar 
        currentPage={currentPage} 
        setCurrentPage={setCurrentPage} 
        onLogout={onLogout} 
      />

      {/* Main Container */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <TopBar 
          title={getPageTitle(currentPage)} 
          activeCameraCount={activeCameraCount}
          unreadAlertCount={unreadAlertCount}
        />

        {/* Dynamic Page View Area */}
        <main className="flex-1 overflow-y-auto bg-bg-base relative p-6 min-w-0">
          {children}
        </main>
      </div>
    </div>
  );
}
