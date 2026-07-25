import { Section } from "../shell/AppShell";

const POINTS = [
  { title: "Natural language", body: "Observers write freely — behavior, uncertainty, and reasoning stay in the text." },
  { title: "Habitat & weather", body: "Notes encode micro-habitat, monsoon context, and light conditions labels never capture." },
  { title: "Migration & time", body: "Timestamps and phenology cues support seasonal and movement models." },
  { title: "Geolocation", body: "Coordinates ground language in place — with conservation-aware precision controls." },
  { title: "Human uncertainty", body: "Phrases like “possible” and “heard only” teach calibrated confidence." },
  { title: "Multilingual signal", body: "Community notes mix English with regional languages — ideal for India-first LLMs." },
];

export function WhyNotesSection() {
  return (
    <Section
      id="why-notes"
      eyebrow="Context"
      title="Why Bird Observation Notes?"
      subtitle="Unlike structured checkboxes, field notes carry the texture language models need: behavior, habitat, migration, weather, reasoning, uncertainty, time, and place."
    >
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {POINTS.map((p) => (
          <div key={p.title} className="panel p-5">
            <h3 className="font-medium text-[var(--color-text)]">{p.title}</h3>
            <p className="mt-2 text-sm text-[var(--color-muted)]">{p.body}</p>
          </div>
        ))}
      </div>
      <p className="measure mt-8 text-sm text-[var(--color-muted)]">
        That richness makes observation notes ideal pretraining text for a bird intelligence stack — if we can turn community noise into a trustworthy corpus.
      </p>
    </Section>
  );
}
