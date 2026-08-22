import { useState } from "react";
import { motion } from "framer-motion";
import { rotate2D } from "../../lib/math";
import { useApp } from "../../context/AppContext";

export function PositionStory() {
  const [method, setMethod] = useState(0);
  const methods = [
    { name: "No position", problem: "DOG BIT MAN = MAN BIT DOG to pure attention", sacrifice: "Order is invisible" },
    { name: "Learned absolute", problem: "Need position signal", sacrifice: "Cannot exceed max trained length" },
    { name: "Sinusoidal", problem: "Fixed encoding without params", sacrifice: "Weak far extrapolation" },
    { name: "RoPE", problem: "Relative distance in QᵀK", sacrifice: "Needs PI/YaRN for long context" },
    { name: "ALiBi", problem: "Train short, test long", sacrifice: "Different bias than RoPE" },
    { name: "DroPE", problem: "Is explicit position necessary?", sacrifice: "Experimental, not universal" },
  ];

  return (
    <div className="panel p-6">
      <h3 className="text-lg font-bold">Position Must Become a Story</h3>
      <div className="mt-4 flex flex-wrap gap-2">
        {methods.map((m, i) => (
          <button
            key={m.name}
            type="button"
            onClick={() => setMethod(i)}
            className={`focus-ring rounded-lg px-3 py-1.5 text-xs ${method === i ? "bg-violet/20 text-violet" : "bg-white/5 text-muted"}`}
          >
            {m.name}
          </button>
        ))}
      </div>
      <motion.div key={method} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-6">
        {method === 0 && (
          <div className="flex flex-col gap-4 sm:flex-row">
            <p className="token-node">DOG BIT MAN</p>
            <p className="token-node opacity-60">MAN BIT DOG</p>
          </div>
        )}
        <p className="mt-4 text-sm"><strong className="text-amber">Problem:</strong> {methods[method].problem}</p>
        <p className="mt-2 text-sm"><strong className="text-danger">Sacrifice:</strong> {methods[method].sacrifice}</p>
      </motion.div>
    </div>
  );
}

export function RoPEVisualization() {
  const { mode } = useApp();
  const [posQ, setPosQ] = useState(2);
  const [posK, setPosK] = useState(5);
  const angleQ = posQ * 0.4;
  const angleK = posK * 0.4;
  const [qx, qy] = rotate2D(1, 0, angleQ);
  const [kx, ky] = rotate2D(1, 0, angleK);
  const dot = qx * kx + qy * ky;

  return (
    <div className="panel p-6">
      <h3 className="text-lg font-bold">RoPE — Rotary Position Embedding</h3>
      <p className="mt-1 text-sm text-muted">
        RoPE doesn&apos;t say &quot;this is position 17.&quot; It changes how Q and K interact via rotation.
      </p>

      <div className="mt-6 flex flex-col gap-6 sm:flex-row">
        <svg viewBox="0 0 200 200" className="h-48 w-48 shrink-0" aria-label="RoPE rotation diagram">
          <circle cx="100" cy="100" r="80" fill="none" stroke="rgba(255,255,255,0.1)" />
          <line x1="100" y1="100" x2={100 + qx * 70} y2={100 - qy * 70} stroke="#f5b942" strokeWidth="2" />
          <line x1="100" y1="100" x2={100 + kx * 70} y2={100 - ky * 70} stroke="#4dd4e8" strokeWidth="2" />
          <text x="100" y="20" textAnchor="middle" fill="#8b95a8" fontSize="10">Q (pos {posQ})</text>
          <text x="100" y="190" textAnchor="middle" fill="#8b95a8" fontSize="10">K (pos {posK})</text>
        </svg>

        <div className="flex-1">
          <label className="block text-sm">
            Q position: {posQ}
            <input type="range" min={0} max={10} value={posQ} onChange={(e) => setPosQ(Number(e.target.value))} className="focus-ring w-full accent-amber" />
          </label>
          <label className="mt-3 block text-sm">
            K position: {posK}
            <input type="range" min={0} max={10} value={posK} onChange={(e) => setPosK(Number(e.target.value))} className="focus-ring w-full accent-cyan" />
          </label>
          <p className="mt-4 font-mono text-sm">
            QᵀK ∝ cos(θ_q − θ_k) ≈ <span className="text-cyan">{dot.toFixed(3)}</span>
          </p>
          <p className="mt-2 text-xs text-muted">
            Relative position {posK - posQ} encoded in the angle difference.
          </p>
          {mode === "expert" && (
            <p className="mt-2 font-mono text-[10px] text-muted">
              RoPE(x, m) = R_m · x where R_m is block-diagonal rotation by m·θ_i
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export function ContextWars() {
  const chain = [
    { name: "Dense Attention", limit: "Too expensive at long n." },
    { name: "Sparse Attention", limit: "Important token may be outside pattern." },
    { name: "Sliding Window", limit: "Local context is cheap but myopic." },
    { name: "Global Attention", limit: "Escape hatches needed — Longformer, BigBird." },
    { name: "Top-k", limit: "Which k tokens? Selection overhead." },
    { name: "NSA", limit: "Hardware-aligned sparsity — still choosing connections." },
  ];

  return (
    <div className="panel p-6">
      <h3 className="text-lg font-bold">Context Wars</h3>
      <p className="mt-1 text-sm text-muted">Every technique enters because something broke.</p>
      <ol className="mt-6 space-y-4">
        {chain.map((item, i) => (
          <li key={item.name} className="flex gap-4">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-violet/20 text-xs font-bold text-violet">
              {i + 1}
            </span>
            <div>
              <p className="font-semibold">{item.name}</p>
              <p className="text-sm text-muted">↓ &quot;{item.limit}&quot;</p>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
