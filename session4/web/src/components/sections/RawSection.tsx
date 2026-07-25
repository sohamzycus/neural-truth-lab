import type { RawObservation } from "../../types";
import { Section } from "../shell/AppShell";
import { ObservationCard } from "../ui";

export function RawSection({ data }: { data: RawObservation[] }) {
  return (
    <Section
      id="raw"
      eyebrow="The problem"
      title="Raw Observation Viewer"
      subtitle="Noisy community notes — the reason a cleaning pipeline exists."
    >
      <div className="grid gap-4 lg:grid-cols-2">
        {data.map((o) => (
          <ObservationCard key={o.id} title={o.title} issues={o.issues} text={o.text} meta={o.meta} />
        ))}
      </div>
    </Section>
  );
}
