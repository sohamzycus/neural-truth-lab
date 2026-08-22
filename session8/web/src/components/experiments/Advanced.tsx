import { useState } from "react";
import { motion } from "framer-motion";

export function LinearAttentionStory() {
  return (
    <div className="panel p-6">
      <h3 className="text-lg font-bold">Linear Attention — Not Magic</h3>
      <p className="mt-2 text-sm text-muted">
        Can we avoid explicitly constructing the entire n×n attention matrix?
      </p>
      <div className="mt-4 font-mono text-sm">
        <p>softmax(QKᵀ)V → kernel trick → (Q&apos;(K&apos;ᵀV))</p>
        <p className="mt-2 text-cyan">O(n²) → O(n) with fixed recurrent state</p>
      </div>
      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <div className="rounded-lg bg-ok/10 p-3 text-sm">
          <strong className="text-ok">Attractive:</strong> linear time, constant memory state
        </div>
        <div className="rounded-lg bg-danger/10 p-3 text-sm">
          <strong className="text-danger">Lost:</strong> exact softmax retrieval, unrestricted memory
        </div>
      </div>
    </div>
  );
}

export function DeltaNetMemory() {
  const [memory, setMemory] = useState<Record<string, string>>({ red: "apple", blue: "sky", green: "grass" });
  const [query, setQuery] = useState("red");
  const [gate, setGate] = useState(0.8);

  const overwrite = () => setMemory((m) => ({ ...m, red: "car" }));

  return (
    <div className="panel p-6">
      <h3 className="text-lg font-bold">DeltaNet Memory Experiment</h3>
      <p className="mt-1 text-xs text-amber">Conceptual experiment — not the actual neural implementation</p>

      <div className="mt-4 grid gap-2 font-mono text-sm sm:grid-cols-3">
        {Object.entries(memory).map(([k, v]) => (
          <div key={k} className="rounded bg-white/5 p-2">
            {k} → {v}
          </div>
        ))}
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <select value={query} onChange={(e) => setQuery(e.target.value)} className="focus-ring rounded-lg border border-white/10 bg-surface px-3 py-2 text-sm">
          {Object.keys(memory).map((k) => <option key={k} value={k}>{k}</option>)}
        </select>
        <button type="button" onClick={overwrite} className="focus-ring rounded-lg bg-white/5 px-3 py-2 text-sm">
          Overwrite: red → car (delta update)
        </button>
      </div>

      <motion.p key={memory[query]} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-4 text-lg">
        Query: {query} → <span className="text-cyan">{memory[query] ?? "?"}</span>
      </motion.p>

      <label className="mt-4 block text-sm">
        Forgetting gate: {gate.toFixed(2)}
        <input type="range" min={0} max={1} step={0.05} value={gate} onChange={(e) => setGate(Number(e.target.value))} className="focus-ring w-full" />
      </label>
      <p className="mt-2 text-xs text-muted">
        Gated DeltaNet: gate controls how much old memory is retained vs overwritten.
      </p>
    </div>
  );
}

export function MLACompression() {
  const [compressed, setCompressed] = useState(false);

  return (
    <div className="panel p-6">
      <h3 className="text-lg font-bold">MLA — Cache Compression Story</h3>
      <p className="mt-1 text-sm text-muted">
        GQA reduced KV heads. MLA compresses the KV representation itself (DeepSeek-V2/V3).
      </p>
      <button
        type="button"
        onClick={() => setCompressed(!compressed)}
        className="focus-ring mt-4 rounded-lg bg-violet/20 px-4 py-2 text-sm text-violet"
      >
        {compressed ? "Show full KV" : "Compress to latent"}
      </button>
      <div className="mt-6 flex items-end justify-center gap-4">
        {!compressed ? (
          <div className="flex gap-1">
            {Array.from({ length: 24 }, (_, i) => (
              <div key={i} className="h-24 w-3 rounded bg-cyan/40" />
            ))}
          </div>
        ) : (
          <motion.div
            initial={{ scale: 0.5 }}
            animate={{ scale: 1 }}
            className="flex h-16 w-16 items-center justify-center rounded-full bg-violet/30 ring-2 ring-violet text-xs font-bold"
          >
            LATENT
          </motion.div>
        )}
      </div>
      <p className="mt-4 text-sm text-muted">
        + Compression buys memory · − Reconstruction complexity
      </p>
    </div>
  );
}

