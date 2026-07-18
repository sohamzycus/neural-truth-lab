import { useMemo, useState } from "react";
import type { Matrix } from "../types";

function weightedScore(scores: number[], weights: number[]): number {
  return scores.reduce((sum, s, i) => sum + s * weights[i], 0);
}

export function DecisionMatrix({ matrix }: { matrix: Matrix }) {
  const [weights, setWeights] = useState(matrix.weights);
  const [showSliders, setShowSliders] = useState(false);

  const ranked = useMemo(
    () =>
      matrix.options
        .map((opt) => ({
          opt,
          score: weightedScore(matrix.scores[opt], weights),
        }))
        .sort((a, b) => b.score - a.score),
    [matrix, weights],
  );

  const winnerFlipped = ranked[0].opt !== matrix.decision.split(" ")[0]
    && !matrix.decision.includes(ranked[0].opt);

  const normalize = (idx: number, val: number) => {
    const next = [...weights];
    next[idx] = val;
    const sum = next.reduce((a, b) => a + b, 0) || 1;
    setWeights(next.map((w) => w / sum));
  };

  return (
    <div className="my-6 overflow-x-auto rounded border border-[var(--border)] bg-white">
      <div className="flex items-center justify-between border-b border-[var(--border)] px-4 py-2">
        <div>
          <h4 className="font-semibold">{matrix.id}: {matrix.title}</h4>
          <p className="text-sm text-[var(--muted)]">Report decision: {matrix.decision}</p>
        </div>
        <button
          type="button"
          onClick={() => setShowSliders((s) => !s)}
          className="rounded border border-[var(--border)] px-2 py-1 text-xs hover:bg-[var(--paper)]"
        >
          {showSliders ? "Hide" : "Stress-test"} weights
        </button>
      </div>

      {showSliders && (
        <div className="space-y-2 border-b border-[var(--border)] bg-[var(--paper)] px-4 py-3">
          {matrix.criteria.map((c, i) => (
            <label key={c} className="block text-xs">
              <span className="text-[var(--muted)]">{c} ({(weights[i] * 100).toFixed(0)}%)</span>
              <input
                type="range"
                min={0.05}
                max={0.6}
                step={0.05}
                value={weights[i]}
                onChange={(e) => normalize(i, Number(e.target.value))}
                className="mt-1 w-full accent-[var(--accent-2)]"
              />
            </label>
          ))}
          <button
            type="button"
            onClick={() => setWeights(matrix.weights)}
            className="text-xs text-[var(--accent-2)] underline"
          >
            Reset to report weights
          </button>
          {winnerFlipped && (
            <p className="text-xs font-medium text-[var(--accent)]">
              Winner flips to: {ranked[0].opt}
            </p>
          )}
        </div>
      )}

      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-[var(--border)] bg-[var(--paper)]">
            <th className="px-3 py-2 text-left">Option</th>
            {matrix.criteria.map((c) => (
              <th key={c} className="px-3 py-2 text-right">{c}</th>
            ))}
            <th className="px-3 py-2 text-right font-semibold">Weighted</th>
          </tr>
        </thead>
        <tbody>
          {ranked.map(({ opt, score }, i) => (
            <tr
              key={opt}
              className={`border-b border-[var(--border)] last:border-0 ${
                i === 0 ? "bg-[var(--accent)]/5" : ""
              }`}
            >
              <td className="px-3 py-2 font-medium">{opt}</td>
              {matrix.scores[opt].map((s, j) => (
                <td key={j} className="px-3 py-2 text-right tabular-nums">{s.toFixed(2)}</td>
              ))}
              <td className="px-3 py-2 text-right font-medium tabular-nums">{score.toFixed(3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
