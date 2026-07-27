import { ArrowDown } from "lucide-react";
import type { DomainEnhancement } from "../../types";
import { Section } from "../shell/AppShell";

export function DomainSection({ items }: { items: DomainEnhancement[] }) {
  return (
    <Section
      id="domain"
      eyebrow="Bird-specific"
      title="Domain Enhancements"
      subtitle={`${items.length} bird-specific layers — implemented in src/lib/pipeline/domain.ts (taxonomy, GPS mask, call norm, confidence, media).`}
    >
      <div className="grid gap-4 md:grid-cols-2">
        {items.map((item) => (
          <article key={item.id} className="panel p-5">
            <h3 className="text-lg font-medium">{item.title}</h3>
            <p className="mt-2 text-sm text-[var(--color-muted)]">{item.description}</p>
            <div className="mt-4 space-y-1">
              {item.inputs.map((inp) => (
                <div key={inp} className="font-mono text-xs text-[var(--color-text)]/80">
                  {inp}
                </div>
              ))}
            </div>
            <div className="my-2 flex justify-center text-[var(--color-muted)]">
              <ArrowDown className="h-3.5 w-3.5" />
            </div>
            <div className="rounded-md border border-[var(--color-accent)]/30 bg-[var(--color-accent)]/5 px-3 py-2 font-mono text-xs text-[var(--color-accent)]">
              {item.output}
            </div>
            {item.note ? <p className="mt-3 text-xs text-[var(--color-warn)]">{item.note}</p> : null}
          </article>
        ))}
      </div>
    </Section>
  );
}
