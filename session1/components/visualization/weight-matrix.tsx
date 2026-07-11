"use client";

import { useMemo } from "react";
import { kernelLabels } from "@/training/weight-collapse";

interface WeightMatrixProps {
  matrix: number[][];
  label: string;
  className?: string;
}

function heatColor(v: number, min: number, max: number): string {
  const t = max === min ? 0.5 : (v - min) / (max - min);
  const r = Math.round(99 + t * 80);
  const g = Math.round(102 + t * 40);
  const b = Math.round(241 - t * 120);
  return `rgb(${r},${g},${b})`;
}

export function WeightMatrix({
  matrix,
  label,
  className,
}: WeightMatrixProps): React.ReactElement {
  const { min, max, rows, cols } = useMemo(() => {
    const flat = matrix.flat();
    return {
      min: Math.min(...flat),
      max: Math.max(...flat),
      rows: matrix.length,
      cols: matrix[0]?.length ?? 0,
    };
  }, [matrix]);

  return (
    <div className={className}>
      <p className="mb-2 text-xs font-mono text-[var(--text-secondary)]">{label}</p>
      <div
        className="grid gap-px overflow-hidden rounded-lg border border-[var(--border)]"
        style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}
      >
        {matrix.flatMap((row, ri) =>
          row.map((val, ci) => (
            <div
              key={`${ri}-${ci}`}
              className="aspect-square min-h-3"
              style={{ background: heatColor(val, min, max) }}
              title={val.toFixed(3)}
            />
          ))
        )}
      </div>
      <p className="mt-1 text-[10px] text-[var(--text-muted)]">
        {rows}×{cols}
      </p>
    </div>
  );
}

interface WeightMatrixGridProps {
  matrices: number[][][] | undefined;
}

export function WeightMatrixGrid({ matrices }: WeightMatrixGridProps): React.ReactElement | null {
  if (!matrices?.length) return null;
  const labels = kernelLabels(matrices);

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
      {matrices.map((m, i) => (
        <WeightMatrix key={labels[i]} matrix={m} label={labels[i]} />
      ))}
    </div>
  );
}
