import { useEffect, useMemo, useState } from "react";
import { fitStatus, memoryEstimate, paramEstimate } from "./lib/estimates";
import { loadResults, type RunRow } from "./lib/results";

const Panel = ({ title, children, tag }: { title: string; children: React.ReactNode; tag?: "ACTUAL" | "ESTIMATED" }) => (
  <section className="rounded-xl border border-white/10 bg-black/40 p-4 backdrop-blur">
    <div className="mb-3 flex items-center justify-between gap-2">
      <h2 className="text-sm font-semibold tracking-wide text-cyan-200/90 uppercase">{title}</h2>
      {tag && <span className={tag === "ACTUAL" ? "tag-actual rounded px-2 py-0.5 text-[10px]" : "tag-est rounded px-2 py-0.5 text-[10px]"}>{tag}</span>}
    </div>
    {children}
  </section>
);

export default function App() {
  const [layers, setLayers] = useState(7);
  const [hidden, setHidden] = useState(448);
  const [heads, setHeads] = useState(7);
  const [seq, setSeq] = useState(256);
  const [vocab, setVocab] = useState(6144);
  const [batch, setBatch] = useState(8);
  const [tokens, setTokens] = useState(50_000_000);
  const [gpuMem, setGpuMem] = useState(16);
  const [reversible, setReversible] = useState(false);
  const [method, setMethod] = useState<"euler" | "midpoint">("euler");
  const [results, setResults] = useState<RunRow[]>([]);

  useEffect(() => { loadResults().then(setResults); }, []);

  const params = useMemo(() => paramEstimate(vocab, layers, hidden, seq, true), [vocab, layers, hidden, seq]);
  const mem = useMemo(() => memoryEstimate(params, batch, seq, hidden, layers, reversible), [params, batch, seq, hidden, layers, reversible]);
  const fit = fitStatus(mem.total, gpuMem);

  const baseline = results.find((r) => r.reversible_method === "none");
  const euler = results.find((r) => r.reversible_method === "euler" && r.run_id.includes("euler"));
  const midpoint = results.find((r) => r.reversible_method === "midpoint");
  const maxB = results.find((r) => r.run_id.startsWith("max_batch"));

  const memSaved = baseline && euler ? (baseline.peak_memory_gb - euler.peak_memory_gb) : null;
  const tpsCost = baseline && euler ? (baseline.tokens_per_sec - euler.tokens_per_sec) : null;

  return (
    <div className="lab-grid min-h-screen">
      <header className="border-b border-white/10 bg-black/60 px-6 py-8">
        <p className="text-xs tracking-[0.35em] text-cyan-400/80">ERA V5 · SESSION 13</p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight">Reversibility Training Lab</h1>
        <p className="mt-2 text-white/60">Trade computation for memory.</p>
      </header>
      <main className="mx-auto grid max-w-6xl gap-4 p-6 md:grid-cols-2">
        <Panel title="Model configuration" tag="ESTIMATED">
          <div className="grid gap-2 text-sm">
            <label>Layers <input type="range" min={4} max={12} value={layers} onChange={(e) => setLayers(+e.target.value)} /></label>
            <label>Hidden <input type="range" min={256} max={768} step={32} value={hidden} onChange={(e) => setHidden(+e.target.value)} /></label>
            <label>Heads <input type="number" value={heads} onChange={(e) => setHeads(+e.target.value)} className="w-16 bg-black/50" /></label>
            <label>Context <input type="range" min={128} max={512} step={64} value={seq} onChange={(e) => setSeq(+e.target.value)} /></label>
            <label>Vocab <input type="number" value={vocab} onChange={(e) => setVocab(+e.target.value)} className="w-20 bg-black/50" /></label>
            <p>~{Math.round(params / 1e6)}M params (estimate)</p>
          </div>
        </Panel>
        <Panel title="Hardware" tag="ESTIMATED">
          <label>GPU memory (GB) <input type="range" min={8} max={80} value={gpuMem} onChange={(e) => setGpuMem(+e.target.value)} /></label>
          <p className="text-sm text-white/70">Usable ~{(gpuMem * 0.9).toFixed(1)} GB</p>
        </Panel>
        <Panel title="Training" tag="ESTIMATED">
          <label>Batch <input type="number" value={batch} onChange={(e) => setBatch(+e.target.value)} className="w-16 bg-black/50" /></label>
          <label>Tokens <input type="number" value={tokens} onChange={(e) => setTokens(+e.target.value)} className="w-28 bg-black/50" /></label>
          <div className="mt-2 flex flex-wrap gap-2 text-xs">
            {["Baseline", "Euler", "Midpoint", "Max batch"].map((p) => (
              <button key={p} className="rounded border border-white/20 px-2 py-1 hover:bg-white/10" onClick={() => {
                if (p === "Baseline") { setReversible(false); setBatch(8); }
                if (p === "Euler") { setReversible(true); setMethod("euler"); }
                if (p === "Midpoint") { setReversible(true); setMethod("midpoint"); }
                if (p === "Max batch") { setReversible(true); setMethod("euler"); setBatch(64); }
              }}>{p}</button>
            ))}
          </div>
        </Panel>
        <Panel title="Reversibility switch" tag="ESTIMATED">
          <button className={`w-full rounded-lg border py-3 text-lg ${reversible ? "border-emerald-400/60 bg-emerald-950/40" : "border-rose-400/60 bg-rose-950/40"}`}
            onClick={() => setReversible(!reversible)}>
            {reversible ? "REVERSIBLE TRAINING" : "NORMAL TRAINING"}
          </button>
          {reversible && (
            <div className="mt-3 flex gap-2">
              {(["euler", "midpoint"] as const).map((m) => (
                <button key={m} onClick={() => setMethod(m)} className={`flex-1 rounded py-2 text-sm capitalize ${method === m ? "bg-cyan-600/40 border border-cyan-400" : "border border-white/20"}`}>{m}</button>
              ))}
            </div>
          )}
        </Panel>
        <Panel title="Memory anatomy" tag="ESTIMATED">
          <div className="flex h-8 overflow-hidden rounded text-[10px]">
            <div style={{ width: `${(mem.weights / mem.total) * 100}%` }} className="bg-slate-500">W</div>
            <div style={{ width: `${(mem.grads / mem.total) * 100}%` }} className="bg-blue-600">G</div>
            <div style={{ width: `${(mem.optim / mem.total) * 100}%` }} className="bg-violet-600">O</div>
            <div style={{ width: `${(mem.activations / mem.total) * 100}%` }} className="bg-amber-500">{reversible ? "A↓" : "A"}</div>
          </div>
          <p className="mt-2 text-xs text-white/60">Activations shrink in reversible mode (modelled).</p>
        </Panel>
        <Panel title="Live trade-off" tag={baseline && euler ? "ACTUAL" : "ESTIMATED"}>
          <table className="w-full text-sm">
            <thead><tr className="text-white/50"><th></th><th>NORMAL</th><th>REVERSIBLE</th></tr></thead>
            <tbody>
              <tr><td>Peak mem (GB)</td><td>{baseline?.peak_memory_gb?.toFixed(3) ?? "—"}</td><td>{euler?.peak_memory_gb?.toFixed(3) ?? "—"}</td></tr>
              <tr><td>Tokens/sec</td><td>{baseline?.tokens_per_sec?.toFixed(0) ?? "—"}</td><td>{euler?.tokens_per_sec?.toFixed(0) ?? "—"}</td></tr>
              <tr><td>Final loss</td><td>{baseline?.final_loss?.toFixed(4) ?? "—"}</td><td>{euler?.final_loss?.toFixed(4) ?? "—"}</td></tr>
              <tr><td>Batch</td><td>{baseline?.batch_size ?? "—"}</td><td>{maxB?.batch_size ?? euler?.batch_size ?? "—"}</td></tr>
            </tbody>
          </table>
          {memSaved !== null && <p className="mt-2 text-xs">Memory saved (CPU trace): {(memSaved * 1e3).toFixed(1)} MB · Throughput Δ: {tpsCost?.toFixed(0)} tok/s</p>}
        </Panel>
        <Panel title="What happens if I…" tag="ESTIMATED">
          <label>Batch size 1–128</label>
          <input type="range" min={1} max={128} value={batch} onChange={(e) => setBatch(+e.target.value)} className="w-full" />
          <p className="mt-2 text-lg">{fit === "fits" ? "✓ FITS" : fit === "close" ? "⚠ CLOSE TO LIMIT" : "✕ OOM (estimated)"}</p>
        </Panel>
        <Panel title="Run experiment" tag="ESTIMATED">
          <p className="text-sm text-white/70">Training runs via CLI / notebooks (no fake live training in browser).</p>
          <ul className="mt-2 list-disc pl-5 text-sm text-cyan-200/90">
            <li><a href="../../notebooks/01_baseline_20m_50m.ipynb">01 baseline notebook</a></li>
            <li><a href="../../notebooks/02_reversible_euler.ipynb">02 Euler notebook</a></li>
            <li><a href="../../notebooks/03_reversible_midpoint.ipynb">03 Midpoint notebook</a></li>
            <li><a href="../../notebooks/04_reversible_max_batch.ipynb">04 max batch notebook</a></li>
          </ul>
          <code className="mt-2 block rounded bg-black/50 p-2 text-xs">python -m src.experiment --mode baseline --tokens 50000000</code>
        </Panel>
        <Panel title="Actual experiment results" tag="ACTUAL">
          {results.length === 0 ? <p className="text-sm text-white/50">No results.json yet — run experiments.</p> : (
            <ul className="space-y-2 text-xs font-mono">{results.map((r) => (
              <li key={r.run_id + r.tokens_trained} className="rounded border border-white/10 p-2">
                <strong>{r.run_id}</strong> · {(r.parameter_count / 1e6).toFixed(2)}M · {r.tokens_trained.toLocaleString()} tok · bs={r.batch_size} · loss={r.final_loss.toFixed(4)} · {r.tokens_per_sec.toFixed(0)} t/s · {r.peak_memory_gb.toFixed(4)} GB peak
              </li>
            ))}</ul>
          )}
        </Panel>
        <Panel title="Loss curves" tag="ACTUAL">
          <div className="flex gap-2 text-xs">{[baseline, euler, midpoint].filter(Boolean).map((r) => (
            <div key={r!.run_id} className="flex-1">
              <p className="text-white/50">{r!.run_id}</p>
              <svg viewBox="0 0 100 40" className="h-20 w-full bg-black/30">
                {(r!.loss_history ?? []).map((p, i, arr) => {
                  if (!arr.length) return null;
                  const xs = arr.map((x) => x.tokens);
                  const ys = arr.map((x) => x.loss);
                  const miny = Math.min(...ys); const maxy = Math.max(...ys);
                  const x = ((p.tokens - xs[0]) / (xs.at(-1)! - xs[0] || 1)) * 100;
                  const y = 38 - ((p.loss - miny) / (maxy - miny || 1)) * 36;
                  return i ? <line key={i} x1={((arr[i-1].tokens-xs[0])/(xs.at(-1)!-xs[0]||1))*100} y1={38-((arr[i-1].loss-miny)/(maxy-miny||1))*36} x2={x} y2={y} stroke="#22d3ee" strokeWidth=".6" /> : null;
                })}
              </svg>
            </div>
          ))}</div>
        </Panel>
        <Panel title="Aha — layer flow" tag="ESTIMATED">
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div>
              <p className="text-rose-300">NORMAL</p>
              {Array.from({ length: 5 }).map((_, i) => <p key={i}>L{i+1} → store activation</p>)}
            </div>
            <div>
              <p className="text-emerald-300">REVERSIBLE</p>
              {Array.from({ length: 5 }).map((_, i) => <p key={i}>L{i+1} → compute → discard</p>)}
              <p className="text-white/50">Backward: reconstruct chain</p>
            </div>
          </div>
        </Panel>
        <Panel title="Experiment journal" tag="ACTUAL">
          <ol className="space-y-3 text-sm">
            {results.map((r, i) => (
              <li key={r.run_id} className="border-l-2 border-cyan-500/40 pl-3">
                <p className="font-semibold">RUN {String(i+1).padStart(2,"0")} — {r.run_id}</p>
                <p className="text-white/60">{r.reversible_method} · bs={r.batch_size} · {r.status}</p>
                <p>loss {r.final_loss.toFixed(4)} · {r.tokens_per_sec.toFixed(0)} tok/s</p>
              </li>
            ))}
          </ol>
        </Panel>
      </main>
    </div>
  );
}
