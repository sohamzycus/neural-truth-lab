import type { Metadata } from "next";
import { LabShell } from "@/components/layout/lab-shell";
import { Section } from "@/components/layout/section";

export const metadata: Metadata = {
  title: "Activations",
  description: "Without nonlinearity, a network cannot separate concentric rings.",
};

export default function ActivationsLabPage(): React.ReactElement {
  return (
    <LabShell
      labNumber={1}
      title="Activations Exist for a Reason"
      subtitle="Train linear vs ReLU models on the same rings dataset. Only activation changes."
      accentClass="text-[var(--lab-activations)]"
    >
      <Section id="claim" eyebrow="Claim" title="The experiment">
        <div className="glass-panel border-l-4 border-l-[var(--lab-activations)] p-8">
          <p className="text-xl font-medium leading-relaxed text-[var(--text-primary)] md:text-2xl">
            Without nonlinearity, a neural network cannot separate concentric rings
            — no matter how you train it.
          </p>
        </div>
        <p className="mt-8 text-[var(--text-muted)]">
          Interactive training UI coming in Milestone 3.
        </p>
      </Section>
    </LabShell>
  );
}
