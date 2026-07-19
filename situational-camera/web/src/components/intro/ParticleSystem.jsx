import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export default function ParticleSystem() {
  const pointsRef = useRef();
  
  const particleCount = 2000;
  
  const [positions, initialPositions, velocities] = useMemo(() => {
    const pos = new Float32Array(particleCount * 3);
    const initPos = new Float32Array(particleCount * 3);
    const vel = new Float32Array(particleCount * 3);
    
    // Create particles roughly in the shape of the robot
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      // Cylinder / Capsule shape bounds
      const r = Math.random() * 0.8;
      const theta = Math.random() * Math.PI * 2;
      const y = Math.random() * 2.5 - 0.5; // Height -0.5 to 2.0
      
      const x = r * Math.cos(theta);
      const z = r * Math.sin(theta);
      
      pos[i3] = x;
      pos[i3 + 1] = y;
      pos[i3 + 2] = z;
      
      initPos[i3] = x;
      initPos[i3 + 1] = y;
      initPos[i3 + 2] = z;
      
      // Elegant digital ascension
      vel[i3] = (Math.random() - 0.5) * 1.5; // slow horizontal drift
      vel[i3 + 1] = (Math.random() * 4) + 1; // strong upward motion
      vel[i3 + 2] = (Math.random() - 0.5) * 1.5;
    }
    
    return [pos, initPos, vel];
  }, [particleCount]);

  useFrame((state, delta) => {
    if (!pointsRef.current) return;
    
    const positions = pointsRef.current.geometry.attributes.position.array;
    
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      // Move particles
      positions[i3] += velocities[i3] * delta;
      positions[i3 + 1] += velocities[i3 + 1] * delta;
      positions[i3 + 2] += velocities[i3 + 2] * delta;
      
      // Gentle swirling effect
      velocities[i3] += Math.sin(state.clock.elapsedTime + i) * 0.02;
      velocities[i3 + 2] += Math.cos(state.clock.elapsedTime + i) * 0.02;
      
      // Accelerate upward
      velocities[i3 + 1] += 0.05; 
    }
    
    pointsRef.current.geometry.attributes.position.needsUpdate = true;
    
    // Smooth cinematic fade out
    if (pointsRef.current.material.opacity > 0) {
      pointsRef.current.material.opacity -= delta * 0.4; // Fades out a bit slower
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particleCount}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.06}
        color="#34D399" // Match the emerald theme
        transparent
        opacity={1}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}
