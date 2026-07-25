import type { Discovery } from "../../types";
import { Section } from "../shell/AppShell";
import { InsightTile } from "../ui";

export function DiscoveriesSection({ items }: { items: Discovery[] }) {
  return (
    <Section
      id="discoveries"
      eyebrow="Corpus insights"
      title="Interesting Discoveries"
      subtitle="Browse corpus curiosities. Hover a tile for why it matters."
    >
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {items.map((d) => (
          <InsightTile key={d.id} label={d.label} value={d.value} detail={d.detail} why={d.why} />
        ))}
      </div>
    </Section>
  );
}
