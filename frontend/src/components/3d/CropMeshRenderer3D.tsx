import React, { useMemo } from 'react';
import * as THREE from 'three';

interface CropMeshRenderer3DProps {
  cropName: string;
  count?: number;
}

export default function CropMeshRenderer3D({ cropName, count = 25 }: CropMeshRenderer3DProps) {
  const normalizedCrop = (cropName || 'Groundnut').toLowerCase();

  // Generate grid positions for 3D plants on the farm field
  const plantPositions = useMemo(() => {
    const pos: Array<[number, number, number]> = [];
    const side = Math.floor(Math.sqrt(count));
    const step = 9 / (side - 1 || 1);
    for (let i = 0; i < side; i++) {
      for (let j = 0; j < side; j++) {
        const x = -4.5 + j * step + (Math.random() * 0.3 - 0.15);
        const z = -4.5 + i * step + (Math.random() * 0.3 - 0.15);
        pos.push([x, 0, z]);
      }
    }
    return pos;
  }, [count]);

  if (normalizedCrop.includes('sunflower')) {
    return (
      <group>
        {plantPositions.map(([x, y, z], idx) => (
          <group key={idx} position={[x, y, z]}>
            {/* Tall Stem */}
            <mesh position={[0, 1.0, 0]} castShadow>
              <cylinderGeometry args={[0.07, 0.09, 2.0, 8]} />
              <meshStandardMaterial color="#15803d" roughness={0.6} />
            </mesh>
            {/* Broad Foliage */}
            <mesh position={[0, 0.9, 0]} castShadow>
              <dodecahedronGeometry args={[0.35]} />
              <meshStandardMaterial color="#16a34a" roughness={0.5} />
            </mesh>
            {/* Large Flower Disc */}
            <mesh position={[0, 2.0, 0.1]} rotation={[Math.PI / 6, 0, 0]} castShadow>
              <cylinderGeometry args={[0.5, 0.5, 0.1, 16]} />
              <meshStandardMaterial color="#eab308" roughness={0.3} />
            </mesh>
            {/* Seed Center */}
            <mesh position={[0, 2.05, 0.15]} rotation={[Math.PI / 6, 0, 0]}>
              <cylinderGeometry args={[0.3, 0.3, 0.12, 16]} />
              <meshStandardMaterial color="#78350f" roughness={0.8} />
            </mesh>
          </group>
        ))}
      </group>
    );
  }

  if (normalizedCrop.includes('sesame')) {
    return (
      <group>
        {plantPositions.map(([x, y, z], idx) => (
          <group key={idx} position={[x, y, z]}>
            {/* Upright Stem */}
            <mesh position={[0, 0.8, 0]} castShadow>
              <cylinderGeometry args={[0.05, 0.06, 1.6, 8]} />
              <meshStandardMaterial color="#166534" roughness={0.5} />
            </mesh>
            {/* Elongated Capsules */}
            <mesh position={[0, 1.3, 0]} castShadow>
              <coneGeometry args={[0.12, 0.4, 6]} />
              <meshStandardMaterial color="#15803d" roughness={0.4} />
            </mesh>
            {/* Light blooms */}
            <mesh position={[0, 1.6, 0]}>
              <sphereGeometry args={[0.1, 8, 8]} />
              <meshStandardMaterial color="#fef08a" emissive="#fef08a" emissiveIntensity={0.2} />
            </mesh>
          </group>
        ))}
      </group>
    );
  }

  if (normalizedCrop.includes('mustard')) {
    return (
      <group>
        {plantPositions.map(([x, y, z], idx) => (
          <group key={idx} position={[x, y, z]}>
            {/* Upright Stem */}
            <mesh position={[0, 0.7, 0]} castShadow>
              <cylinderGeometry args={[0.04, 0.05, 1.4, 8]} />
              <meshStandardMaterial color="#15803d" roughness={0.5} />
            </mesh>
            {/* Yellow Flower Tops */}
            <mesh position={[0, 1.4, 0]} castShadow>
              <sphereGeometry args={[0.26, 8, 8]} />
              <meshStandardMaterial color="#facc15" roughness={0.3} emissive="#facc15" emissiveIntensity={0.15} />
            </mesh>
          </group>
        ))}
      </group>
    );
  }

  if (normalizedCrop.includes('soybean')) {
    return (
      <group>
        {plantPositions.map(([x, y, z], idx) => (
          <group key={idx} position={[x, y, z]}>
            {/* Bushy Stem */}
            <mesh position={[0, 0.5, 0]} castShadow>
              <cylinderGeometry args={[0.04, 0.05, 1.0, 8]} />
              <meshStandardMaterial color="#14532d" roughness={0.6} />
            </mesh>
            {/* Leaf Cluster */}
            <mesh position={[0, 0.9, 0]} castShadow>
              <sphereGeometry args={[0.34, 10, 10]} />
              <meshStandardMaterial color="#4ade80" roughness={0.5} />
            </mesh>
          </group>
        ))}
      </group>
    );
  }

  // Default: Groundnut
  return (
    <group>
      {plantPositions.map(([x, y, z], idx) => (
        <group key={idx} position={[x, y, z]}>
          {/* Stem */}
          <mesh position={[0, 0.25, 0]} castShadow>
            <cylinderGeometry args={[0.04, 0.05, 0.5, 8]} />
            <meshStandardMaterial color="#166534" roughness={0.6} />
          </mesh>
          {/* Canopy */}
          <mesh position={[0, 0.45, 0]} castShadow>
            <sphereGeometry args={[0.28, 10, 10]} />
            <meshStandardMaterial color="#22c55e" roughness={0.5} />
          </mesh>
          {/* Underground pods indicator */}
          <mesh position={[0, -0.05, 0]}>
            <sphereGeometry args={[0.08, 6, 6]} />
            <meshStandardMaterial color="#a16207" roughness={0.9} />
          </mesh>
        </group>
      ))}
    </group>
  );
}
