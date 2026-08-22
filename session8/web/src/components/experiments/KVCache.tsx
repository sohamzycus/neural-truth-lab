import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { kvCacheBytes } from "../../lib/math";
import { useApp } from "../../context/AppContext";

type KVMode = "MHA" | "GQA" | "MQA";

const PROMPT = "The procurement agent reviewed the supplier";
const GENERATED = ["and", "found", "compliance", "gaps"];

export function KVCacheSimulator() {
  const { mode } = useApp();
  const [kvMode, setKvMode] = useState<KVMode>("MHA");
  const [tokenIdx, setTokenIdx] = useState(0);
  const qHeads = 8;
  const kvHeads = kvMode === "MHA" ? 8 : kvMode === "GQA" ? 2 : 1;
  const layers = 4;
  const seqLen = PROMPT.split(" ").length + tokenIdx;
  const cacheBytes = kvCacheBytes(seqLen, layers, kvHeads, 128);
  const mhaBytes = kvCacheBytes(seqLen, layers, 8, 128);

  return (
    <div className="panel p-6">
      <h3 className="text-lg font-bold">KV Cache — Decoding Simulator</h3>
      <p className="mt-1 text-sm text-muted">
        Each new token adds K and V to every layer. Toggle MHA / GQA / MQA — watch cache shrink.
      </p>

      <p className="mt-4 rounded-lg bg-white/5 p-3 font-mono text-sm">
        {PROMPT}{" "}
        <AnimatePresence>
          {GENERATED.slice(0, tokenIdx).map((t, i) => (
            <motion.span key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-cyan">
              {t}{" "}
            </motion.span>
          ))}
        </AnimatePresence>
        <span className="animate-pulse text-amber">▌</span>
      </p>

      <div className="mt-4 flex flex-wrap gap-2">
        {(["MHA", "GQA", "MQA"] as const).map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => setKvMode(m)}
            className={`focus-ring rounded-lg px-3 py-1.5 text-sm font-medium ${
              kvMode === m ? "bg-violet/20 text-violet" : "bg-white/5 text-muted"
            }`}
            aria-pressed={kvMode === m}
          >
            {m}
          </button>
        ))}
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <div>
          <p className="text-xs uppercase tracking-wide text-muted">KV Cache</p>
          <div className="mt-2 space-y-1">
            {Array.from({ length: layers }, (_, l) => (
              <div key={l} className="flex items-center gap-2">
                <span className="w-16 font-mono text-xs text-muted">Layer {l + 1}</span>
                <div className="flex flex-1 gap-0.5">
                  {Array.from({ length: kvHeads }, (_, h) => (
                    <motion.div
                      key={h}
                      layout
                      className="h-6 flex-1 rounded bg-cyan/30 ring-1 ring-cyan/40"
                      title={`KV head ${h + 1}`}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
          <p className="mt-2 text-xs text-muted">
            {qHeads} Q heads · {kvHeads} KV heads
            {kvMode === "GQA" && " (groups of 4 share K/V)"}
          </p>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-muted">Relative memory</p>
          <div className="mt-2 h-8 overflow-hidden rounded-full bg-white/5">
            <motion.div
              className="h-full bg-gradient-to-r from-violet to-cyan"
              animate={{ width: `${(cacheBytes / mhaBytes) * 100}%` }}
            />
          </div>
          <p className="mt-2 font-mono text-sm">
            {(cacheBytes / 1024).toFixed(0)} KB
            <span className="text-muted"> ({((cacheBytes / mhaBytes) * 100).toFixed(0)}% of MHA)</span>
          </p>
          {mode === "expert" && (
            <p className="mt-1 font-mono text-[10px] text-muted">
              KV bytes ≈ 2 × seq × layers × kv_heads × d × sizeof(fp16)
            </p>
          )}
        </div>
      </div>

      <div className="mt-4 flex gap-2">
        <button
          type="button"
          onClick={() => setTokenIdx((i) => Math.min(GENERATED.length, i + 1))}
          disabled={tokenIdx >= GENERATED.length}
          className="focus-ring rounded-lg bg-cyan/20 px-4 py-2 text-sm text-cyan disabled:opacity-40"
        >
          Generate token
        </button>
        <button
          type="button"
          onClick={() => setTokenIdx(0)}
          className="focus-ring rounded-lg bg-white/5 px-4 py-2 text-sm text-muted"
        >
          Reset
        </button>
      </div>

      <dl className="mt-4 grid gap-2 text-xs sm:grid-cols-3">
        <div className="rounded bg-white/5 p-2">
          <dt className="font-semibold text-ok">MHA</dt>
          <dd className="text-muted">Max K/V diversity, max cache</dd>
        </div>
        <div className="rounded bg-white/5 p-2">
          <dt className="font-semibold text-cyan">GQA</dt>
          <dd className="text-muted">Middle ground — not always better, but often balanced</dd>
        </div>
        <div className="rounded bg-white/5 p-2">
          <dt className="font-semibold text-amber">MQA</dt>
          <dd className="text-muted">Min cache, aggressive sharing</dd>
        </div>
      </dl>
    </div>
  );
}

export function MHAComparison() {
  const [kvHeads, setKvHeads] = useState(8);
  const qHeads = 8;
  const label = kvHeads === 8 ? "MHA" : kvHeads === 1 ? "MQA" : "GQA";

  return (
    <div className="panel p-6">
      <h3 className="text-lg font-bold">MHA / GQA / MQA Visual Experiment</h3>
      <label className="mt-4 block text-sm">
        KV heads: <strong>{kvHeads}</strong> → <span className="text-violet">{label}</span>
        <input
          type="range"
          min={1}
          max={8}
          step={1}
          value={kvHeads}
          onChange={(e) => setKvHeads(Number(e.target.value))}
          className="focus-ring mt-2 w-full accent-violet"
          aria-label="KV heads slider"
        />
      </label>
      <div className="mt-4 flex gap-4">
        <div>
          <p className="mb-2 text-xs text-muted">Q heads ({qHeads})</p>
          <div className="flex flex-col gap-1">
            {Array.from({ length: qHeads }, (_, i) => (
              <div key={i} className="h-4 w-24 rounded bg-amber/40" />
            ))}
          </div>
        </div>
        <div>
          <p className="mb-2 text-xs text-muted">KV heads ({kvHeads})</p>
          <div className="flex flex-col gap-1">
            {Array.from({ length: kvHeads }, (_, i) => (
              <div key={i} className="h-4 w-24 rounded bg-cyan/50" />
            ))}
          </div>
        </div>
      </div>
      <p className="mt-4 text-sm text-muted">
        {qHeads / kvHeads} query heads share each K/V head. Cache ∝ kvHeads, not qHeads.
      </p>
    </div>
  );
}
