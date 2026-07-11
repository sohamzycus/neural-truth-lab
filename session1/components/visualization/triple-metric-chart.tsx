"use client";

import { cn } from "@/lib/utils";
import { ExpandableViz } from "@/components/visualization/expandable-viz";
interface Series {
  id: string;
  label: string;
  color: string;
  history: { epoch: number; value: number }[];
}

interface TripleMetricChartProps {
  title: string;
  series: Series[];
  currentEpoch: number;
  formatValue?: (v: number) => string;
  maxY?: number;
  compact?: boolean;
  expandable?: boolean;
}

function TripleChartBody({
  title,
  series,
  currentEpoch,
  formatValue = (v) => v.toFixed(3),
  maxY,
  compact,
}: TripleMetricChartProps): React.ReactElement {
  const width = 400;
  const height = compact ? 110 : 160;
  const pad = compact
    ? { top: 10, right: 12, bottom: 22, left: 36 }
    : { top: 16, right: 16, bottom: 28, left: 44 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;

  const visible = series.map((s) => ({
    ...s,
    points: s.history.filter((p) => p.epoch <= currentEpoch),
  }));

  const allValues = visible.flatMap((s) => s.points.map((p) => p.value));
  const yMax = maxY ?? (allValues.length ? Math.max(...allValues, 0.01) * 1.1 : 1);
  const xMax = Math.max(
    currentEpoch,
    ...series.map((s) => s.history.length),
    1
  );

  const toX = (epoch: number): number => pad.left + (epoch / xMax) * plotW;
  const toY = (v: number): number => pad.top + plotH - (v / yMax) * plotH;

  const path = (pts: { epoch: number; value: number }[]): string =>
    pts.map((p, i) => `${i === 0 ? "M" : "L"}${toX(p.epoch)},${toY(p.value)}`).join(" ");

  return (
    <>
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full" role="img" aria-label={title}>
        {[0, 0.25, 0.5, 0.75, 1].map((t) => {
          const y = pad.top + plotH * (1 - t);
          return (
            <g key={t}>
              <line x1={pad.left} y1={y} x2={width - pad.right} y2={y} stroke="var(--border)" />
              <text x={pad.left - 6} y={y + 4} textAnchor="end" className="fill-[var(--text-muted)] text-[9px]">
                {formatValue(yMax * t)}
              </text>
            </g>
          );
        })}
        {visible.map((s) =>
          s.points.length > 1 ? (
            <path key={s.id} d={path(s.points)} fill="none" stroke={s.color} strokeWidth={2} strokeLinecap="round" />
          ) : null
        )}
        {currentEpoch > 0 && (
          <line
            x1={toX(currentEpoch)}
            y1={pad.top}
            x2={toX(currentEpoch)}
            y2={height - pad.bottom}
            stroke="var(--accent-primary)"
            strokeDasharray="4 4"
            opacity={0.6}
          />
        )}
      </svg>
      <div className={cn("flex flex-wrap gap-3 text-xs text-[var(--text-muted)]", compact ? "mt-1 gap-2" : "mt-2")}>
        {series.map((s) => (
          <span key={s.id} className="flex items-center gap-1.5">
            <span className="h-0.5 w-4" style={{ background: s.color }} />
            {s.label}
          </span>
        ))}
      </div>
    </>
  );
}

export function TripleMetricChart({
  title,
  series,
  currentEpoch,
  formatValue = (v) => v.toFixed(3),
  maxY,
  compact = false,
  expandable = false,
}: TripleMetricChartProps): React.ReactElement {
  const hasData = series.some((s) => s.history.length > 1);
  const panel = (
    <div className={cn("glass-panel", compact ? "p-2" : "p-4")}>
      {!expandable ? (
        <p className={cn("font-medium text-[var(--text-primary)]", compact ? "mb-1 text-xs" : "mb-3 text-sm")}>
          {title}
        </p>
      ) : null}
      <TripleChartBody
        title={title}
        series={series}
        currentEpoch={currentEpoch}
        formatValue={formatValue}
        maxY={maxY}
        compact={compact}
      />
    </div>
  );

  if (!expandable) return panel;

  return (
    <ExpandableViz
      label={title}
      disabled={!hasData}
      expandedChildren={
        <div className="glass-panel p-4">
          <TripleChartBody
            title={title}
            series={series}
            currentEpoch={currentEpoch}
            maxY={maxY}
          />
        </div>
      }
    >
      {panel}
    </ExpandableViz>
  );
}
