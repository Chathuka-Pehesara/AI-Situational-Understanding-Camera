import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function HUDOverlay({ phase }) {
  const [typedText, setTypedText] = useState('');
  
  const dialogue = "Hello.\nWelcome to SituVision AI.\nInitializing secure environment.\nAccess Granted.";

  useEffect(() => {
    if (phase === 'GREETING') {
      let index = 0;
      const interval = setInterval(() => {
        setTypedText(dialogue.slice(0, index));
        index++;
        if (index > dialogue.length) clearInterval(interval);
      }, 40);
      return () => clearInterval(interval);
    }
  }, [phase]);

  // High-end spring physics for smooth, heavy animations
  const premiumSpring = { type: "spring", stiffness: 100, damping: 20, mass: 1 };

  return (
    <div className="absolute inset-0 pointer-events-none z-10 flex flex-col justify-between p-8 md:p-12 overflow-hidden text-slate-300 font-sans">
      
      {/* Top Left - Minimal System Status */}
      <AnimatePresence>
        {phase !== 'FADE_IN' && phase !== 'COMPLETE' && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={premiumSpring}
            className="flex items-center gap-3 backdrop-blur-md bg-white/5 border border-white/10 px-4 py-2 rounded-full w-max shadow-lg"
          >
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
            <span className="text-[10px] font-medium tracking-[0.2em] text-white/80 uppercase">
              Secure Link Established
            </span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Top Right - Subtle Auth Streams */}
      <AnimatePresence>
        {(phase === 'SCANNING' || phase === 'GREETING') && (
          <motion.div 
            initial={{ opacity: 0, filter: 'blur(10px)' }}
            animate={{ opacity: 1, filter: 'blur(0px)' }}
            exit={{ opacity: 0, filter: 'blur(10px)' }}
            transition={{ duration: 1, ease: "circOut" }}
            className="absolute top-12 right-12 text-right flex flex-col gap-1"
          >
            <div className="text-[9px] tracking-[0.15em] text-white/40 uppercase">Session Hash</div>
            <div className="text-[11px] tracking-widest text-slate-200 font-mono">0x8A49F2 • VALID</div>
            <div className="mt-2 text-[9px] tracking-[0.15em] text-white/40 uppercase animate-pulse">
              Biometric Scan Active
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Center - Premium Cinematic Reticle */}
      <AnimatePresence>
        {phase === 'SCANNING' && (
          <motion.div 
            initial={{ opacity: 0, scale: 2, rotate: -45 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            exit={{ opacity: 0, scale: 0.5, filter: 'blur(10px)' }}
            transition={premiumSpring}
            className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 flex items-center justify-center pointer-events-none"
          >
            {/* Outer rotating dashed ring */}
            <div className="absolute inset-0 rounded-full border border-white/10 border-dashed animate-[spin_12s_linear_infinite]" />
            {/* Inner dynamic ring */}
            <div className="absolute inset-8 rounded-full border border-white/5 border-t-emerald-400/40 border-b-emerald-400/10 animate-[spin_4s_ease-in-out_infinite]" />
            
            {/* Precision Crosshairs */}
            <div className="absolute top-0 bottom-0 left-1/2 w-[1px] bg-gradient-to-b from-transparent via-white/10 to-transparent" />
            <div className="absolute left-0 right-0 top-1/2 h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent" />
            
            {/* Center target dot */}
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400/80 animate-pulse shadow-[0_0_10px_rgba(52,211,153,0.8)]" />
            
            {/* Soft sweeping radar glow */}
            <div className="absolute inset-2 rounded-full bg-[conic-gradient(from_0deg,transparent,rgba(52,211,153,0.05),transparent)] animate-[spin_2s_linear_infinite]" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Mid Left - Refined Dialogue Panel */}
      <AnimatePresence>
        {(phase === 'GREETING' || phase === 'ACCESS_GRANTED') && (
          <motion.div 
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50, filter: 'blur(5px)' }}
            transition={premiumSpring}
            className="absolute bottom-1/3 left-12 max-w-sm flex flex-col items-start gap-4 p-6 bg-[#0B0F19]/60 backdrop-blur-xl border border-white/10 rounded-2xl shadow-[0_10px_40px_rgba(0,0,0,0.5)]"
          >
            {/* Subtle Voice Waveform */}
            <div className="flex items-end justify-start gap-[3px] h-4 w-full">
              {[...Array(12)].map((_, i) => (
                <div 
                  key={i} 
                  className="w-[2px] bg-emerald-400/80 rounded-full animate-pulse" 
                  style={{ 
                    height: `${Math.random() * 100}%`,
                    animationDelay: `${i * 0.05}s`,
                    animationDuration: '0.6s'
                  }} 
                />
              ))}
            </div>

            <div className="text-sm font-medium tracking-wide whitespace-pre-wrap leading-loose text-left text-white/90">
              {typedText}
              <span className="inline-block w-1.5 h-3 bg-emerald-400 ml-1.5 align-middle animate-pulse rounded-sm" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Access Granted - Superb Glassmorphic Pill Confirmation */}
      <AnimatePresence>
        {phase === 'ACCESS_GRANTED' && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.1, filter: 'blur(10px)' }}
            transition={{ duration: 0.8, type: "spring", bounce: 0.4 }}
            className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center justify-center gap-4 w-full"
          >
            <div className="relative flex items-center justify-center w-full">
              {/* Expanding subtle laser line */}
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: "350px" }}
                transition={{ duration: 1, delay: 0.2, ease: "circOut" }}
                className="h-[1px] bg-gradient-to-r from-transparent via-emerald-400/80 to-transparent absolute shadow-[0_0_20px_rgba(52,211,153,0.5)]"
              />
              
              {/* Glassmorphic Auth Badge */}
              <motion.div 
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.5, type: "spring", bounce: 0.5 }}
                className="px-6 py-3 bg-[#0B0F19]/60 border border-emerald-400/30 backdrop-blur-xl rounded-full z-10 shadow-[0_10px_40px_rgba(52,211,153,0.15)] flex items-center gap-3"
              >
                 <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
                 <span className="text-[11px] font-bold tracking-[0.25em] text-emerald-300 uppercase">
                    Authentication Successful
                 </span>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
    </div>
  );
}
