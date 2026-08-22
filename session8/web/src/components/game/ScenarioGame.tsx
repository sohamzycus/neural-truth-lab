import { useState } from "react";
import { SCENARIOS } from "../../data/scenarios";

export function ScenarioGame() {
  const [idx, setIdx] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const scenario = SCENARIOS[idx];

  return (
    <section className="mt-16">
      <h2 className="text-2xl font-bold">What Would You Choose?</h2>
      <p className="mt-2 text-muted">Reason about trade-offs before seeing the answer.</p>

      <div className="panel mt-6 p-6">
        <p className="text-xs text-muted">Scenario {idx + 1} / {SCENARIOS.length}</p>
        <h3 className="mt-2 text-xl font-bold">{scenario.title}</h3>
        <p className="mt-2 text-muted">{scenario.description}</p>

        {!revealed ? (
          <button
            type="button"
            onClick={() => setRevealed(true)}
            className="focus-ring mt-6 rounded-lg bg-violet/20 px-4 py-2 text-sm text-violet"
          >
            Reveal answer
          </button>
        ) : (
          <div className="mt-6 space-y-4">
            <div className="grid gap-2 font-mono text-sm sm:grid-cols-2">
              {Object.entries(scenario.choices).map(([k, v]) => (
                <div key={k} className="rounded bg-white/5 p-2">
                  <span className="text-muted">{k}:</span> {v}
                </div>
              ))}
            </div>
            <p className="text-sm"><strong>Rationale:</strong> {scenario.rationale}</p>
            <p className="text-sm text-danger"><strong>Pitfalls:</strong> {scenario.pitfalls}</p>
          </div>
        )}

        <div className="mt-6 flex gap-2">
          <button
            type="button"
            onClick={() => { setIdx((i) => (i + 1) % SCENARIOS.length); setRevealed(false); }}
            className="focus-ring rounded-lg bg-white/5 px-4 py-2 text-sm"
          >
            Next scenario →
          </button>
        </div>
      </div>
    </section>
  );
}
