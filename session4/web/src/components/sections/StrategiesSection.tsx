import { useState } from "react";
import type { Strategy } from "../../types";
import { isStrategyImplemented, STRATEGY_IMPLEMENTATION } from "../../lib/pipeline/strategyMap";
import { Section } from "../shell/AppShell";
import { ExpandableCard } from "../ui";

export function StrategiesSection({ strategies }: { strategies: Strategy[] }) {
  const [openId, setOpenId] = useState<string | null>(strategies[0]?.id ?? null);
  const implementedCount = strategies.filter((s) => isStrategyImplemented(s.id)).length;

  return (
    <Section
      id="strategies"
      eyebrow="Cleaning playbook"
      title="Corpus Cleaning Strategies"
      subtitle={`${strategies.length} preprocessing strategies — ${implementedCount}/${strategies.length} implemented in src/lib with selfcheck coverage. Expand for why, algorithms, and before/after.`}
    >
      <div className="space-y-2">
        {strategies.map((s) => {
          const impl = STRATEGY_IMPLEMENTATION[s.id];
          const done = isStrategyImplemented(s.id);
          return (
            <ExpandableCard
              key={s.id}
              title={
                <span className="flex flex-wrap items-center gap-2">
                  {s.title}
                  <span
                    className={`rounded-full px-2 py-0.5 font-mono text-[9px] uppercase tracking-wide ${
                      done
                        ? "border border-[var(--color-ok)]/40 bg-[var(--color-ok)]/10 text-[var(--color-ok)]"
                        : "border border-[var(--color-warn)]/40 text-[var(--color-warn)]"
                    }`}
                  >
                    {done ? "implemented" : "documented"}
                  </span>
                </span>
              }
              open={openId === s.id}
              onToggle={() => setOpenId((id) => (id === s.id ? null : s.id))}
            >
              {impl ? (
                <p className="mb-3 font-mono text-[10px] text-[var(--color-accent)]">
                  {impl.module} → {impl.fn}
                </p>
              ) : null}
              <p className="text-[var(--color-text)]">
                <span className="text-[var(--color-muted)]">Why needed · </span>
                {s.why}
              </p>
              <ul className="mt-3 list-disc space-y-1 pl-5">
                {s.algorithms.map((a) => (
                  <li key={a}>{a}</li>
                ))}
              </ul>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <div>
                  <div className="mb-1 text-[10px] uppercase tracking-wider text-[var(--color-danger)]">Before</div>
                  <pre className="whitespace-pre-wrap rounded bg-black/30 p-3 font-mono text-xs">{s.before}</pre>
                </div>
                <div>
                  <div className="mb-1 text-[10px] uppercase tracking-wider text-[var(--color-ok)]">After</div>
                  <pre className="whitespace-pre-wrap rounded bg-black/30 p-3 font-mono text-xs">{s.after}</pre>
                </div>
              </div>
            </ExpandableCard>
          );
        })}
      </div>
    </Section>
  );
}
