import { useMemo, useState } from "react";
import type { FertilityProjections, InferenceCosts } from "../types";

const SCENARIOS: { key: string; label: string }[] = [
  { key: "llama3_generic", label: "Llama-3 generic" },
  { key: "population_weighted", label: "Population-weighted vocab" },
  { key: "india_first_128k", label: "India-first 128k (proposed)" },
  { key: "oracle_theoretical", label: "Oracle (theoretical)" },
];

export function FertilityExplorer({
  fertility,
  inference,
}: {
  fertility: FertilityProjections | null;
  inference: InferenceCosts | null;
}) {
  const [scenario, setScenario] = useState("india_first_128k");
  const [queriesPerDay, setQueriesPerDay] = useState(30_000_000);
  const [tokensPerQuery, setTokensPerQuery] = useState(1200);

  const calc = useMemo(() => {
    if (!fertility || !inference) return null;
    const baseline = fertility.projections.llama3_generic.relative_inference_cost;
    const selected = fertility.projections[scenario];
    if (!selected) return null;

    const baselineTco = inference.annual_tco_usd_millions["40b_int4_baseline"];
    const annualTokens = queriesPerDay * tokensPerQuery * 365;
    const scaledBaseline = (annualTokens / 1.32e13) * baselineTco;
    const scaledSelected = scaledBaseline * (selected.relative_inference_cost / baseline);
    const savings = scaledBaseline - scaledSelected;

    return {
      fertility: selected.avg_indic_fertility,
      annualTcoM: scaledSelected,
      savingsM: savings,
      savingsPct: ((1 - selected.relative_inference_cost / baseline) * 100).toFixed(0),
    };
  }, [fertility, inference, scenario, queriesPerDay, tokensPerQuery]);

  if (!fertility || !inference || !calc) return null;

  return (
    <section className="rounded border border-[var(--border)] bg-white p-5">
      <div className="mb-4 flex flex-col gap-1 sm:flex-row sm:items-baseline sm:justify-between">
        <div>
          <h3 className="font-semibold">Fertility → TCO Explorer</h3>
          <p className="text-sm text-[var(--muted)]">
            Tokenizer choice is a budget line item — not an implementation detail.
          </p>
        </div>
        <span className="font-mono text-xs text-[var(--accent)]">
          −{calc.savingsPct}% vs generic at this scale
        </span>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <label className="block text-sm">
          <span className="text-[var(--muted)]">Tokenizer scenario</span>
          <select
            value={scenario}
            onChange={(e) => setScenario(e.target.value)}
            className="mt-1 w-full rounded border border-[var(--border)] bg-[var(--paper)] px-3 py-2 font-mono text-sm"
          >
            {SCENARIOS.map((s) => (
              <option key={s.key} value={s.key}>{s.label}</option>
            ))}
          </select>
        </label>

        <label className="block text-sm">
          <span className="text-[var(--muted)]">
            Daily queries: {(queriesPerDay / 1e6).toFixed(0)}M
          </span>
          <input
            type="range"
            min={1_000_000}
            max={100_000_000}
            step={1_000_000}
            value={queriesPerDay}
            onChange={(e) => setQueriesPerDay(Number(e.target.value))}
            className="mt-2 w-full accent-[var(--accent)]"
          />
        </label>

        <label className="block text-sm md:col-span-2">
          <span className="text-[var(--muted)]">Avg tokens per query: {tokensPerQuery}</span>
          <input
            type="range"
            min={200}
            max={4000}
            step={100}
            value={tokensPerQuery}
            onChange={(e) => setTokensPerQuery(Number(e.target.value))}
            className="mt-2 w-full accent-[var(--accent-2)]"
          />
        </label>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-3 border-t border-[var(--border)] pt-4 font-mono text-sm">
        <div>
          <p className="text-[10px] uppercase text-[var(--muted)]">Avg Indic fertility</p>
          <p className="text-xl font-semibold tabular-nums">{calc.fertility.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-[10px] uppercase text-[var(--muted)]">Annual TCO</p>
          <p className="text-xl font-semibold tabular-nums">${calc.annualTcoM.toFixed(1)}M</p>
        </div>
        <div>
          <p className="text-[10px] uppercase text-[var(--muted)]">Savings vs generic</p>
          <p className="text-xl font-semibold tabular-nums text-[var(--accent)]">
            ${calc.savingsM.toFixed(1)}M
          </p>
        </div>
      </div>
    </section>
  );
}
