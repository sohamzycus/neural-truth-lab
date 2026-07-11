"use client";

import dynamic from "next/dynamic";

const EmbeddingsLab = dynamic(
  () =>
    import("@/components/labs/embeddings-lab").then((m) => ({
      default: m.EmbeddingsLab,
    })),
  {
    ssr: false,
    loading: () => (
      <p className="px-4 py-16 text-center text-[var(--text-muted)]">
        Loading TensorFlow.js…
      </p>
    ),
  }
);

export function EmbeddingsLabClient(): React.ReactElement {
  return <EmbeddingsLab />;
}
