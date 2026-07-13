import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Environment, PerspectiveCamera, ContactShadows, Sparkles } from '@react-three/drei';
import RobotModel from './RobotModel';
import ParticleSystem from './ParticleSystem';

function CameraRig({ phase }) {
  const group = useRef();
  
  useFrame((state, delta) => {
    const t = state.clock.elapsedTime;
    
    // Base cinematic slow drift (parallax floating)
    let targetX = Math.sin(t * 0.2) * 1.5;
    let targetY = 2.0 + Math.cos(t * 0.3) * 0.3;
    let targetZ = 8.5 + Math.sin(t * 0.1) * 0.5; // Moved further back

    // Dramatic phase-based cinematic camera positioning
    if (phase === 'SCANNING') {
       // Push in slightly and lower angle for scanning
       targetZ = 6.5; // kept further back to avoid clipping
       targetY = 1.6;
       targetX = Math.sin(t * 0.5) * 0.8;
    } else if (phase === 'GREETING') {
       // Angle dramatically to the side for the greeting
       targetX = -2.5; // wider angle
       targetY = 1.8;
       targetZ = 7.5; // further back
    } else if (phase === 'ACCESS_GRANTED' || phase === 'DISSOLVE') {
       // Sweep dramatically to the right and push in to reveal the login screen behind
       targetX = 6;
       targetY = 3.0;
       targetZ = 5.5;
    }

    // Ultra-smooth easing dampening for premium cinematic feel
    state.camera.position.x += (targetX - state.camera.position.x) * (delta * 1.5);
    state.camera.position.y += (targetY - state.camera.position.y) * (delta * 1.5);
    state.camera.position.z += (targetZ - state.camera.position.z) * (delta * 1.5);
    
    // Keep focus dynamically on the robot's upper torso/head
    state.camera.lookAt(0, 1.4, 0);
  });

  return <group ref={group} />;
}

export default function Scene3D({ phase }) {
  return (
    <div className="absolute inset-0 w-full h-full bg-[#02050A]">
      <Canvas shadows>
        <PerspectiveCamera makeDefault position={[0, 2, 8]} fov={45} />
        
        {/* Dynamic Cinematic Lighting */}
        <ambientLight intensity={0.2} />
        <spotLight 
          position={[5, 5, 5]} 
          angle={0.15} 
          penumbra={1} 
          intensity={1.5} 
          castShadow 
          color="#06B6D4" // Cyan hue
        />
        <spotLight 
          position={[-5, 5, -5]} 
          angle={0.15} 
          penumbra={1} 
          intensity={2} 
          color="#8B5CF6" // Purple rim light
        />
        
        {/* Subtle Atmospheric Dust / Sparkles */}
        <Sparkles 
          count={150} 
          scale={12} 
          size={1.5} 
          speed={0.4} 
          opacity={0.3} 
          color="#34D399" // Emerald tint 
        />

        {/* 3D Character Model */}
        {phase !== 'DISSOLVE' && (
          <RobotModel phase={phase} />
        )}

        {/* Particles specifically for the dissolve transition */}
        {phase === 'DISSOLVE' && (
          <ParticleSystem />
        )}

        {/* Beautiful ground reflection/shadow */}
        <ContactShadows position={[0, -0.1, 0]} opacity={0.6} scale={10} blur={2} far={4} color="#06B6D4" />
        
        {/* Realistic HDRI Environment as the background */}
        <Environment preset="night" background blur={0.3} backgroundIntensity={0.2} environmentIntensity={0.8} />
        
        <CameraRig phase={phase} />
      </Canvas>
    </div>
  );
}
