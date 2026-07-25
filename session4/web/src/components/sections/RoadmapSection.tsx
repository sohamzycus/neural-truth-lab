import { ArrowDown } from "lucide-react";
import type { RoadmapItem } from "../../types";
import { Section } from "../shell/AppShell";

export function RoadmapSection({ items }: { items: RoadmapItem[] }) {
  return (
    <Section
      id="roadmap"
      eyebrow="Multimodal path"
      title="Future Roadmap"
      subtitle="How this textual corpus plugs into Ataavi’s multimodal Bird Foundation Model."
    >
      <div className="mx-auto max-w-xl">
        {items.map((item, i) => (
          <div key={item.id}>
            <div className="panel px-5 py-4">
              <div className="font-mono text-[11px] text-[var(--color-accent)]">{String(i + 1).padStart(2, "0")}</div>
              <h3 className="mt-1 font-medium">{item.label}</h3>
              <p className="mt-1 text-sm text-[var(--color-muted)]">{item.description}</p>
            </div>
            {i < items.length - 1 ? (
              <div className="flex justify-center py-2 text-[var(--color-muted)]">
                <ArrowDown className="h-4 w-4" />
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </Section>
  );
}
