import React, { useState, useEffect } from 'react';
import Scene3D from './Scene3D';
import HUDOverlay from './HUDOverlay';

export default function IntroManager({ onComplete }) {
  const [phase, setPhase] = useState('FADE_IN');

  useEffect(() => {
    // Basic timeline sequence
    const timeline = [
      { delay: 1000, nextPhase: 'WALKING' },
      { delay: 3000, nextPhase: 'SCANNING' }, // Robot stops, scans
      { delay: 3000, nextPhase: 'GREETING' }, // Robot waves and talks
      { delay: 5000, nextPhase: 'ACCESS_GRANTED' }, // Access granted transition
      { delay: 2000, nextPhase: 'DISSOLVE' }, // Fade to login
      { delay: 2000, nextPhase: 'COMPLETE' }, // Unmount
    ];

    let timeouts = [];
    
    const runTimeline = () => {
      let cumulativeDelay = 0;
      for (const step of timeline) {
        cumulativeDelay += step.delay;
        const t = setTimeout(() => {
          if (step.nextPhase === 'COMPLETE') {
            onComplete();
          } else {
            setPhase(step.nextPhase);
          }
        }, cumulativeDelay);
        timeouts.push(t);
      }
    };

    runTimeline();

    return () => {
      timeouts.forEach(t => clearTimeout(t));
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="fixed inset-0 z-50 bg-[#02050A] overflow-hidden">
      {/* 3D Scene Background (Now using realistic HDRI) */}
      <div className="absolute inset-0 z-10">
        <Scene3D phase={phase} />
      </div>
      
      {/* 2D Framer Motion HUD Overlay */}
      <HUDOverlay phase={phase} />
    </div>
  );
}
