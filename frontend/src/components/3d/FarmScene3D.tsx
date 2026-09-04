import React from 'react';
import CropMeshRenderer3D from './CropMeshRenderer3D';

interface FarmScene3DProps {
  selectedCrop: string;
  activeLayer: 'all' | 'soil' | 'water' | 'crop';
}

export default function FarmScene3D({ selectedCrop, activeLayer }: FarmScene3DProps) {
  const showSoil = activeLayer === 'all' || activeLayer === 'soil';
  const showWater = activeLayer === 'all' || activeLayer === 'water';
  const showCrops = activeLayer === 'all' || activeLayer === 'crop';

  return (
    <group>
      {/* 1. Real WebGL 3D Lighting */}
      <ambientLight intensity={0.8} />
      <directionalLight
        position={[12, 18, 12]}
        intensity={1.3}
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />
      <pointLight position={[-10, 10, -10]} intensity={0.5} color="#38bdf8" />

      {/* 2. Real 3D Soil/Terrain Platform Geometry */}
      <mesh position={[0, -0.2, 0]} receiveShadow>
        <boxGeometry args={[14, 0.4, 14]} />
        <meshStandardMaterial color="#1c140e" roughness={0.85} metalness={0.1} />
      </mesh>

      {/* Top Green Field Surface Mesh */}
      <mesh position={[0, 0.01, 0]} receiveShadow>
        <planeGeometry args={[13.6, 13.6]} />
        <meshStandardMaterial color="#14532d" roughness={0.7} />
      </mesh>

      {/* 3. Soil Cutaway Sub-layer Geometry */}
      {showSoil && (
        <group position={[0, -1.4, 0]}>
          <mesh>
            <boxGeometry args={[13.6, 2.0, 13.6]} />
            <meshStandardMaterial color="#0f0b07" roughness={0.9} />
          </mesh>
          <mesh position={[0, -0.3, 0]}>
            <boxGeometry args={[13.7, 0.4, 13.7]} />
            <meshStandardMaterial color="#291b12" roughness={0.9} />
          </mesh>
        </group>
      )}

      {/* 4. Irrigation Water Channel Mesh */}
      {showWater && (
        <mesh position={[0, 0.03, 0]} receiveShadow>
          <boxGeometry args={[1.6, 0.06, 13.6]} />
          <meshStandardMaterial color="#0284c7" transparent opacity={0.85} roughness={0.1} metalness={0.2} />
        </mesh>
      )}

      {/* 5. Glowing Green Boundary Ring */}
      <mesh position={[0, 0.04, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[7.0, 7.15, 32]} />
        <meshBasicMaterial color="#10b981" transparent opacity={0.6} />
      </mesh>

      {/* 6. Real 3D Crop Field Models */}
      {showCrops && <CropMeshRenderer3D cropName={selectedCrop} count={25} />}
    </group>
  );
}
