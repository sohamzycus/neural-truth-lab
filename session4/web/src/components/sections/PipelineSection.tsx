import { useState } from "react";
import type { PipelineStage } from "../../types";
import { Section } from "../shell/AppShell";
import { PipelineNode } from "../ui";

export function PipelineSection({ stages }: { stages: PipelineStage[] }) {
  const [activeId, setActiveId] = useState(stages[0]?.id ?? "");
  const active = stages.find((s) => s.id === activeId) ?? stages[0];

  return (
    <Section
      id="pipeline"
      eyebrow="End-to-end flow"
      title="Cleaning Pipeline"
      subtitle={`${stages.length} ordered stages from raw community notes to a versioned training corpus — select a stage for purpose, technique, and I/O.`}
    >
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)]">
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-1">
          {stages.map((stage) => (
            <PipelineNode
              key={stage.id}
              name={stage.name}
              active={active?.id === stage.id}
              onClick={() => setActiveId(stage.id)}
            />
          ))}
        </div>
        {active ? (
          <article className="panel p-6">
            <h3 className="text-xl font-medium">{active.name}</h3>
            <dl className="mt-5 space-y-4 text-sm">
              <div>
                <dt className="text-[11px] uppercase tracking-[0.16em] text-[var(--color-muted)]">Purpose</dt>
                <dd className="mt-1 text-[var(--color-text)]">{active.purpose}</dd>
              </div>
              <div>
                <dt className="text-[11px] uppercase tracking-[0.16em] text-[var(--color-muted)]">Technique</dt>
                <dd className="mt-1 font-mono text-xs text-[var(--color-accent)]">{active.technique}</dd>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <dt className="text-[11px] uppercase tracking-[0.16em] text-[var(--color-muted)]">Input</dt>
                  <dd className="mt-1 text-[var(--color-muted)]">{active.input}</dd>
                </div>
                <div>
                  <dt className="text-[11px] uppercase tracking-[0.16em] text-[var(--color-muted)]">Output</dt>
                  <dd className="mt-1 text-[var(--color-muted)]">{active.output}</dd>
                </div>
              </div>
              <div>
                <dt className="text-[11px] uppercase tracking-[0.16em] text-[var(--color-warn)]">Challenges</dt>
                <dd className="mt-1 text-[var(--color-muted)]">{active.challenges}</dd>
              </div>
            </dl>
          </article>
        ) : null}
      </div>
    </Section>
  );
}
