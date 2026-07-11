import type { Metadata } from "next";
import { LabShell } from "@/components/layout/lab-shell";
import { EmbeddingsLabClient } from "@/components/labs/embeddings-lab-client";

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
      <EmbeddingsLabClient />
    </LabShell>
  );
}
