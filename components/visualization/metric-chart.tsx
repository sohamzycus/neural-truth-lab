"use client";

interface MetricChartProps {
  title: string;
  historyA: { epoch: number; value: number }[];
  historyB: { epoch: number; value: number }[];
  currentEpoch: number;
  labelA?: string;
  labelB?: string;
  formatValue?: (v: number) => string;
  maxY?: number;
}

export function MetricChart({
  title,
  historyA,
  historyB,
  currentEpoch,
  labelA = "Linear",
  labelB = "ReLU",
  formatValue = (v) => v.toFixed(3),
  maxY,
}: MetricChartProps): React.ReactElement {
  const width = 400;
  const height = 160;
  const pad = { top: 16, right: 16, bottom: 28, left: 44 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;

  const visibleA = historyA.filter((p) => p.epoch <= currentEpoch);
  const visibleB = historyB.filter((p) => p.epoch <= currentEpoch);
  const allValues = [...visibleA, ...visibleB].map((p) => p.value);
  const yMax = maxY ?? (allValues.length ? Math.max(...allValues, 0.01) * 1.1 : 1);
  const xMax = Math.max(currentEpoch, historyA.length, historyB.length, 1);

  const toX = (epoch: number): number =>
    pad.left + (epoch / xMax) * plotW;
  const toY = (v: number): number =>
    pad.top + plotH - (v / yMax) * plotH;

  const path = (pts: { epoch: number; value: number }[]): string =>
    pts
      .map((p, i) => `${i === 0 ? "M" : "L"}${toX(p.epoch)},${toY(p.value)}`)
      .join(" ");

  return (
    <div className="glass-panel p-4">
      <p className="mb-3 text-sm font-medium text-[var(--text-primary)]">{title}</p>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full"
        role="img"
        aria-label={`${title} chart`}
      >
        {[0, 0.25, 0.5, 0.75, 1].map((t) => {
          const y = pad.top + plotH * (1 - t);
          return (
            <g key={t}>
              <line
                x1={pad.left}
                y1={y}
                x2={width - pad.right}
                y2={y}
                stroke="var(--border)"
                strokeWidth={1}
              />
              <text
                x={pad.left - 6}
                y={y + 4}
                textAnchor="end"
                className="fill-[var(--text-muted)] text-[9px]"
              >
                {formatValue(yMax * t)}
              </text>
            </g>
          );
        })}
        {visibleA.length > 1 && (
          <path
            d={path(visibleA)}
            fill="none"
            stroke="var(--text-muted)"
            strokeWidth={2}
            strokeLinecap="round"
          />
        )}
        {visibleB.length > 1 && (
          <path
            d={path(visibleB)}
            fill="none"
            stroke="var(--lab-activations)"
            strokeWidth={2}
            strokeLinecap="round"
          />
        )}
        {currentEpoch > 0 && (
          <line
            x1={toX(currentEpoch)}
            y1={pad.top}
            x2={toX(currentEpoch)}
            y2={height - pad.bottom}
            stroke="var(--accent-primary)"
            strokeWidth={1}
            strokeDasharray="4 4"
            opacity={0.6}
          />
        )}
      </svg>
      <div className="mt-2 flex gap-4 text-xs text-[var(--text-muted)]">
        <span className="flex items-center gap-1.5">
          <span className="h-0.5 w-4 bg-[var(--text-muted)]" />
          {labelA}
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-0.5 w-4 bg-[var(--lab-activations)]" />
          {labelB}
        </span>
      </div>
    </div>
  );
}
