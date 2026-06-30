import type { Metadata } from "next";
import { LabShell } from "@/components/layout/lab-shell";
import { Section } from "@/components/layout/section";

export const metadata: Metadata = {
  title: "Embeddings",
  description: "Words used in similar contexts end up close together in embedding space.",
};

export default function EmbeddingsLabPage(): React.ReactElement {
  return (
    <LabShell
      labNumber={3}
      title="Embedding Universe"
      subtitle="Train embeddings on synthetic language and watch meaning cluster in space."
      accentClass="text-[var(--lab-embeddings)]"
    >
      <Section id="claim" eyebrow="Claim" title="The experiment">
        <div className="glass-panel border-l-4 border-l-[var(--lab-embeddings)] p-8">
          <p className="text-xl font-medium leading-relaxed text-[var(--text-primary)] md:text-2xl">
            Words that appear in similar contexts end up close together in
            embedding space.
          </p>
        </div>
        <p className="mt-8 text-[var(--text-muted)]">
          Embedding galaxy visualization coming in Milestone 5.
        </p>
      </Section>
    </LabShell>
  );
}
