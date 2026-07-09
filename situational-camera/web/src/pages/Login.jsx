import React, { useState } from "react";
import { Cctv, ShieldCheck, Cpu, BellRing, Lock, Mail, Loader2 } from "lucide-react";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("operator@situvision.ai");
  const [password, setPassword] = useState("password");
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Please fill in all fields.");
      return;
    }
    setError("");
    setIsScanning(true);

    // Simulate connection / scan animation for 1.5 seconds
    setTimeout(() => {
      setIsScanning(false);
      onLogin(email);
    }, 1500);
  };

  return (
    <div className="w-screen h-screen bg-bg-base flex overflow-hidden relative font-sans">
      
      {/* LEFT HALF (60%): Aesthetic branding and visual details */}
      <div className="hidden lg:flex w-[60%] h-full relative flex-col justify-between p-12 bg-dot-grid border-r border-border select-none">
        
        {/* Abstract animated background elements */}
        <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
          <div className="absolute top-[20%] left-[10%] w-72 h-72 rounded-full bg-accent-blue/10 blur-[100px] animate-pulse" style={{ animationDuration: '8s' }}></div>
          <div className="absolute bottom-[20%] right-[10%] w-96 h-96 rounded-full bg-accent-purple/10 blur-[120px] animate-pulse" style={{ animationDuration: '10s' }}></div>
          
          {/* Animated floating particles */}
          <div className="absolute top-1/4 left-1/3 w-2 h-2 bg-accent-cyan rounded-full opacity-60 animate-ping" style={{ animationDuration: '4s' }}></div>
          <div className="absolute bottom-1/3 left-1/4 w-3 h-3 bg-accent-purple rounded-full opacity-40 animate-bounce" style={{ animationDuration: '6s' }}></div>
          <div className="absolute top-1/3 right-1/4 w-1.5 h-1.5 bg-accent-blue rounded-full opacity-50 animate-pulse" style={{ animationDuration: '3s' }}></div>
        </div>

        {/* Top bar header */}
        <div className="flex items-center gap-3 z-10">
          <div className="w-10 h-10 rounded-btn bg-accent-blue/20 border border-accent-blue/40 flex items-center justify-center shadow-[0_0_15px_rgba(59,130,246,0.25)]">
            <Cctv className="w-5 h-5 text-accent-blue" />
          </div>
          <span className="font-extrabold text-xl bg-gradient-to-r from-accent-blue via-accent-purple to-accent-cyan bg-clip-text text-transparent tracking-wide">
            SituVision AI
          </span>
        </div>

        {/* Hero title & features */}
        <div className="my-auto z-10 max-w-xl">
          <h1 className="text-5xl font-black text-text-primary leading-[1.15] mb-6">
            Intelligent Security{" "}
            <span className="bg-gradient-to-r from-accent-blue via-accent-purple to-accent-cyan bg-clip-text text-transparent">
              Supervision
            </span>{" "}
            Powered by Gemini
          </h1>
          <p className="text-base text-text-secondary mb-8 leading-relaxed">
            A next-generation Surveillance Operations Center integrating computer vision models with real-time generative reasoning. Detect threats, analyze zones, and ask footage queries instantly.
          </p>

          {/* Feature Pills */}
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center gap-2 bg-bg-surface border border-border px-4 py-2.5 rounded-full text-xs font-semibold text-text-primary shadow-lg hover:border-border-bright transition-colors duration-300">
              <span className="h-2.5 w-2.5 rounded-full bg-severity-critical animate-[pulse-live_1.5s_infinite]"></span>
              Live Detection
            </div>
            <div className="flex items-center gap-2 bg-bg-surface border border-border px-4 py-2.5 rounded-full text-xs font-semibold text-text-primary shadow-lg hover:border-border-bright transition-colors duration-300">
              <span className="h-2.5 w-2.5 rounded-full bg-accent-purple"></span>
              Gemini Vision
            </div>
            <div className="flex items-center gap-2 bg-bg-surface border border-border px-4 py-2.5 rounded-full text-xs font-semibold text-text-primary shadow-lg hover:border-border-bright transition-colors duration-300">
              <span className="h-2.5 w-2.5 rounded-full bg-accent-cyan"></span>
              Smart Alerts
            </div>
          </div>
        </div>

        {/* Footer legalities */}
        <div className="text-xs text-text-muted z-10 select-none">
          © {new Date().getFullYear()} SituVision AI Security Corp. All rights reserved.
        </div>
      </div>

      {/* RIGHT HALF (40%): Login Form */}
      <div className="w-full lg:w-[40%] h-full flex flex-col justify-center items-center p-8 bg-bg-base z-10">
        
        {/* Frosted Glass Login Card */}
        <div className="w-full max-w-md relative overflow-hidden backdrop-blur-xl bg-white/5 border border-white/10 rounded-card p-10 shadow-[0_20px_50px_rgba(10,14,26,0.8)]">
          
          {/* Scanning Sweep Line (triggers on form submission) */}
          {isScanning && (
            <div className="absolute left-0 w-full h-1 bg-gradient-to-r from-transparent via-accent-cyan to-transparent animate-scan z-20 pointer-events-none" />
          )}

          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-text-primary mb-2">Welcome Back</h2>
            <p className="text-xs text-text-secondary">Authorized SOC personnel authentication required</p>
          </div>

          {error && (
            <div className="mb-4 bg-severity-critical/15 border border-severity-critical/30 rounded-btn p-3 text-xs text-text-primary font-medium text-center">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* Email Field */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-text-secondary tracking-wide block">Email Address</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-text-muted pointer-events-none">
                  <Mail className="w-4 h-4" />
                </span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-bg-surface hover:bg-bg-elevated/50 focus:bg-bg-surface border border-border focus:border-accent-blue rounded-input py-2.5 pl-10 pr-4 text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-accent-blue transition-all duration-300 font-medium placeholder-text-muted"
                  placeholder="name@agency.gov"
                  disabled={isScanning}
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-text-secondary tracking-wide block">Security Key</label>
              </div>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-text-muted pointer-events-none">
                  <Lock className="w-4 h-4" />
                </span>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-bg-surface hover:bg-bg-elevated/50 focus:bg-bg-surface border border-border focus:border-accent-blue rounded-input py-2.5 pl-10 pr-4 text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-accent-blue transition-all duration-300 font-medium placeholder-text-muted"
                  placeholder="••••••••••••"
                  disabled={isScanning}
                />
              </div>
            </div>

            {/* Auth Button with glowing hover */}
            <button
              type="submit"
              disabled={isScanning}
              className="w-full bg-gradient-to-r from-accent-blue to-accent-purple hover:scale-[1.02] focus:scale-98 text-text-primary font-bold py-3 px-4 rounded-btn text-sm cursor-pointer shadow-[0_4px_15px_rgba(59,130,246,0.2)] hover:shadow-[0_0_25px_rgba(59,130,246,0.45)] transition-all duration-300 flex items-center justify-center gap-2"
            >
              {isScanning ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Scanning Credentials...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                </>
              )}
            </button>

          </form>

        </div>
      </div>
      
    </div>
  );
}
