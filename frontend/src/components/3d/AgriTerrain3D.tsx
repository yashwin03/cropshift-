import React, { useEffect, useRef } from 'react';

interface AgriTerrain3DProps {
  activeRole: 'farmer' | 'buyer';
}

export default function AgriTerrain3D({ activeRole }: AgriTerrain3DProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || typeof canvas.getContext !== 'function') return;
    let ctx: CanvasRenderingContext2D | null = null;
    try {
      ctx = canvas.getContext('2d');
    } catch {
      return;
    }
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    // Mouse tilt interaction
    let mouseX = 0;
    let mouseY = 0;
    let targetMouseX = 0;
    let targetMouseY = 0;

    const handleMouseMove = (e: MouseEvent) => {
      targetMouseX = (e.clientX / window.innerWidth - 0.5) * 2;
      targetMouseY = (e.clientY / window.innerHeight - 0.5) * 2;
    };
    window.addEventListener('mousemove', handleMouseMove);

    // Check reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Grid particles & telemetry nodes
    const cols = 28;
    const rows = 20;
    let time = 0;

    // Dynamic data floating labels
    const telemetryNodes = [
      { text: 'SOIL pH: 7.2 [OPTIMAL]', xRatio: 0.15, yRatio: 0.25, phase: 0 },
      { text: 'DHARWAD APMC: ₹6,200/Q', xRatio: 0.82, yRatio: 0.2, phase: 2 },
      { text: 'OILSEED DEMAND: +18%', xRatio: 0.85, yRatio: 0.75, phase: 4 },
      { text: 'WATER RISK: LOW (88%)', xRatio: 0.12, yRatio: 0.78, phase: 1 },
      { text: 'HIGH MATCH: KADIR-6', xRatio: 0.5, yRatio: 0.12, phase: 3 },
    ];

    const render = () => {
      time += prefersReducedMotion ? 0.002 : 0.015;
      mouseX += (targetMouseX - mouseX) * 0.05;
      mouseY += (targetMouseY - mouseY) * 0.05;

      // Dark background gradient
      const isFarmer = activeRole === 'farmer';
      const bgGradient = ctx.createRadialGradient(
        width * 0.5 + mouseX * 50,
        height * 0.4 + mouseY * 50,
        100,
        width * 0.5,
        height * 0.5,
        Math.max(width, height)
      );

      if (isFarmer) {
        bgGradient.addColorStop(0, '#0a2e1d');
        bgGradient.addColorStop(0.5, '#051b12');
        bgGradient.addColorStop(1, '#020b07');
      } else {
        bgGradient.addColorStop(0, '#0d2847');
        bgGradient.addColorStop(0.5, '#07162b');
        bgGradient.addColorStop(1, '#020814');
      }

      ctx.fillStyle = bgGradient;
      ctx.fillRect(0, 0, width, height);

      // Render 3D Topographic Terrain Mesh
      const horizonY = height * 0.42;
      const fov = 350;
      const baseColor = isFarmer ? '16, 185, 129' : '59, 130, 246';
      const accentColor = isFarmer ? '132, 204, 22' : '14, 165, 233';

      ctx.save();
      ctx.lineWidth = 1;

      // Draw grid lines (perspective projection)
      for (let r = 0; r < rows; r++) {
        const z = (r + 1) * 35;
        const scale = fov / (fov + z);
        const nextZ = (r + 2) * 35;
        const nextScale = fov / (fov + nextZ);

        const py = horizonY + z * 0.75 + mouseY * 25;
        const nextPy = horizonY + nextZ * 0.75 + mouseY * 25;
        const alpha = Math.max(0, 1 - r / rows);

        ctx.strokeStyle = `rgba(${baseColor}, ${alpha * 0.25})`;

        for (let c = -cols / 2; c <= cols / 2; c++) {
          const x = c * 75 + mouseX * 40;
          const px = width * 0.5 + x * scale;
          const nextPx = width * 0.5 + x * nextScale;

          // Undulating heightmap calculation
          const wave1 = Math.sin(c * 0.3 + time + r * 0.2) * 15;
          const wave2 = Math.cos(r * 0.4 - time * 0.8) * 10;
          const offset = wave1 + wave2;

          if (c === -cols / 2) {
            ctx.beginPath();
            ctx.moveTo(px, py + offset * scale);
          } else {
            ctx.lineTo(px, py + offset * scale);
          }

          // Vertical grid segment
          ctx.beginPath();
          ctx.moveTo(px, py + offset * scale);
          ctx.lineTo(nextPx, nextPy + offset * nextScale);
          ctx.stroke();
        }

        ctx.stroke();
      }

      // Draw Glowing Telemetry Nodes (3D crop markers)
      for (let i = 0; i < 18; i++) {
        const nodeX = width * (0.1 + ((i * 37) % 80) / 100) + mouseX * 20;
        const nodeZ = 100 + ((i * 43) % 400);
        const scale = fov / (fov + nodeZ);
        const nodeY = horizonY + nodeZ * 0.7 + Math.sin(time * 2 + i) * 8 + mouseY * 15;

        // Glowing dot
        const pulse = 2 + Math.sin(time * 3 + i) * 1.5;
        ctx.fillStyle = `rgba(${accentColor}, ${0.6 + Math.sin(time * 2 + i) * 0.3})`;
        ctx.beginPath();
        ctx.arc(nodeX, nodeY, pulse * scale * 2, 0, Math.PI * 2);
        ctx.fill();

        // Vertical beam from terrain node
        ctx.strokeStyle = `rgba(${baseColor}, ${0.15 * scale})`;
        ctx.beginPath();
        ctx.moveTo(nodeX, nodeY);
        ctx.lineTo(nodeX, nodeY - 60 * scale);
        ctx.stroke();
      }

      // Render Floating Data Signals HUD
      ctx.font = '9px monospace';
      telemetryNodes.forEach((node) => {
        const nx = width * node.xRatio + Math.sin(time + node.phase) * 12 + mouseX * 15;
        const ny = height * node.yRatio + Math.cos(time * 0.8 + node.phase) * 10 + mouseY * 15;

        ctx.fillStyle = `rgba(${accentColor}, 0.85)`;
        ctx.strokeStyle = `rgba(${baseColor}, 0.4)`;
        ctx.beginPath();
        ctx.arc(nx - 8, ny - 3, 3, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = 'rgba(255, 255, 255, 0.75)';
        ctx.fillText(node.text, nx, ny);
      });

      ctx.restore();

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, [activeRole]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 w-full h-full pointer-events-none z-0"
      aria-hidden="true"
    />
  );
}
