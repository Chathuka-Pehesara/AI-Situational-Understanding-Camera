import React, { useState } from "react";
import { GraduationCap, ShieldCheck, Cpu, BellRing, Lock, Mail, Loader2, Zap, Video, ArrowRight } from "lucide-react";

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

    setTimeout(() => {
      setIsScanning(false);
      onLogin(email);
    }, 1500);
  };

  return (
    <div 
      className="w-screen h-screen flex overflow-hidden relative font-sans opacity-0"
      style={{ animation: 'page-enter 1.2s cubic-bezier(0.2, 0.8, 0.2, 1) forwards' }}
    >
      
      {/* LEFT HALF (50%): Dark theme branding */}
      <div className="hidden lg:flex w-1/2 h-full flex-col justify-between p-16 bg-[#0A0F1C] bg-dot-grid border-r border-slate-800/50 select-none relative">
        
        {/* Top bar header */}
        <div className="flex items-center gap-3 z-10">
          <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
            <GraduationCap className="w-5 h-5 text-blue-400" />
          </div>
          <span className="font-extrabold text-xl text-white tracking-wide">
            SituVision <span className="text-blue-400">AI</span>
          </span>
        </div>

        {/* Hero title & features */}
        <div className="my-auto z-10 max-w-lg">
          
          <div className="inline-flex items-center gap-2 bg-slate-800/50 border border-slate-700/50 rounded-full px-3 py-1.5 mb-8 backdrop-blur-sm">
            <div className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.6)]"></div>
            <span className="text-cyan-300 text-xs font-semibold tracking-wide">Proctoring Dashboard v2.0</span>
          </div>

          <h1 className="text-5xl font-extrabold !text-white leading-[1.15] mb-5 tracking-tight">
            AI Exam Proctoring<br/>
            <span className="bg-gradient-to-r from-[#38BDF8] to-[#C084FC] bg-clip-text text-transparent">
              Supervision
            </span>
          </h1>
          <p className="text-[15px] text-[#8A9BC4] mb-10 leading-relaxed font-medium">
            Elevate your proctoring operations. Harness real-time computer vision paired with generative reasoning to instantly detect, track, and resolve anomalies.
          </p>

          {/* Feature List (Vertical) */}
          <div className="flex flex-col gap-5">
            <div className="flex items-center gap-4 text-sm text-[#E8EEFF] font-medium">
              <div className="p-2 bg-white/5 rounded-lg border border-white/10">
                <Zap className="w-4 h-4 text-[#818CF8]" />
              </div>
              <span>Sub-second real-time object detection</span>
            </div>
            <div className="flex items-center gap-4 text-sm text-[#E8EEFF] font-medium">
              <div className="p-2 bg-white/5 rounded-lg border border-white/10">
                <ShieldCheck className="w-4 h-4 text-[#818CF8]" />
              </div>
              <span>Automated perimeter & loitering alerts</span>
            </div>
            <div className="flex items-center gap-4 text-sm text-[#E8EEFF] font-medium">
              <div className="p-2 bg-white/5 rounded-lg border border-white/10">
                <Video className="w-4 h-4 text-[#818CF8]" />
              </div>
              <span>Seamless multi-stream camera integration</span>
            </div>
          </div>
        </div>

        {/* Footer legalities */}
        <div className="text-xs text-slate-500 font-medium z-10 select-none">
          © {new Date().getFullYear()} AI Exam Proctoring Solutions.
        </div>
      </div>

      {/* RIGHT HALF (50%): Light Theme Form */}
      <div className="w-full lg:w-1/2 h-full flex flex-col justify-center items-center p-8 bg-white z-10">
        
        <div className="w-full max-w-[380px]">
          
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-slate-900 mb-2.5">Welcome Back</h2>
            <p className="text-sm text-slate-500 font-medium">Log in to the Operations Center</p>
          </div>

          {error && (
            <div className="mb-6 bg-red-50 border border-red-100 rounded-xl p-3.5 text-sm text-red-600 font-medium text-center">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            
            {/* Email Field */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-700 tracking-wide block">Work Email</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-4 flex items-center text-slate-400 pointer-events-none">
                  <Mail className="w-4 h-4" />
                </span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-white border border-slate-200 hover:border-slate-300 focus:border-blue-500 rounded-xl py-3.5 pl-11 pr-4 text-sm text-slate-900 focus:outline-none focus:ring-4 focus:ring-blue-500/10 transition-all font-medium placeholder-slate-400 shadow-sm"
                  placeholder="operator@situvision.ai"
                  disabled={isScanning}
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-slate-700 tracking-wide block">Security Key</label>
                <a href="#" className="text-xs font-bold text-blue-600 hover:text-blue-700 transition-colors">Forgot key?</a>
              </div>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-4 flex items-center text-slate-400 pointer-events-none">
                  <Lock className="w-4 h-4" />
                </span>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-white border border-slate-200 hover:border-slate-300 focus:border-blue-500 rounded-xl py-3.5 pl-11 pr-4 text-sm text-slate-900 focus:outline-none focus:ring-4 focus:ring-blue-500/10 transition-all font-medium placeholder-slate-400 shadow-sm"
                  placeholder="••••••••••••"
                  disabled={isScanning}
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isScanning}
              className="w-full mt-2 bg-[#0F172A] hover:bg-[#1E293B] text-white font-bold py-3.5 px-4 rounded-xl text-sm cursor-pointer shadow-md hover:shadow-lg transition-all duration-300 flex items-center justify-center gap-2"
            >
              {isScanning ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Authenticating...</span>
                </>
              ) : (
                <>
                  <span>Sign In to SOC</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>

          </form>
        </div>
      </div>
      
    </div>
  );
}
