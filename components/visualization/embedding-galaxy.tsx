"use client";

import { useMemo } from "react";
import { motion } from "framer-motion";
import type { TokenCategory } from "@/datasets/synthetic-language";
import type { Point2D } from "@/visualization/embedding-projection";

const CATEGORY_COLOR: Record<TokenCategory, string> = {
  animal: "#6366f1",
  fruit: "#22c55e",
  verb: "#f59e0b",
  other: "#a1a1aa",
};

interface EmbeddingGalaxyProps {
  points: Point2D[];
  categories: Record<string, TokenCategory>;
  frequencies: Record<string, number>;
  selectedTokenId: number | null;
  neighborIds: number[];
  onSelect: (tokenId: number | null) => void;
}

function scalePoints(points: Point2D[]): Point2D[] {
  if (points.length === 0) return points;
  const xs = points.map((p) => p.x);
  const ys = points.map((p) => p.y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const rx = maxX - minX || 1;
  const ry = maxY - minY || 1;
  return points.map((p) => ({
    ...p,
    x: 40 + ((p.x - minX) / rx) * 320,
    y: 40 + ((p.y - minY) / ry) * 320,
  }));
}

export function EmbeddingGalaxy({
  points,
  categories,
  frequencies,
  selectedTokenId,
  neighborIds,
  onSelect,
}: EmbeddingGalaxyProps): React.ReactElement {
  const scaled = useMemo(() => scalePoints(points), [points]);
  const byId = useMemo(
    () => Object.fromEntries(scaled.map((p) => [p.tokenId, p])),
    [scaled]
  );

  const maxFreq = Math.max(...Object.values(frequencies), 1);

  return (
    <div className="glass-panel relative aspect-square w-full overflow-hidden rounded-xl border border-[var(--border)] bg-[radial-gradient(ellipse_at_center,rgba(168,85,247,0.12)_0%,transparent_70%)]">
      <svg viewBox="0 0 400 400" className="h-full w-full">
        {selectedTokenId !== null &&
          neighborIds.map((nid) => {
            const from = byId[selectedTokenId];
            const to = byId[nid];
            if (!from || !to) return null;
            return (
              <line
                key={nid}
                x1={from.x}
                y1={from.y}
                x2={to.x}
                y2={to.y}
                stroke="rgba(168,85,247,0.4)"
                strokeWidth={1}
              />
            );
          })}
        {scaled.map((p) => {
          const cat = categories[p.token] ?? "other";
          const freq = frequencies[p.token] ?? 1;
          const r = 4 + (freq / maxFreq) * 6;
          const selected = selectedTokenId === p.tokenId;
          return (
            <motion.g
              key={p.tokenId}
              animate={{ x: p.x, y: p.y }}
              transition={{ duration: 1.2, ease: [0.4, 0, 0.2, 1] }}
              style={{ cursor: "pointer" }}
              onClick={() =>
                onSelect(selected ? null : p.tokenId)
              }
            >
              <circle
                cx={0}
                cy={0}
                r={selected ? r + 2 : r}
                fill={CATEGORY_COLOR[cat]}
                opacity={selected ? 1 : 0.85}
                style={{
                  filter: selected
                    ? "drop-shadow(0 0 8px rgba(168,85,247,0.8))"
                    : undefined,
                }}
              />
              <text
                x={r + 4}
                y={4}
                className="fill-[var(--text-secondary)] text-[10px]"
              >
                {p.token}
              </text>
            </motion.g>
          );
        })}
      </svg>
      <p className="absolute bottom-3 left-3 text-xs text-[var(--text-muted)]">
        Hover a star to see neighbors
      </p>
    </div>
  );
}
