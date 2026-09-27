import { useEffect, useMemo, useState } from "react";
import { useArtifacts, type RunRow } from "../../hooks/useArtifacts";
import { EstimatedBadge, MeasuredBadge } from "./Badges";
import { CopyBtn } from "./CopyBtn";
import { TerminalBlock } from "./TerminalBlock";
import { fitStatus, memoryEstimate, paramEstimate } from "../../lib/estimates";

const fmt = (n: number, d = 2) => n.toLocaleString(undefined, { maximumFractionDigits: d });

function Section({ id, title, children }: { id?: string; title: string; children: React.ReactNode }) {
  return (
    <section id={id} className="scroll-mt-20 border-t border-white/10 py-16">
      <h2 className="mb-8 text-2xl font-semibold tracking-tight text-stone-100">{title}</h2>
      {children}
    </section>
  );
}

function LossSvg({ run, cap = 40 }: { run: RunRow | undefined; cap?: number }) {
  if (!run?.loss_history?.length) return null;
  const pts = run.loss_history;
  const xs = pts.map((p) => p.tokens);
  const ys = pts.map((p) => Math.min(p.loss, cap));
  const minX = xs[0], maxX = xs.at(-1)!;
  const minY = 0, maxY = Math.max(...ys, 1);
  const path = pts.map((p, i) => {
    const x = ((p.tokens - minX) / (maxX - minX || 1)) * 100;
    const y = 95 - ((Math.min(p.loss, cap) - minY) / (maxY - minY || 1)) * 90;
    return `${i === 0 ? "M" : "L"}${x},${y}`;
  }).join(" ");
  return (
    <svg viewBox="0 0 100 100" className="h-32 w-full rounded bg-black/40">
      <path d={path} fill="none" stroke="#38bdf8" strokeWidth="1.2" />
    </svg>
  );
}

