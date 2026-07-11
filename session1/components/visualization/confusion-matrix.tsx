"use client";

import { ExpandableViz } from "@/components/visualization/expandable-viz";

interface ConfusionMatrixProps {
  matrix: number[][] | undefined;
  label?: string;
  compact?: boolean;
  expandable?: boolean;
}

function MatrixGrid({
  matrix,
  compact,
}: {
  matrix: number[][];
  compact?: boolean;
}): React.ReactElement {
  const max = Math.max(...matrix.flat(), 1);

  return (
    <>
      <div className="grid grid-cols-2 gap-1">
        {matrix.flat().map((val, i) => (
          <div
            key={i}
            className={`flex items-center justify-center rounded-lg font-mono ${compact ? "aspect-square text-xs" : "aspect-square text-sm"}`}
            style={{
              background: `rgba(99, 102, 241, ${0.1 + (val / max) * 0.5})`,
            }}
          >
            {val}
          </div>
        ))}
      </div>
      <div className="mt-2 grid grid-cols-2 gap-1 text-center text-[10px] text-[var(--text-muted)]">
        <span>Pred 0</span>
        <span>Pred 1</span>
      </div>
    </>
  );
}

export function ConfusionMatrix({
  matrix,
  label,
  compact = false,
  expandable = false,
}: ConfusionMatrixProps): React.ReactElement {
  const data = matrix ?? [
    [0, 0],
    [0, 0],
  ];
  const hasData = matrix !== undefined;

  const panel = (
    <div className={`glass-panel ${compact ? "p-2" : "p-4"}`}>
      {!expandable && label ? (
        <p className="mb-2 text-xs font-medium text-[var(--text-secondary)] sm:text-sm">{label}</p>
      ) : null}
      <MatrixGrid matrix={data} compact={compact} />
    </div>
  );

  if (!expandable) return panel;

  return (
    <ExpandableViz
      label={label}
      disabled={!hasData}
      expandedChildren={
        <div className="glass-panel mx-auto max-w-xs p-6">
          <MatrixGrid matrix={data} />
        </div>
      }
    >
      {panel}
    </ExpandableViz>
  );
}
