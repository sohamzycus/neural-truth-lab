import { useState } from "react";
import type { Strategy } from "../../types";
import { Section } from "../shell/AppShell";
import { ExpandableCard } from "../ui";

export function StrategiesSection({ strategies }: { strategies: Strategy[] }) {
  const [openId, setOpenId] = useState<string | null>(strategies[0]?.id ?? null);

  return (
    <Section
      id="strategies"
      eyebrow="Cleaning playbook"
      title="Corpus Cleaning Strategies"
      subtitle="Ten preprocessing strategies we apply before text enters Ataavi pretraining — expand for algorithms and before/after examples."
    >
      <div className="space-y-2">
        {strategies.map((s) => (
          <ExpandableCard
            key={s.id}
            title={s.title}
            open={openId === s.id}
            onToggle={() => setOpenId((id) => (id === s.id ? null : s.id))}
          >
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
        ))}
      </div>
    </Section>
  );
}
