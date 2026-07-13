import React, { useRef, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { useGLTF, useAnimations } from '@react-three/drei';
import * as THREE from 'three';

export default function RobotModel({ phase }) {
  const group = useRef();
  
  // Load the provided placeholder robot.glb (or final GLB)
  const { scene, animations } = useGLTF('/models/robot.glb');
  const { actions, names } = useAnimations(animations, group);

  // Crossfade between animations based on the current phase
  useEffect(() => {
    if (!actions || names.length === 0) return;
    
    const animMap = {
      'FADE_IN': 'Idle',
      'WALKING': 'Walking',
      'SCANNING': 'Idle',
      'GREETING': 'Wave',
      'ACCESS_GRANTED': 'ThumbsUp',
      'DISSOLVE': 'Idle'
    };

    const targetAnimName = animMap[phase] || 'Idle';
    const action = actions[targetAnimName] || actions['Idle'];
    
    if (action) {
      action.reset().fadeIn(0.5);
      
      // Don't loop greeting and thumbs up animations (play once and hold)
      if (targetAnimName === 'Wave' || targetAnimName === 'ThumbsUp') {
        action.setLoop(THREE.LoopOnce, 1);
        action.clampWhenFinished = true;
      } else {
        action.setLoop(THREE.LoopRepeat, Infinity);
      }
      
      action.play();
      
      return () => {
        action.fadeOut(0.5);
      };
    }
  }, [phase, actions, names]);

  // Handle positional walking movement
  useFrame((state, delta) => {
    if (phase === 'WALKING' && group.current) {
      // Move the robot forward dynamically. 1.66 units/sec covers 5 units in exactly 3 seconds
      group.current.position.z -= 1.66 * delta;
      
      if (group.current.position.z < 0) {
        group.current.position.z = 0;
      }
    }
  });

  // Setup initial position (start further back in the z-axis)
  useEffect(() => {
    if (group.current) {
      group.current.position.set(0, -1, 5); // Adjust Y based on model pivot
      group.current.rotation.set(0, 0, 0); 
    }
  }, []);

  return (
    <group ref={group} dispose={null}>
      {/* 
        This renders the GLTF scene. 
        We enable shadow casting on all meshes within the scene.
      */}
      <primitive 
        object={scene} 
        scale={0.5} // Scale down the RobotExpressive placeholder (adjust for final)
      />
    </group>
  );
}

// Preload the model so it's instantly ready when the intro starts
useGLTF.preload('/models/robot.glb');
