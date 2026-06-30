import type { Metadata } from "next";
import { LabShell } from "@/components/layout/lab-shell";
import { Section } from "@/components/layout/section";

export const metadata: Metadata = {
  title: "Generalization",
  description: "More data closes the gap between memorization and true learning.",
};

export default function GeneralizationLabPage(): React.ReactElement {
  return (
    <LabShell
      labNumber={4}
      title="Generalization Arena"
      subtitle="Train on 20 to 20,000 samples and watch the generalization gap close."
      accentClass="text-[var(--lab-generalization)]"
    >
      <Section id="claim" eyebrow="Claim" title="The experiment">
        <div className="glass-panel border-l-4 border-l-[var(--lab-generalization)] p-8">
          <p className="text-xl font-medium leading-relaxed text-[var(--text-primary)] md:text-2xl">
            More data closes the gap between what a model memorizes and what it
            truly learns.
          </p>
        </div>
        <p className="mt-8 text-[var(--text-muted)]">
          Generalization graph coming in Milestone 6.
        </p>
      </Section>
    </LabShell>
  );
}
