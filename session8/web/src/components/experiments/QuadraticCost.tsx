import { useRef, useEffect, useState } from "react";
import { SEQ_PRESETS, pairCount, formatPairs } from "../../lib/math";

export function QuadraticCost() {
  const [idx, setIdx] = useState(2);
  const n = SEQ_PRESETS[idx];
  const pairs = pairCount(n);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const size = 280;
    canvas.width = size;
    canvas.height = size;
    ctx.clearRect(0, 0, size, size);

    const gridN = Math.min(64, Math.ceil(Math.sqrt(n / 16)));
    const cell = size / gridN;

    for (let i = 0; i < gridN; i++) {
      for (let j = 0; j < gridN; j++) {
        const intensity = 0.15 + 0.85 * ((i + j) / (gridN * 2));
        ctx.fillStyle = `rgba(77, 212, 232, ${intensity * Math.min(1, n / 512)})`;
        ctx.fillRect(j * cell, i * cell, cell - 0.5, cell - 0.5);
      }
    }

    ctx.strokeStyle = "rgba(167, 139, 250, 0.5)";
    ctx.lineWidth = 2;
    ctx.strokeRect(0, 0, size, size);
  }, [n]);

  const examples = [
    { n: 128, pairs: "16K" },
    { n: 1024, pairs: "~1M" },
    { n: 8192, pairs: "~67M" },
    { n: 32768, pairs: "~1.07B" },
    { n: 1000000, pairs: "1T" },
  ];

  return (
    <div className="panel p-6">
      <h3 className="text-lg font-bold">The O(n²) Moment</h3>
      <p className="mt-1 text-sm text-muted">
        Every token pair can interact. This is why &quot;just make context longer&quot; was never free.
      </p>

      <label className="mt-6 block">
        <span className="text-sm text-muted">Sequence length: <strong className="text-cyan">{formatPairs(n)}</strong> tokens</span>
        <input
          type="range"
          min={0}
          max={SEQ_PRESETS.length - 1}
          value={idx}
          onChange={(e) => setIdx(Number(e.target.value))}
          className="focus-ring mt-2 w-full accent-cyan"
          aria-valuemin={0}
          aria-valuemax={SEQ_PRESETS.length - 1}
          aria-valuenow={idx}
          aria-label="Sequence length slider"
        />
        <div className="mt-1 flex justify-between font-mono text-[10px] text-muted">
          {SEQ_PRESETS.map((s) => (
            <span key={s}>{s >= 1e6 ? "1M" : s >= 1000 ? `${s / 1000}K` : s}</span>
          ))}
        </div>
      </label>

      <div className="mt-6 flex flex-col items-center gap-4 sm:flex-row">
        <canvas ref={canvasRef} className="rounded-lg border border-white/10" aria-hidden />
        <div>
          <p className="text-3xl font-bold text-amber">{formatPairs(pairs)}</p>
          <p className="text-sm text-muted">pairwise attention interactions</p>
          <p className="mt-2 font-mono text-xs text-muted">O(n²) = {n}² = {pairs.toLocaleString()}</p>
        </div>
      </div>

      <ul className="mt-6 grid gap-2 sm:grid-cols-2">
        {examples.map((ex) => (
          <li key={ex.n} className="rounded-lg bg-white/5 px-3 py-2 font-mono text-xs">
            {ex.n.toLocaleString()} → {ex.pairs}
          </li>
        ))}
      </ul>
    </div>
  );
}
