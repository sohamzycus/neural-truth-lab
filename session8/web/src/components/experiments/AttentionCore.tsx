import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { softmax } from "../../lib/math";
import { useApp } from "../../context/AppContext";

const SENTENCES = {
  river: { tokens: ["The", "river", "bank", "was", "muddy"], focus: 2 },
  finance: { tokens: ["The", "investment", "bank", "approved", "credit"], focus: 2 },
};

const KEYS = ["city", "animal", "food", "tiger", "weather"];
const VALUES: Record<string, string> = {
  city: "urban infrastructure",
  animal: "living creature",
  food: "edible substance",
  tiger: "large feline predator",
  weather: "atmospheric conditions",
};

const QUERY_VECS: Record<string, number[]> = {
  "Where is the animal?": [0.1, 0.9, 0.1, 0.8, 0.05],
  "What is the weather?": [0.05, 0.1, 0.05, 0.1, 0.95],
  "What food is nearby?": [0.1, 0.2, 0.9, 0.15, 0.1],
};

export function OpeningSequence() {
  const [step, setStep] = useState(0);
  const tokens = ["THE", "CAT", "SAT", "ON", "THE", "MAT"];
  const steps = [
    "question",
    "tokens",
    "query",
    "pipeline",
    "scale",
    "decode",
  ];

  return (
    <section id="chapter-0" className="scroll-mt-20 min-h-[85vh] flex flex-col justify-center">
      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-3xl text-4xl font-bold leading-tight tracking-tight sm:text-5xl lg:text-6xl"
      >
        Every token wants to know one thing:
        <span className="mt-2 block text-cyan">Who should I listen to?</span>
      </motion.h1>

      <div className="mt-10 panel panel-glow p-6 sm:p-8">
        {step === 0 && (
          <p className="text-lg text-muted">
            Not a taxonomy. Not a paper summary. A causal story of bottlenecks and compromises.
          </p>
        )}

        {step >= 1 && (
          <div className="flex flex-wrap justify-center gap-2">
            {tokens.map((t, i) => (
              <motion.span
                key={i}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: i * 0.08 }}
                className={`token-node ${step >= 2 && i === 1 ? "ring-2 ring-amber ring-offset-2 ring-offset-surface" : ""}`}
              >
                {t}
              </motion.span>
            ))}
          </div>
        )}

        {step >= 3 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-8 flex flex-col items-center gap-1 font-mono text-sm text-cyan"
          >
            <span>Q × Kᵀ → scores → /√dₖ → mask → softmax → weighted V</span>
          </motion.div>
        )}

        {step >= 4 && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-6 text-center text-xl font-semibold text-amber"
          >
            Beautiful. But now give me 100,000 tokens.
          </motion.p>
        )}

        {step >= 5 && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 text-center text-muted"
          >
            And generate one token at a time. → KV cache. Memory fills. The story continues.
          </motion.p>
        )}

        <div className="mt-8 flex justify-center gap-2">
          {steps.map((_, i) => (
            <button
              key={i}
              type="button"
              onClick={() => setStep(i)}
              className={`focus-ring h-2 w-8 rounded-full ${i <= step ? "bg-cyan" : "bg-white/15"}`}
              aria-label={`Opening step ${i + 1}`}
            />
          ))}
          {step < steps.length - 1 && (
            <button
              type="button"
              onClick={() => setStep((s) => s + 1)}
              className="focus-ring ml-4 rounded-lg bg-cyan/20 px-4 py-2 text-sm font-medium text-cyan"
            >
              Next →
            </button>
          )}
        </div>
      </div>

      <BankDisambiguation />
    </section>
  );
}

function BankDisambiguation() {
  const [sense, setSense] = useState<"river" | "finance">("river");
  const s = SENTENCES[sense];

  return (
    <div className="mt-12 panel p-6">
      <h3 className="text-lg font-bold">The token didn&apos;t change. Context did.</h3>
      <p className="mt-1 text-sm text-muted">
        Select &quot;bank&quot; — watch attention shift between river bank and investment bank.
      </p>
      <div className="mt-4 flex gap-2">
        {(["river", "finance"] as const).map((k) => (
          <button
            key={k}
            type="button"
            onClick={() => setSense(k)}
            className={`focus-ring rounded-lg px-3 py-1.5 text-sm ${sense === k ? "bg-violet/20 text-violet" : "bg-white/5 text-muted"}`}
          >
            {k === "river" ? "river bank" : "investment bank"}
          </button>
        ))}
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {s.tokens.map((t, i) => (
          <span
            key={i}
            className={`token-node ${i === s.focus ? "ring-2 ring-violet" : ""} ${i === s.focus - 1 || i === s.focus + 1 ? "opacity-100" : "opacity-60"}`}
          >
            {t}
          </span>
        ))}
      </div>
      <p className="mt-3 text-xs text-muted">
        Neighbors &quot;{s.tokens[s.focus - 1]}&quot; and &quot;{s.tokens[s.focus + 1]}&quot; reshape the contextual representation of &quot;bank&quot;.
      </p>
    </div>
  );
}

export function QKVExperiment() {
  const { mode } = useApp();
  const [query, setQuery] = useState("Where is the animal?");
  const [showMath, setShowMath] = useState(false);

  const weights = useMemo(() => {
    const vec = QUERY_VECS[query] ?? QUERY_VECS["Where is the animal?"];
    return softmax(vec);
  }, [query]);

  return (
    <div className="panel p-6">
      <h3 className="text-lg font-bold">Q / K / V Experiment</h3>
      <p className="mt-1 text-sm text-muted">Change the query. Watch attention weights move. Then reveal the math.</p>

      <label className="mt-4 block text-sm">
        <span className="text-muted">Query:</span>
        <select
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="focus-ring mt-1 w-full rounded-lg border border-white/10 bg-surface px-3 py-2"
          aria-label="Select query"
        >
          {Object.keys(QUERY_VECS).map((q) => (
            <option key={q} value={q}>{q}</option>
          ))}
        </select>
      </label>

      <div className="mt-6 space-y-3">
        {KEYS.map((k, i) => (
          <div key={k} className="flex items-center gap-3">
            <span className="w-16 font-mono text-xs text-violet">K:{k}</span>
            <div className="h-3 flex-1 overflow-hidden rounded-full bg-white/5">
              <motion.div
                className="h-full rounded-full bg-gradient-to-r from-cyan to-violet"
                animate={{ width: `${weights[i] * 100}%` }}
                transition={{ type: "spring", stiffness: 120 }}
              />
            </div>
            <span className="w-12 text-right font-mono text-xs">{(weights[i] * 100).toFixed(0)}%</span>
            <span className="hidden text-xs text-muted sm:inline">V: {VALUES[k]}</span>
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={() => setShowMath(!showMath)}
        className="focus-ring mt-6 text-sm text-cyan hover:underline"
      >
        {showMath ? "Hide" : "Reveal"} equation →
      </button>

      {showMath && (
        <div className="mt-4 space-y-2 font-mono text-sm">
          <p>Attention(Q,K,V) = softmax(QKᵀ / √dₖ) V</p>
          {mode === "expert" && (
            <p className="text-xs text-muted">
              Shapes: Q ∈ ℝ^(n×d), K ∈ ℝ^(n×d), V ∈ ℝ^(n×d_v). Per-head dₖ = d / h.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
