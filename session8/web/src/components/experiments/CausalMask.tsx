import { useState } from "react";
import { motion } from "framer-motion";

const TOKENS = ["I", "love", "machine", "learning"];

export function CausalMaskExperiment() {
  const [causal, setCausal] = useState(true);
  const n = TOKENS.length;

  return (
    <div className="panel p-6">
      <h3 className="text-lg font-bold">Causal Masking Experiment</h3>
      <p className="mt-1 text-sm text-muted">
        Token <em>i</em> cannot see future tokens when causal masking is ON.
      </p>

      <div className="mt-4 flex items-center gap-3">
        <button
          type="button"
          onClick={() => setCausal(true)}
          className={`focus-ring rounded-lg px-3 py-1.5 text-sm ${causal ? "bg-cyan/20 text-cyan" : "bg-white/5"}`}
          aria-pressed={causal}
        >
          Causal ON
        </button>
        <button
          type="button"
          onClick={() => setCausal(false)}
          className={`focus-ring rounded-lg px-3 py-1.5 text-sm ${!causal ? "bg-amber/20 text-amber" : "bg-white/5"}`}
          aria-pressed={!causal}
        >
          Causal OFF
        </button>
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        {TOKENS.map((t, i) => (
          <span key={i} className="token-node">{t}</span>
        ))}
      </div>

      <div
        className="mt-6 inline-grid gap-1"
        style={{ gridTemplateColumns: `repeat(${n}, 3rem)` }}
        role="img"
        aria-label={`Attention mask matrix, causal ${causal ? "on" : "off"}`}
      >
        {Array.from({ length: n * n }, (_, idx) => {
          const row = Math.floor(idx / n);
          const col = idx % n;
          const allowed = !causal || col <= row;
          const isFuture = col > row;
          return (
            <motion.div
              key={idx}
              animate={{
                opacity: allowed ? 1 : 0.15,
                scale: allowed ? 1 : 0.85,
              }}
              className={`flex h-12 w-12 items-center justify-center rounded text-xs font-mono ${
                allowed
                  ? "bg-cyan/25 text-cyan ring-1 ring-cyan/30"
                  : "bg-white/5 text-muted line-through"
              }`}
              title={isFuture && causal ? "Future token — locked" : "Can attend"}
            >
              {allowed ? "✓" : "🔒"}
            </motion.div>
          );
        })}
      </div>

      <p className="mt-4 text-sm text-muted">
        {causal
          ? "Next-token prediction requires causal masking — the model must not peek at the answer."
          : "Bidirectional attention (BERT-style) sees the full sequence — unsuitable for autoregressive generation."}
      </p>
    </div>
  );
}
