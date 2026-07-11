"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ZoomIn, X } from "lucide-react";
import { drawDecisionBoundary } from "@/lib/draw-decision-boundary";
import { cn } from "@/lib/utils";

interface DecisionBoundaryProps {
  grid: Float32Array | null;
  features: Float32Array;
  labels: Float32Array;
  sampleCount: number;
  label?: string;
  className?: string;
  compact?: boolean;
  expandable?: boolean;
}

function useBoundaryPaint(
  canvasRef: React.RefObject<HTMLCanvasElement | null>,
  data: DrawData,
  active: boolean
): void {
  const paint = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !active) return;
    drawDecisionBoundary(canvas, data);
  }, [canvasRef, data, active]);

  useEffect(() => {
    paint();
    const canvas = canvasRef.current;
    if (!canvas || !active) return;
    const ro = new ResizeObserver(() => paint());
    ro.observe(canvas);
    return () => ro.disconnect();
  }, [paint, canvasRef, active]);
}

interface DrawData {
  grid: Float32Array | null;
  features: Float32Array;
  labels: Float32Array;
  sampleCount: number;
}

export function DecisionBoundary({
  grid,
  features,
  labels,
  sampleCount,
  label,
  className,
  compact = false,
  expandable = false,
}: DecisionBoundaryProps): React.ReactElement {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const expandedCanvasRef = useRef<HTMLCanvasElement>(null);
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [expanded, setExpanded] = useState(false);

  const data: DrawData = { grid, features, labels, sampleCount };

  useBoundaryPaint(canvasRef, data, true);
  useBoundaryPaint(expandedCanvasRef, data, expanded);

  const openExpanded = (): void => {
    if (!expandable || !grid) return;
    setExpanded(true);
    dialogRef.current?.showModal();
  };

  const closeExpanded = (): void => {
    setExpanded(false);
    dialogRef.current?.close();
  };

  const canvasClass = cn(
    "w-full rounded-lg border border-[var(--border)] bg-[var(--viz-canvas-bg)]",
    compact ? "lab-viz-canvas-compact" : "lab-viz-canvas aspect-square"
  );

  return (
    <div className={className}>
      {label ? (
        <p className="mb-1.5 text-xs font-medium text-[var(--text-secondary)] sm:text-sm">
          {label}
        </p>
      ) : null}

      {expandable ? (
        <button
          type="button"
          onClick={openExpanded}
          disabled={!grid}
          className={cn(
            "group relative w-full text-left",
            !grid && "cursor-default"
          )}
          aria-label={label ? `Expand ${label}` : "Expand decision boundary"}
        >
          <canvas
            ref={canvasRef}
            className={cn(canvasClass, grid && "cursor-zoom-in")}
            aria-hidden
          />
          {grid ? (
            <span className="pointer-events-none absolute inset-0 flex items-end justify-end rounded-lg bg-gradient-to-t from-stone-900/25 via-transparent to-transparent p-2 opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100">
              <span className="flex items-center gap-1 rounded-md bg-white/95 px-2 py-1 text-[10px] font-medium text-stone-800 shadow-sm">
                <ZoomIn className="h-3 w-3" />
                Expand
              </span>
            </span>
          ) : null}
        </button>
      ) : (
        <canvas
          ref={canvasRef}
          className={canvasClass}
          aria-label={label ?? "Decision boundary visualization"}
        />
      )}

      {expandable ? (
        <dialog
          ref={dialogRef}
          onClose={closeExpanded}
          className="max-h-[95vh] w-[min(100%,42rem)] max-w-[calc(100vw-1.5rem)] rounded-xl border border-[var(--border)] bg-[var(--background-elevated)] p-0 text-[var(--text-primary)] shadow-2xl backdrop:bg-stone-900/40 backdrop:backdrop-blur-sm"
          aria-label={label ?? "Expanded decision boundary"}
        >
          <div className="flex items-center justify-between gap-3 border-b border-[var(--border)] px-4 py-3">
            <p className="text-sm font-semibold">{label ?? "Decision boundary"}</p>
            <button
              type="button"
              onClick={closeExpanded}
              className="rounded-lg border border-[var(--border)] p-1.5 text-[var(--text-muted)] hover:bg-[var(--surface)] hover:text-[var(--text-primary)]"
              aria-label="Close"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <div className="p-4">
            <canvas
              ref={expandedCanvasRef}
              className="lab-viz-canvas-expanded aspect-square w-full rounded-lg border border-[var(--border)] bg-[var(--viz-canvas-bg)]"
            />
            <p className="mt-2 text-center text-xs text-[var(--text-muted)]">
              Esc to close · click backdrop to dismiss
            </p>
          </div>
        </dialog>
      ) : null}
    </div>
  );
}
