"use client";

interface GeneralizationGraphProps {
  trainHistory: { epoch: number; value: number }[];
  valHistory: { epoch: number; value: number }[];
  currentEpoch: number;
  title?: string;
}

export function GeneralizationGraph({
  trainHistory,
  valHistory,
  currentEpoch,
  title = "Train vs validation loss",
}: GeneralizationGraphProps): React.ReactElement {
  const width = 480;
  const height = 200;
  const pad = { top: 20, right: 16, bottom: 32, left: 48 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;

  const train = trainHistory.filter((p) => p.epoch <= currentEpoch);
  const val = valHistory.filter((p) => p.epoch <= currentEpoch);
  const all = [...train, ...val].map((p) => p.value);
  const yMax = all.length ? Math.max(...all, 0.01) * 1.15 : 1;
  const xMax = Math.max(currentEpoch, trainHistory.length, valHistory.length, 1);

  const toX = (epoch: number): number => pad.left + (epoch / xMax) * plotW;
  const toY = (v: number): number => pad.top + plotH - (v / yMax) * plotH;

  const linePath = (pts: { epoch: number; value: number }[]): string =>
    pts.map((p, i) => `${i === 0 ? "M" : "L"}${toX(p.epoch)},${toY(p.value)}`).join(" ");

  const gapPath =
    train.length > 1 && val.length > 1
      ? [
          ...train.map((p, i) => `${i === 0 ? "M" : "L"}${toX(p.epoch)},${toY(p.value)}`),
          ...[...val].reverse().map((p) => `L${toX(p.epoch)},${toY(p.value)}`),
          "Z",
        ].join(" ")
      : "";

  return (
    <div className="glass-panel p-4">
      <p className="mb-3 text-sm font-medium text-[var(--text-primary)]">{title}</p>
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full" role="img" aria-label={title}>
        {[0, 0.25, 0.5, 0.75, 1].map((t) => {
          const y = pad.top + plotH * (1 - t);
          return (
            <g key={t}>
              <line x1={pad.left} y1={y} x2={width - pad.right} y2={y} stroke="var(--border)" />
              <text x={pad.left - 6} y={y + 4} textAnchor="end" className="fill-[var(--text-muted)] text-[9px]">
                {(yMax * t).toFixed(2)}
              </text>
            </g>
          );
        })}
        {gapPath && (
          <path d={gapPath} fill="var(--lab-generalization)" fillOpacity={0.15} stroke="none" />
        )}
        {train.length > 1 && (
          <path d={linePath(train)} fill="none" stroke="var(--lab-generalization)" strokeWidth={2.5} />
        )}
        {val.length > 1 && (
          <path
            d={linePath(val)}
            fill="none"
            stroke="var(--text-muted)"
            strokeWidth={2}
            strokeDasharray="6 4"
          />
        )}
        {currentEpoch > 0 && (
          <line
            x1={toX(currentEpoch)}
            y1={pad.top}
            x2={toX(currentEpoch)}
            y2={height - pad.bottom}
            stroke="var(--accent-primary)"
            strokeDasharray="4 4"
            opacity={0.5}
          />
        )}
      </svg>
      <div className="mt-2 flex gap-4 text-xs text-[var(--text-muted)]">
        <span className="flex items-center gap-1.5">
          <span className="h-0.5 w-4 bg-[var(--lab-generalization)]" />
          Train loss
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-0.5 w-4 border-t border-dashed border-[var(--text-muted)]" />
          Val loss
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-sm bg-[var(--lab-generalization)] opacity-20" />
          Gap
        </span>
      </div>
    </div>
  );
}