export function LabPage() {
  const { loading, host, baseline, euler, midpoint, maxBatch } = useArtifacts();
  const [device, setDevice] = useState<"mps" | "cpu">("mps");
  const [method, setMethod] = useState<"normal" | "euler" | "midpoint">("normal");
  const [batch, setBatch] = useState(8);
  const [seq, setSeq] = useState(256);
  const [layers, setLayers] = useState(7);
  const [hidden, setHidden] = useState(448);
  const tokens = 1_000_000;
  const [playRun, setPlayRun] = useState<"baseline" | "euler" | "midpoint">("baseline");
  const [playIdx, setPlayIdx] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [showHostJson, setShowHostJson] = useState(false);

  const reversible = method !== "normal";
  const params = useMemo(() => paramEstimate(6144, layers, hidden, seq, true), [layers, hidden, seq]);
  const memEst = useMemo(() => memoryEstimate(params, batch, seq, hidden, layers, reversible), [params, batch, seq, hidden, layers, reversible]);
  const fit = fitStatus(memEst.total, host?.ram_gb ?? 24);

  const measuredRun = method === "normal" ? baseline : method === "euler" ? euler : midpoint;
  const matchesMeasured = measuredRun && batch === measuredRun.batch_size && seq === measuredRun.sequence_length && tokens === measuredRun.tokens_trained;

  const playData = playRun === "baseline" ? baseline : playRun === "euler" ? euler : midpoint;
  useEffect(() => {
    if (!playing || !playData?.loss_history) return;
    const t = setInterval(() => {
      setPlayIdx((i) => (i + 1 >= playData.loss_history.length ? 0 : i + 1));
    }, 400);
    return () => clearInterval(t);
  }, [playing, playData]);

  if (loading) return <p className="p-12 text-white/60">Loading recorded evidence…</p>;

  return (
    <div className="mx-auto max-w-5xl px-4 pb-24">
      <header className="py-16 text-center">
        <p className="text-xs tracking-[0.4em] text-stone-500">ERA V5 · SESSION 13</p>
        <h1 className="mt-4 text-4xl font-bold md:text-5xl">Can we trade compute for memory?</h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-stone-400">
          I trained the same ~20M parameter language model normally and with reversible blocks. The result was not what I expected.
        </p>
        <div className="mt-10 grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-6 text-left">
            <p className="text-sm text-rose-300">NORMAL</p>
            <p className="mt-2 text-3xl font-mono">{fmt(baseline?.tokens_per_sec ?? 0, 0)} <span className="text-base text-stone-500">tok/s</span></p>
            <p className="text-stone-400">Batch {baseline?.batch_size}</p>
            <p className="font-mono text-xl">{fmt(baseline?.peak_mps_gb ?? 0, 2)} GB MPS</p>
            <MeasuredBadge className="mt-2" />
          </div>
          <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-6 text-left">
            <p className="text-sm text-emerald-300">REVERSIBLE — EULER</p>
            <p className="mt-2 text-3xl font-mono">{fmt(euler?.tokens_per_sec ?? 0, 0)} <span className="text-base text-stone-500">tok/s</span></p>
            <p className="text-stone-400">Batch {euler?.batch_size}</p>
            <p className="font-mono text-xl">{fmt(euler?.peak_mps_gb ?? 0, 2)} GB MPS</p>
            <MeasuredBadge className="mt-2" />
          </div>
        </div>
        <div className="mx-auto mt-10 max-w-xl rounded-lg border border-amber-500/40 bg-amber-950/10 p-6">
          <p className="text-lg font-medium text-amber-100">So… why use reversibility?</p>
          <p className="mt-2 text-3xl font-mono">BATCH CAPACITY <span className="text-amber-400">8 → 64</span></p>
          <p className="mt-3 text-sm text-stone-400">
            The memory win didn&apos;t show up the way I expected at the small batch. The interesting difference appeared when I pushed the reversible model to a much larger batch.
          </p>
          <MeasuredBadge className="mt-3" />
        </div>
      </header>

      <Section id="machine" title="My machine">
        <div className="mx-auto max-w-md">
          <div className="rounded-[2rem] border border-stone-600 bg-stone-900 p-3 shadow-2xl">
            <div className="rounded-xl border border-stone-700 bg-[#0a0f14] p-6 font-mono text-sm">
              <p className="text-center text-xs tracking-widest text-stone-500">ERA V5 TRAINING LAB</p>
              <div className="mt-6 space-y-4">
                <div><p className="text-stone-500">CPU</p><p>{host?.cpu_brand}</p><p className="text-stone-400">{host?.physical_cpus} cores</p></div>
                <div><p className="text-stone-500">MEMORY</p><p>{host?.ram_gb} GB unified</p></div>
                <div><p className="text-stone-500">ACCELERATOR</p><p>Apple MPS</p></div>
                <div><p className="text-stone-500">PYTORCH</p><p>{host?.pytorch}</p></div>
              </div>
            </div>
          </div>
          <p className="mt-4 text-center text-xs text-stone-500">Captured from the machine used for the experiment.</p>
          <div className="mt-4 text-center">
            <button type="button" className="text-sm text-sky-400 underline" onClick={() => setShowHostJson(!showHostJson)}>View raw host profile</button>
          </div>
          {showHostJson && host && (
            <pre className="mt-3 max-h-48 overflow-auto rounded border border-white/10 bg-black/50 p-3 text-xs">{JSON.stringify(host, null, 2)}</pre>
          )}
        </div>
      </Section>
      <Section id="evidence" title="Evidence wall">
        <div className="grid gap-4 md:grid-cols-2">
          {[
            { t: "MY MACHINE", sub: host?.captured_at?.slice(0, 10), body: `${host?.cpu_brand}, ${host?.ram_gb}GB, MPS` },
            { t: "BASELINE RUN", sub: baseline?.timestamp?.slice(0, 10), body: `${fmt(baseline?.tokens_per_sec ?? 0, 0)} tok/s · loss ${fmt(baseline?.final_loss ?? 0, 4)} · ${fmt(baseline?.peak_mps_gb ?? 0, 2)} GB MPS` },
            { t: "EULER RUN", sub: euler?.timestamp?.slice(0, 10), body: `${fmt(euler?.tokens_per_sec ?? 0, 0)} tok/s · recon ${euler?.reconstruction_error}` },
            { t: "MIDPOINT RUN", sub: midpoint?.timestamp?.slice(0, 10), body: `loss ${fmt(midpoint?.final_loss ?? 0, 2)} · unstable spikes in history` },
            { t: "MAX BATCH RUN", sub: maxBatch?.timestamp?.slice(0, 10), body: `batch ${maxBatch?.batch_size} · ${fmt(maxBatch?.peak_mps_gb ?? 0, 2)} GB MPS` },
          ].map((c) => (
            <article key={c.t} className="rounded-lg border border-white/10 bg-white/[0.02] p-4">
              <h3 className="font-medium">{c.t}</h3>
              <p className="text-xs text-stone-500">{c.sub}</p>
              <p className="mt-2 text-sm text-stone-300">{c.body}</p>
              <MeasuredBadge className="mt-3" />
            </article>
          ))}
        </div>
        {baseline && (
          <div className="mt-6">
            <TerminalBlock
              title="Recorded run output — baseline"
              lines={[
                "$ python -m src.experiment --mode baseline --tokens 1000000 --run-label baseline_1M_laptop",
                `run_id: ${baseline.run_id}`,
                `tokens_per_sec: ${baseline.tokens_per_sec}`,
                `final_loss: ${baseline.final_loss}`,
                `peak_mps_gb: ${baseline.peak_mps_gb}`,
                `cpu_time_s: ${baseline.cpu_time_s}`,
              ]}
            />
          </div>
        )}
      </Section>

      <Section id="cockpit" title="Try the experiment yourself">
        <p className="mb-6 text-stone-400">Adjust the instrument. Values only match a recorded run when controls align with that run.</p>
        <div className="grid gap-6 rounded-xl border border-white/10 bg-black/30 p-6 md:grid-cols-2">
          <label className="text-sm">Device
            <select className="mt-1 w-full rounded bg-stone-900 p-2" value={device} onChange={(e) => setDevice(e.target.value as "mps" | "cpu")}>
              <option value="mps">M4 Pro / MPS</option>
              <option value="cpu">CPU</option>
            </select>
          </label>
          <label className="text-sm">Method
            <select className="mt-1 w-full rounded bg-stone-900 p-2" value={method} onChange={(e) => setMethod(e.target.value as typeof method)}>
              <option value="normal">Normal</option>
              <option value="euler">Euler</option>
              <option value="midpoint">Midpoint</option>
            </select>
          </label>
          <label className="text-sm">Batch size {batch}
            <input type="range" min={1} max={128} value={batch} onChange={(e) => setBatch(+e.target.value)} className="w-full" />
          </label>
          <label className="text-sm">Context {seq}
            <input type="range" min={128} max={512} step={64} value={seq} onChange={(e) => setSeq(+e.target.value)} className="w-full" />
          </label>
          <label className="text-sm">Layers {layers}
            <input type="range" min={4} max={12} value={layers} onChange={(e) => setLayers(+e.target.value)} className="w-full" />
          </label>
          <label className="text-sm">Hidden {hidden}
            <input type="range" min={256} max={768} step={32} value={hidden} onChange={(e) => setHidden(+e.target.value)} className="w-full" />
          </label>
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border border-white/10 p-4">
            <p className="text-stone-400">Peak memory (interactive)</p>
            {matchesMeasured && measuredRun ? (
              <>
                <p className="text-2xl font-mono">{fmt(measuredRun.peak_mps_gb, 3)} GB</p>
                <MeasuredBadge />
              </>
            ) : (
              <>
                <p className="text-2xl font-mono">{(memEst.total / 1e9).toFixed(2)} GB</p>
                <EstimatedBadge />
              </>
            )}
          </div>
          <div className="rounded-lg border border-white/10 p-4">
            <p className="text-stone-400">Fit on {host?.ram_gb} GB machine</p>
            <p className="text-xl">{fit === "fits" ? "✓ Fits (estimate)" : fit === "close" ? "⚠ Close (estimate)" : "✕ OOM (estimate)"}</p>
            <EstimatedBadge />
          </div>
        </div>
      </Section>

      <Section id="memory" title="Memory lab">
        <p className="mb-4 text-sm text-stone-400">
          The reversible design reduces the amount of activation state that must be retained. On this particular MPS run, however, the measured driver allocation was <strong>not lower</strong> at batch 8.
        </p>
        <div className="space-y-2 font-mono text-xs">
          {["WEIGHTS", "GRADIENTS", "OPTIMIZER", "ACTIVATIONS", "RUNTIME"].map((k, i) => (
            <div key={k} className="flex items-center gap-2">
              <span className="w-24 text-stone-500">{k}</span>
              <div className="h-3 flex-1 overflow-hidden rounded bg-stone-800">
                <div className="h-full bg-amber-500/70" style={{ width: `${20 + i * 15}%` }} />
              </div>
              <EstimatedBadge />
            </div>
          ))}
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div>
            <p className="text-sm text-stone-500">Normal @ batch 8 (recorded)</p>
            <p className="font-mono text-xl">{fmt(baseline?.peak_mps_gb ?? 0, 3)} GB <MeasuredBadge /></p>
          </div>
          <div>
            <p className="text-sm text-stone-500">Euler @ batch 8 (recorded)</p>
            <p className="font-mono text-xl">{fmt(euler?.peak_mps_gb ?? 0, 3)} GB <MeasuredBadge /></p>
          </div>
        </div>
      </Section>

      <Section id="cpu" title="CPU / compute lab">
        <div className="space-y-4">
          {[
            { label: "BASELINE", s: baseline?.cpu_time_s ?? 0 },
            { label: "EULER", s: euler?.cpu_time_s ?? 0 },
            { label: "MIDPOINT", s: midpoint?.cpu_time_s ?? 0 },
          ].map((r) => (
            <div key={r.label}>
              <div className="flex justify-between text-sm"><span>{r.label}</span><span className="font-mono">{fmt(r.s, 2)} s</span><MeasuredBadge /></div>
              <div className="mt-1 h-2 rounded bg-stone-800"><div className="h-full bg-sky-500" style={{ width: `${Math.min(100, (r.s / 65) * 100)}%` }} /></div>
            </div>
          ))}
        </div>
        <p className="mt-4 text-sm text-stone-400">Euler was much more expensive to run. Reconstruction saves stored activation state by doing more work during backward.</p>
      </Section>
      <Section id="surprise" title="The result surprised me">
        <p className="text-xl text-stone-300">I expected reversibility to mean less memory.</p>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border border-white/10 p-4"><p>BATCH 8 · NORMAL</p><p className="font-mono text-2xl">{fmt(baseline?.peak_mps_gb ?? 0, 2)} GB</p><MeasuredBadge /></div>
          <div className="rounded-lg border border-white/10 p-4"><p>BATCH 8 · EULER</p><p className="font-mono text-2xl">{fmt(euler?.peak_mps_gb ?? 0, 2)} GB</p><MeasuredBadge /></div>
        </div>
        <p className="mt-8 text-lg">So I changed the question.</p>
        <div className="my-6 flex flex-wrap items-center justify-center gap-4 font-mono text-2xl text-amber-300">
          <span>8</span><span>↓</span><span>16</span><span>↓</span><span>32</span><span>↓</span><span>64</span>
        </div>
        <p className="text-sm text-stone-500">Only batch 8 and 64 were measured on this machine. Steps in between are not recorded runs.</p>
        <div className="mt-6 rounded-xl border border-emerald-500/30 bg-emerald-950/10 p-6">
          <p>REVERSIBLE @ batch {maxBatch?.batch_size}</p>
          <p className="font-mono text-3xl">{fmt(maxBatch?.peak_mps_gb ?? 0, 2)} GB · {fmt(maxBatch?.tokens_per_sec ?? 0, 0)} tok/s</p>
          <p className="mt-2 text-stone-300">Batch capacity became the interesting result.</p>
          <MeasuredBadge className="mt-2" />
        </div>
      </Section>

      <Section id="batch" title="Batch explorer">
        <svg viewBox="0 0 400 200" className="w-full rounded-lg bg-black/40">
          <text x="200" y="190" textAnchor="middle" className="fill-stone-500 text-[10px]">Batch size</text>
          <text x="12" y="100" className="fill-stone-500 text-[10px]" transform="rotate(-90 12 100)">MPS peak GB</text>
          {baseline && <circle cx={40 + baseline.batch_size * 4} cy={180 - baseline.peak_mps_gb * 30} r="6" className="fill-rose-400" />}
          {euler && <circle cx={40 + euler.batch_size * 4} cy={180 - euler.peak_mps_gb * 30} r="6" className="fill-emerald-400" />}
          {maxBatch && <circle cx={40 + maxBatch.batch_size * 4} cy={180 - maxBatch.peak_mps_gb * 30} r="8" className="fill-amber-400" />}
          <text x="70" y="30" className="fill-stone-400 text-[10px]">● Measured points only</text>
        </svg>
        <EstimatedBadge className="mt-2" />
        <p className="mt-2 text-xs text-stone-500">No OOM boundary recorded — sweep stopped at batch 64 without failure.</p>
      </Section>

      <Section id="methods" title="Euler vs Midpoint">
        <div className="grid gap-4 md:grid-cols-2">
          <article className="rounded-lg border border-white/10 p-4">
            <h3 className="text-emerald-300">EULER</h3>
            <ul className="mt-2 space-y-1 text-sm font-mono">
              <li>Reconstruction error: {euler?.reconstruction_error}</li>
              <li>Throughput: {fmt(euler?.tokens_per_sec ?? 0, 0)} tok/s</li>
              <li>Final loss: {fmt(euler?.final_loss ?? 0, 4)}</li>
              <li>Training behaviour: Stable</li>
            </ul>
            <LossSvg run={euler} />
            <MeasuredBadge className="mt-2" />
          </article>
          <article className="rounded-lg border border-white/10 p-4">
            <h3 className="text-amber-300">MIDPOINT</h3>
            <ul className="mt-2 space-y-1 text-sm font-mono">
              <li>Reconstruction error: ~{midpoint?.reconstruction_error?.toFixed(2)}</li>
              <li>Throughput: {fmt(midpoint?.tokens_per_sec ?? 0, 0)} tok/s</li>
              <li>Final loss: {fmt(midpoint?.final_loss ?? 0, 4)}</li>
              <li>Training behaviour: Unstable</li>
            </ul>
            <LossSvg run={midpoint} cap={50} />
            <p className="mt-2 text-sm text-stone-400">Midpoint looked promising. In this run, it didn&apos;t hold up.</p>
            <MeasuredBadge className="mt-2" />
          </article>
        </div>
      </Section>

      <Section id="playback" title="Loss playback">
        <div className="flex flex-wrap gap-2">
          {(["baseline", "euler", "midpoint"] as const).map((k) => (
            <button key={k} type="button" className={`rounded px-3 py-1 text-sm capitalize ${playRun === k ? "bg-sky-600" : "border border-white/20"}`} onClick={() => { setPlayRun(k); setPlayIdx(0); }}>{k}</button>
          ))}
          <button type="button" className="rounded bg-stone-700 px-4 py-1 text-sm" onClick={() => setPlaying(!playing)}>{playing ? "Pause" : "Play"}</button>
        </div>
        {playData && playData.loss_history[playIdx] && (
          <div className="mt-4 font-mono text-sm">
            <p>tokens: {playData.loss_history[playIdx].tokens.toLocaleString()}</p>
            <p>loss: {playData.loss_history[playIdx].loss}</p>
            <p>throughput: {fmt(playData.tokens_per_sec, 0)} tok/s (run average)</p>
            <MeasuredBadge />
          </div>
        )}
        {playData && <LossSvg run={{ ...playData, loss_history: playData.loss_history.slice(0, playIdx + 1) }} cap={playRun === "midpoint" ? 50 : 10} />}
      </Section>

      <Section id="anatomy" title="Memory anatomy">
        <div className="grid gap-8 md:grid-cols-2 text-sm">
          <div>
            <p className="text-rose-300">NORMAL</p>
            {[1, 2, 3].map((n) => (
              <p key={n} className="mt-2 border-l-2 border-rose-500/40 pl-3">Layer {n} → activation stored</p>
            ))}
            <p className="mt-4 text-stone-500">BACKWARD → reuse stored activations</p>
          </div>
          <div>
            <p className="text-emerald-300">REVERSIBLE</p>
            {[1, 2, 3].map((n) => (
              <p key={n} className="mt-2 border-l-2 border-emerald-500/40 pl-3">Layer {n} → compute → discard internal state</p>
            ))}
            <p className="mt-4 text-stone-500">BACKWARD → reconstruct → recompute → continue</p>
          </div>
        </div>
        <EstimatedBadge className="mt-4" />
      </Section>
      <Section id="diary" title="Lab notebook">
        <article className="mb-8 border-l-2 border-stone-600 pl-4">
          <h3 className="text-lg">Run 01 — I needed a baseline</h3>
          <p className="text-stone-400">I started with the normal model first. The goal was simple: get a stable run and understand what this laptop could handle.</p>
          <p className="mt-2 font-mono text-sm">{baseline?.run_id}: {fmt(baseline?.tokens_per_sec ?? 0, 0)} tok/s, loss {fmt(baseline?.final_loss ?? 0, 4)}</p>
        </article>
        <article className="mb-8 border-l-2 border-stone-600 pl-4">
          <h3 className="text-lg">Run 02 — Euler</h3>
          <p className="text-stone-400">I kept the batch size unchanged and switched to reversible Euler.</p>
          <p className="mt-2 font-mono text-sm">CPU {fmt(euler?.cpu_time_s ?? 0, 1)}s · MPS {fmt(euler?.peak_mps_gb ?? 0, 2)} GB (higher than baseline at bs=8)</p>
        </article>
        <article className="mb-8 border-l-2 border-stone-600 pl-4">
          <h3 className="text-lg">Run 03 — Midpoint</h3>
          <p className="text-stone-400">This was the interesting one. The loss started behaving badly.</p>
          <LossSvg run={midpoint} cap={50} />
        </article>
        <article className="border-l-2 border-amber-600 pl-4">
          <h3 className="text-lg">Run 04 — Push the batch</h3>
          <p className="text-stone-400">I didn&apos;t want to stop at the small batch because that wasn&apos;t answering the real question. I pushed the reversible model.</p>
          <p className="mt-2 font-mono text-amber-200">8 → 64 · {fmt(maxBatch?.peak_mps_gb ?? 0, 2)} GB MPS peak</p>
        </article>
      </Section>

      <Section id="learned" title="What I learned">
        <ul className="space-y-3 text-stone-300">
          <li>I expected lower memory at batch 8. I didn&apos;t get it.</li>
          <li>Euler was stable enough to continue experimenting with.</li>
          <li>Midpoint became unstable in this setup.</li>
          <li>The biggest practical difference was batch capacity.</li>
          <li>Reversibility was not free. The throughput hit was large.</li>
          <li>That trade-off is the actual point of the experiment.</li>
        </ul>
      </Section>

      <Section id="reproduce" title="Reproduce it">
        {[
          "git clone https://github.com/sohamzycus/neural-truth-lab.git",
          "cd neural-truth-lab/session13",
          "pip install -r requirements.txt",
          "pytest tests/ -q",
          "python -m src.experiment --mode baseline --tokens 1000000 --run-label baseline_1M_laptop",
          "python -m src.experiment --mode euler --tokens 1000000 --run-label euler_1M_laptop",
          "python -m src.experiment --mode midpoint --tokens 1000000 --run-label midpoint_1M_laptop",
          "python -m src.experiment --mode max_batch --tokens 1000000",
          "cd web/interactive-lab && npm install && npm run dev",
        ].map((cmd, i) => (
          <div key={cmd} className="mb-2 flex flex-wrap items-center gap-2 font-mono text-xs">
            <span className="text-stone-500">{i + 1}.</span>
            <code className="flex-1 rounded bg-black/50 px-2 py-1">{cmd}</code>
            <CopyBtn text={cmd} />
          </div>
        ))}
        <div className="mt-8 grid gap-3 md:grid-cols-2">
          {[
            ["01_baseline_20m_50m.ipynb", "NORMAL baseline"],
            ["02_reversible_euler.ipynb", "Euler reversible"],
            ["03_reversible_midpoint.ipynb", "Midpoint reversible"],
            ["04_reversible_max_batch.ipynb", "Max batch sweep"],
          ].map(([n, p]) => (
            <div key={n} className="rounded border border-white/10 p-3">
              <p className="font-medium">{n}</p>
              <p className="text-sm text-stone-500">{p}</p>
              <p className="mt-2 text-xs text-sky-400">notebooks/{n}</p>
            </div>
          ))}
        </div>
      </Section>
    </div>
  );
}
