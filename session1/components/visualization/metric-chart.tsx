"use client";

import { cn } from "@/lib/utils";
import { ExpandableViz } from "@/components/visualization/expandable-viz";

interface MetricChartProps {
  title: string;
  historyA: { epoch: number; value: number }[];
  historyB: { epoch: number; value: number }[];
  currentEpoch: number;
  labelA?: string;
  labelB?: string;
  formatValue?: (v: number) => string;
  maxY?: number;
  compact?: boolean;
  expandable?: boolean;
  strokeB?: string;
}

function ChartSvg({
  title,
  historyA,
  historyB,
  currentEpoch,
  labelA,
  labelB,
  formatValue,
  maxY,
  compact,
  strokeB,
}: MetricChartProps): React.ReactElement {
  const width = 400;
  const height = compact ? 110 : 160;
  const pad = compact
    ? { top: 10, right: 12, bottom: 22, left: 36 }
    : { top: 16, right: 16, bottom: 28, left: 44 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;

  const visibleA = historyA.filter((p) => p.epoch <= currentEpoch);
  const visibleB = historyB.filter((p) => p.epoch <= currentEpoch);
  const allValues = [...visibleA, ...visibleB].map((p) => p.value);
  const yMax = maxY ?? (allValues.length ? Math.max(...allValues, 0.01) * 1.1 : 1);
  const xMax = Math.max(currentEpoch, historyA.length, historyB.length, 1);

  const toX = (epoch: number): number => pad.left + (epoch / xMax) * plotW;
  const toY = (v: number): number => pad.top + plotH - (v / yMax) * plotH;

  const path = (pts: { epoch: number; value: number }[]): string =>
    pts.map((p, i) => `${i === 0 ? "M" : "L"}${toX(p.epoch)},${toY(p.value)}`).join(" ");

  const colorB = strokeB ?? "var(--lab-activations)";

  return (
    <>
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full" role="img" aria-label={title}>
        {[0, 0.25, 0.5, 0.75, 1].map((t) => {
          const y = pad.top + plotH * (1 - t);
          return (
            <g key={t}>
              <line x1={pad.left} y1={y} x2={width - pad.right} y2={y} stroke="var(--border)" />
              <text x={pad.left - 6} y={y + 4} textAnchor="end" className="fill-[var(--text-muted)] text-[9px]">
                {formatValue?.(yMax * t) ?? (yMax * t).toFixed(3)}
              </text>
            </g>
          );
        })}
        {visibleA.length > 1 ? (
          <path d={path(visibleA)} fill="none" stroke="var(--text-muted)" strokeWidth={2} strokeLinecap="round" />
        ) : null}
        {visibleB.length > 1 ? (
          <path d={path(visibleB)} fill="none" stroke={colorB} strokeWidth={2} strokeLinecap="round" />
        ) : null}
        {currentEpoch > 0 ? (
          <line
            x1={toX(currentEpoch)}
            y1={pad.top}
            x2={toX(currentEpoch)}
            y2={height - pad.bottom}
            stroke="var(--accent-primary)"
            strokeDasharray="4 4"
            opacity={0.6}
          />
        ) : null}
      </svg>
      <div className={cn("flex flex-wrap gap-3 text-xs text-[var(--text-muted)]", compact ? "mt-1 gap-2" : "mt-2")}>
        {labelA ? (
          <span className="flex items-center gap-1.5">
            <span className="h-0.5 w-4 bg-[var(--text-muted)]" />
            {labelA}
          </span>
        ) : null}
        {labelB && visibleB.length > 0 ? (
          <span className="flex items-center gap-1.5">
            <span className="h-0.5 w-4" style={{ background: colorB }} />
            {labelB}
          </span>
        ) : null}
      </div>
    </>
  );
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
  compact = false,
  expandable = false,
  strokeB,
}: MetricChartProps): React.ReactElement {
  const hasData = historyA.length > 1 || historyB.length > 1;
  const chart = (
    <ChartSvg
      title={title}
      historyA={historyA}
      historyB={historyB}
      currentEpoch={currentEpoch}
      labelA={labelA}
      labelB={labelB}
      formatValue={formatValue}
      maxY={maxY}
      compact={compact}
      strokeB={strokeB}
    />
  );

  const panel = (
    <div className={cn("glass-panel", compact ? "p-2" : "p-4")}>
      {!expandable ? (
        <p className={cn("font-medium text-[var(--text-primary)]", compact ? "mb-1 text-xs" : "mb-3 text-sm")}>
          {title}
        </p>
      ) : null}
      {chart}
    </div>
  );

  if (!expandable) return panel;

  return (
    <ExpandableViz
      label={title}
      disabled={!hasData}
      expandedChildren={
        <div className="glass-panel p-4">
          <ChartSvg
            title={title}
            historyA={historyA}
            historyB={historyB}
            currentEpoch={currentEpoch}
            labelA={labelA}
            labelB={labelB}
            formatValue={formatValue}
            maxY={maxY}
            strokeB={strokeB}
          />
        </div>
      }
    >
      {panel}
    </ExpandableViz>
  );
}
