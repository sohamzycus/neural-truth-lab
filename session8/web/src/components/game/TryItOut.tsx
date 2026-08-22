import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { TRY_IT_PROBLEMS, type TryItProblem } from "../../data/tryItProblems";
import { FadeIn } from "../ui/FadeIn";

type Pick = TryItProblem["answer"];

const KEYS = ["attention", "position", "kv", "kernel"] as const;

function scorePick(pick: Pick, answer: Pick) {
  return KEYS.reduce((n, k) => n + (pick[k] === answer[k] ? 1 : 0), 0);
}

export function TryItOut() {
  const [activeId, setActiveId] = useState(TRY_IT_PROBLEMS[0].id);
  const [picks, setPicks] = useState<Record<string, Partial<Pick>>>({});
  const [checked, setChecked] = useState<Record<string, boolean>>({});

  const problem = TRY_IT_PROBLEMS.find((p) => p.id === activeId) ?? TRY_IT_PROBLEMS[0];
  const pick = picks[problem.id] ?? {};
  const isChecked = checked[problem.id] ?? false;
  const complete = KEYS.every((k) => pick[k]);

  const setField = (key: keyof Pick, value: string) => {
    setPicks((prev) => ({
      ...prev,
      [problem.id]: { ...prev[problem.id], [key]: value },
    }));
    setChecked((prev) => ({ ...prev, [problem.id]: false }));
  };

  const check = () => {
    if (!complete) return;
    setChecked((prev) => ({ ...prev, [problem.id]: true }));
  };

  const score = isChecked ? scorePick(pick as Pick, problem.answer) : 0;

  return (
    <section id="try-it-out" className="scroll-mt-24 mt-16">
      <FadeIn>
        <h2 className="text-2xl font-bold">Try It Out</h2>
        <p className="mt-2 text-muted">
          Six workloads. Pick attention, position, KV, and kernel — then check your reasoning.
        </p>
      </FadeIn>

      <div className="mt-6 flex flex-wrap gap-2">
        {TRY_IT_PROBLEMS.map((p, i) => {
          const done = checked[p.id];
          const s = done ? scorePick(picks[p.id] as Pick, p.answer) : 0;
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => setActiveId(p.id)}
              className={`focus-ring rounded-full px-3 py-1.5 text-xs font-medium transition-all ${
                activeId === p.id ? "chip-active" : "chip"
              }`}
            >
              {i + 1}. {p.title}
              {done && (
                <span className="ml-1 opacity-70">
                  ({s}/{KEYS.length})
                </span>
              )}
            </button>
          );
        })}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={problem.id}
          initial={{ opacity: 0, x: 12 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -12 }}
          transition={{ duration: 0.25 }}
          className="panel panel-glow mt-6 p-6"
        >
          <h3 className="text-xl font-bold">{problem.title}</h3>
          <p className="mt-2 text-muted">{problem.description}</p>

          <div className="mt-6 space-y-5">
            {KEYS.map((key) => (
              <fieldset key={key}>
                <legend className="text-sm font-semibold capitalize text-text">{key}</legend>
                <div className="mt-2 flex flex-wrap gap-2">
                  {problem.options[key].map((opt) => {
                    const selected = pick[key] === opt;
                    const correct = problem.answer[key] === opt;
                    let cls = "chip";
                    if (selected) cls = "chip-active";
                    if (isChecked && selected && correct) cls = "chip-correct";
                    if (isChecked && selected && !correct) cls = "chip-wrong";
                    if (isChecked && !selected && correct) cls = "chip-correct";

                    return (
                      <button
                        key={opt}
                        type="button"
                        onClick={() => !isChecked && setField(key, opt)}
                        disabled={isChecked}
                        className={`focus-ring ${cls} max-w-full whitespace-normal text-left leading-snug`}
                      >
                        {opt}
                      </button>
                    );
                  })}
                </div>
              </fieldset>
            ))}
          </div>

          {!isChecked ? (
            <button
              type="button"
              onClick={check}
              disabled={!complete}
              className="focus-ring mt-6 rounded-lg bg-violet/15 px-5 py-2.5 text-sm font-medium text-violet disabled:opacity-40"
            >
              Check my choices
            </button>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 space-y-3 rounded-lg border border-theme bg-[var(--color-surface-2)] p-4 text-sm"
            >
              <p className="font-semibold text-text">
                Score: {score}/{KEYS.length}
                {score === KEYS.length ? " — excellent trade-off reasoning!" : " — compare with the model answer below."}
              </p>
              <div className="flex flex-wrap gap-2">
                {KEYS.map((k) => (
                  <span key={k} className="chip chip-active max-w-full whitespace-normal">
                    <span className="capitalize opacity-70">{k}:</span> {problem.answer[k]}
                  </span>
                ))}
              </div>
              <p><strong>Rationale:</strong> {problem.rationale}</p>
              <p className="text-danger"><strong>Pitfalls:</strong> {problem.pitfalls}</p>
              <button
                type="button"
                onClick={() => setChecked((prev) => ({ ...prev, [problem.id]: false }))}
                className="focus-ring text-xs text-[var(--color-accent)] hover:underline"
              >
                Try again
              </button>
            </motion.div>
          )}
        </motion.div>
      </AnimatePresence>
    </section>
  );
}
