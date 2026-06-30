import type { Metadata } from "next";
import { LabShell } from "@/components/layout/lab-shell";
import { Section } from "@/components/layout/section";

export const metadata: Metadata = {
  title: "Depth",
  description: "Depth without activation is mathematically equivalent to one layer.",
};

export default function DepthLabPage(): React.ReactElement {
  return (
    <LabShell
      labNumber={2}
      title="Depth Without Nonlinearity"
      subtitle="Compare 1 linear layer, 5 linear layers, and 5 ReLU layers on the same data."
      accentClass="text-[var(--lab-depth)]"
    >
      <Section id="claim" eyebrow="Claim" title="The experiment">
        <div className="glass-panel border-l-4 border-l-[var(--lab-depth)] p-8">
          <p className="text-xl font-medium leading-relaxed text-[var(--text-primary)] md:text-2xl">
            Stacking linear layers does not add expressive power. Five linear
            layers collapse into one.
          </p>
        </div>
        <p className="mt-8 text-[var(--text-muted)]">
          Weight collapse visualization coming in Milestone 4.
        </p>
      </Section>
    </LabShell>
  );
}
