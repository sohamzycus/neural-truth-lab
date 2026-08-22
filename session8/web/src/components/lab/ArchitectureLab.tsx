import { useState } from "react";
import { useApp } from "../../context/AppContext";

interface ArchChoices {
  context: string;
  attention: string;
  position: string;
  kv: string;
  kernel: string;
}

const DEFAULT: ArchChoices = {
  context: "8K",
  attention: "Dense",
  position: "RoPE",
  kv: "GQA",
  kernel: "FlashAttention",
};

function analyze(c: ArchChoices) {
  const strengths: string[] = [];
  const weaknesses: string[] = [];
  const fails: string[] = [];

  if (c.attention === "Dense" && ["128K", "1M"].includes(c.context)) {
    weaknesses.push("Quadratic cost at long context");
    fails.push("1M dense attention without sparsity/linear layers");
  }
  if (c.kv === "MHA") strengths.push("Maximum K/V diversity");
  if (c.kv === "MQA") {
    strengths.push("Smallest KV cache");
    weaknesses.push("Reduced K/V representational capacity");
  }
  if (c.kv === "GQA") strengths.push("Balanced cache vs quality");
  if (c.kv === "MLA") {
    strengths.push("Compressed latent KV");
    weaknesses.push("Architectural complexity");
  }
  if (c.kernel === "FlashAttention") strengths.push("Efficient exact attention on GPU");
  if (c.attention === "Linear / Delta") {
    strengths.push("O(n) recurrent memory");
    weaknesses.push("Different retrieval than softmax");
  }
  if (c.attention === "Sparse") strengths.push("Sub-quadratic connectivity");
  if (c.position === "ALiBi") strengths.push("Train-short/test-long bias");
  if (c.position === "RoPE" && c.context === "128K") {
    weaknesses.push("May need YaRN/PI for extrapolation");
  }

  return {
    strengths: strengths.length ? strengths : ["Reasonable default for moderate workloads"],
    weaknesses: weaknesses.length ? weaknesses : ["No major red flags at this scale"],
    fails: fails.length ? fails : ["Would struggle at extreme scale without hybrid design"],
    workload: `${c.context} context, ${c.attention} attention, ${c.kv} KV, ${c.position} position`,
  };
}

export function ArchitectureLab() {
  const { mode } = useApp();
  const [choices, setChoices] = useState<ArchChoices>(DEFAULT);
  const result = analyze(choices);

  const set = <K extends keyof ArchChoices>(k: K, v: ArchChoices[K]) =>
    setChoices((c) => ({ ...c, [k]: v }));

  return (
    <section id="chapter-11" className="scroll-mt-20">
      <h2 className="text-2xl font-bold">Build Your Architecture</h2>
      <p className="mt-2 text-muted">Educational composer — not a production recommender.</p>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <div className="panel space-y-4 p-6">
          {(
            [
              ["context", ["2K", "8K", "32K", "128K", "1M"]],
              ["attention", ["Dense", "Sliding Window", "Sparse", "Linear / Delta"]],
              ["position", ["Learned", "Sinusoidal", "RoPE", "ALiBi"]],
              ["kv", ["MHA", "GQA", "MQA", "MLA"]],
              ["kernel", ["Standard", "FlashAttention"]],
            ] as const
          ).map(([key, opts]) => (
            <fieldset key={key}>
              <legend className="text-sm font-medium capitalize">{key}</legend>
              <div className="mt-2 flex flex-wrap gap-2">
                {opts.map((o) => (
                  <button
                    key={o}
                    type="button"
                    onClick={() => set(key, o)}
                    className={`focus-ring rounded-lg px-3 py-1.5 text-xs ${
                      choices[key] === o ? "bg-cyan/20 text-cyan" : "bg-white/5 text-muted"
                    }`}
                  >
                    {o}
                  </button>
                ))}
              </div>
            </fieldset>
          ))}
        </div>

        <div className="panel panel-glow p-6">
          <h3 className="text-lg font-bold text-cyan">YOUR ARCHITECTURE</h3>
          <pre className="mt-4 overflow-x-auto rounded-lg bg-black/30 p-4 font-mono text-xs">
            {JSON.stringify(choices, null, 2)}
          </pre>
          <dl className="mt-4 space-y-3 text-sm">
            <div>
              <dt className="text-ok font-semibold">Strengths</dt>
              <dd className="text-muted">{result.strengths.join(" · ")}</dd>
            </div>
            <div>
              <dt className="text-danger font-semibold">Weaknesses</dt>
              <dd className="text-muted">{result.weaknesses.join(" · ")}</dd>
            </div>
            <div>
              <dt className="text-amber font-semibold">Would fail when</dt>
              <dd className="text-muted">{result.fails.join(" · ")}</dd>
            </div>
            <div>
              <dt className="font-semibold">Suits</dt>
              <dd className="text-muted">{result.workload}</dd>
            </div>
          </dl>
          {mode === "expert" && (
            <p className="mt-4 font-mono text-[10px] text-muted">
              Heuristic analysis only. Real architecture requires profiling on target hardware.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
