"use client";

import { useEffect, useRef } from "react";
import { getGridConfig } from "@/training/metrics";

interface DecisionBoundaryProps {
  grid: Float32Array | null;
  features: Float32Array;
  labels: Float32Array;
  sampleCount: number;
  label?: string;
  className?: string;
}

export function DecisionBoundary({
  grid,
  features,
  labels,
  sampleCount,
  label,
  className,
}: DecisionBoundaryProps): React.ReactElement {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { gridSize, bounds } = getGridConfig();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const size = canvas.clientWidth;
    canvas.width = size * dpr;
    canvas.height = size * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const w = size;
    const h = size;

    const toX = (v: number): number => ((v + bounds) / (2 * bounds)) * w;
    const toY = (v: number): number => h - ((v + bounds) / (2 * bounds)) * h;

    ctx.fillStyle = "#0a0a0f";
    ctx.fillRect(0, 0, w, h);

    if (grid) {
      const cellW = w / gridSize;
      const cellH = h / gridSize;
      for (let row = 0; row < gridSize; row++) {
        for (let col = 0; col < gridSize; col++) {
          const p = grid[row * gridSize + col];
          const r = Math.round(99 + p * 80);
          const g = Math.round(102 - p * 40);
          const b = Math.round(241 - p * 100);
          const a = 0.25 + Math.abs(p - 0.5) * 0.35;
          ctx.fillStyle = `rgba(${r},${g},${b},${a})`;
          ctx.fillRect(col * cellW, row * cellH, cellW + 1, cellH + 1);
        }
      }
    }

    for (let i = 0; i < sampleCount; i++) {
      const x = features[i * 2];
      const y = features[i * 2 + 1];
      const isOuter = labels[i] >= 0.5;
      ctx.beginPath();
      ctx.arc(toX(x), toY(y), 3, 0, Math.PI * 2);
      ctx.fillStyle = isOuter ? "#f97316" : "#6366f1";
      ctx.fill();
      ctx.strokeStyle = "rgba(255,255,255,0.3)";
      ctx.lineWidth = 0.5;
      ctx.stroke();
    }

    if (grid) {
      ctx.strokeStyle = "rgba(255,255,255,0.35)";
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      let started = false;
      const step = (2 * bounds) / (gridSize - 1);
      for (let row = 0; row < gridSize; row++) {
        for (let col = 0; col < gridSize; col++) {
          const p = grid[row * gridSize + col];
          const px = -bounds + col * step;
          const py = -bounds + row * step;
          const onBoundary =
            p >= 0.48 &&
            p <= 0.52 &&
            (col === 0 ||
              col === gridSize - 1 ||
              row === 0 ||
              row === gridSize - 1 ||
              Math.abs(grid[row * gridSize + col - 1] - 0.5) > 0.05 ||
              Math.abs(grid[row * gridSize + col + 1] - 0.5) > 0.05);
          if (onBoundary) {
            if (!started) {
              ctx.moveTo(toX(px), toY(py));
              started = true;
            } else {
              ctx.lineTo(toX(px), toY(py));
            }
          }
        }
      }
      ctx.stroke();
    }
  }, [grid, features, labels, sampleCount, gridSize, bounds]);

  return (
    <div className={className}>
      {label && (
        <p className="mb-2 text-sm font-medium text-[var(--text-secondary)]">
          {label}
        </p>
      )}
      <canvas
        ref={canvasRef}
        className="aspect-square w-full rounded-xl border border-[var(--border)] bg-[var(--background-elevated)]"
        aria-label={label ?? "Decision boundary visualization"}
      />
    </div>
  );
}