export function FlashAttentionIO() {
  return (
    <div className="panel p-6">
      <h3 className="text-lg font-bold">FlashAttention — Algorithm vs Hardware</h3>
      <p className="mt-2 text-sm text-muted">
        FlashAttention does NOT make attention O(n). Same math, better memory movement.
      </p>
      <div className="mt-6 flex flex-col items-center gap-4">
        <div className="w-full max-w-xs rounded-lg border border-amber/30 bg-amber/10 p-4 text-center text-sm">
          HBM (slow, large)
        </div>
        <div className="flex gap-4 text-2xl" aria-hidden>↕ ↕ ↕</div>
        <div className="w-full max-w-xs rounded-lg border border-cyan/30 bg-cyan/10 p-4 text-center text-sm">
          SRAM / shared memory (fast, small)
          <p className="mt-2 text-xs text-muted">Tiled softmax blocks computed here</p>
        </div>
      </div>
      <p className="mt-4 font-mono text-xs text-muted">
        Complexity: still O(n²) · IO: dramatically reduced HBM round-trips
      </p>
    </div>
  );
}

export function AttentionSinks() {
  const [sinks, setSinks] = useState(false);
  const tokens = Array.from({ length: 12 }, (_, i) => `t${i}`);

  return (
    <div className="panel p-6">
      <h3 className="text-lg font-bold">Attention Sinks / StreamingLLM</h3>
      <p className="mt-1 text-sm text-muted">
        Sliding window alone degrades. Keep first few sink tokens for stability.
      </p>
      <button
        type="button"
        onClick={() => setSinks(!sinks)}
        className={`focus-ring mt-4 rounded-lg px-4 py-2 text-sm ${sinks ? "bg-cyan/20 text-cyan" : "bg-white/5"}`}
      >
        {sinks ? "Sinks ON" : "Sinks OFF"}
      </button>
      <div className="mt-4 flex flex-wrap gap-1">
        {tokens.map((t, i) => {
          const isSink = sinks && i < 2;
          const inWindow = i >= tokens.length - 6;
          const visible = isSink || inWindow;
          return (
            <span
              key={t}
              className={`rounded px-2 py-1 text-xs ${visible ? (isSink ? "bg-amber/30 text-amber" : "bg-cyan/20") : "bg-white/5 opacity-30 line-through"}`}
            >
              {t}
            </span>
          );
        })}
      </div>
      <p className="mt-3 text-xs text-muted">
        Sink tokens become attention anchors even when semantically unimportant.
      </p>
    </div>
  );
}

export function ContextExtension() {
  const steps = [
    { name: "Naïve extrapolation", result: "Breaks beyond train length" },
    { name: "Position Interpolation", result: "Scale indices into trained range" },
    { name: "NTK-aware scaling", result: "Community technique — frequency adjustment", badge: "COMMUNITY ORIGIN" },
    { name: "YaRN", result: "Yet another RoPE extensioN — frequency mixing + temperature" },
  ];

  return (
    <div className="panel p-6">
      <h3 className="text-lg font-bold">Context Extension: 4K → 32K?</h3>
      <p className="mt-1 text-sm text-muted">Trained context = 4K. Can I use this model at 32K?</p>
      <ol className="mt-6 space-y-3">
        {steps.map((s) => (
          <li key={s.name} className="rounded-lg bg-white/5 p-3">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-semibold">{s.name}</span>
              {s.badge && (
                <span className="rounded bg-amber/20 px-2 py-0.5 text-[10px] text-amber">{s.badge}</span>
              )}
            </div>
            <p className="mt-1 text-sm text-muted">→ {s.result}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}
