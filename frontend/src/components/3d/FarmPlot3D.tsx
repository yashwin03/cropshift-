import React, { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import FarmScene3D from './FarmScene3D';

interface FarmPlot3DProps {
  selectedCrop: string;
  onSelectCrop?: (crop: string) => void;
  className?: string;
}

function checkWebGLSupport(): boolean {
  if (typeof window === 'undefined' || typeof document === 'undefined') return false;
  try {
    const canvas = document.createElement('canvas');
    return !!(
      window.WebGLRenderingContext &&
      (canvas.getContext('webgl') || canvas.getContext('experimental-webgl') || canvas.getContext('webgl2'))
    );
  } catch {
    return false;
  }
}

export default function FarmPlot3D({ selectedCrop, onSelectCrop, className = '' }: FarmPlot3DProps) {
  const [activeLayer, setActiveLayer] = useState<'all' | 'soil' | 'water' | 'crop'>('all');
  const [hasWebGL, setHasWebGL] = useState<boolean>(true);

  useEffect(() => {
    setHasWebGL(checkWebGLSupport());
  }, []);

  return (
    <div className={`relative w-full h-[420px] sm:h-[480px] bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 shadow-2xl flex flex-col ${className}`}>
      {/* Real WebGL R3F 3D Canvas */}
      {hasWebGL ? (
        <Canvas
          shadows
          camera={{ position: [9, 10, 12], fov: 45 }}
          className="w-full h-full cursor-grab active:cursor-grabbing"
        >
          <color attach="background" args={['#06130d']} />
          <FarmScene3D selectedCrop={selectedCrop} activeLayer={activeLayer} />
          <OrbitControls
            enableDamping
            dampingFactor={0.05}
            minDistance={6}
            maxDistance={22}
            maxPolarAngle={Math.PI / 2 - 0.05}
          />
        </Canvas>
      ) : (
        /* Graceful Fallback Container for Non-WebGL / Test Environments */
        <div className="w-full h-full flex flex-col items-center justify-center p-6 bg-slate-950 text-slate-300 text-center space-y-3">
          <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-2xl font-black">
            🌱
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">WebGL 3D Crop Simulator</h3>
            <p className="text-xs text-slate-400 mt-1">
              Currently simulating <span className="text-emerald-400 font-bold">{selectedCrop || 'Groundnut'}</span> plot.
            </p>
          </div>
        </div>
      )}

      {/* Layer Toggle Chips & Controls HUD */}
      <div className="absolute top-4 right-4 flex flex-col gap-2 z-10">
        <button
          type="button"
          onClick={() => {
            const layers: Array<'all' | 'soil' | 'water' | 'crop'> = ['all', 'soil', 'water', 'crop'];
            const nextIdx = (layers.indexOf(activeLayer) + 1) % layers.length;
            setActiveLayer(layers[nextIdx]);
          }}
          className="px-3 py-2 bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-xl text-slate-200 hover:text-white text-xs font-extrabold shadow-lg transition-all flex items-center gap-1.5"
          title="Toggle Layers"
        >
          <span>🥞</span>
          <span className="capitalize">{activeLayer} Layer</span>
        </button>
      </div>

      {/* Selected Crop Badge & Helper Text */}
      <div className="absolute bottom-3 left-4 z-10 flex items-center gap-2">
        <div className="text-[11px] font-black text-emerald-400 bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-emerald-500/40 shadow-lg">
          Active 3D Plot: {selectedCrop || 'Groundnut'}
        </div>
        <div className="hidden sm:block text-[10px] text-slate-400 font-mono bg-slate-950/80 px-2.5 py-1.5 rounded-lg border border-slate-800/80">
          💡 Drag to Orbit 3D Camera | Scroll to Zoom
        </div>
      </div>
    </div>
  );
}
