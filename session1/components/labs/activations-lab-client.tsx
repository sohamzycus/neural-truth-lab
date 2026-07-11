"use client";

import dynamic from "next/dynamic";

const ActivationsLab = dynamic(
  () =>
    import("@/components/labs/activations-lab").then((m) => ({
      default: m.ActivationsLab,
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

export function ActivationsLabClient(): React.ReactElement {
  return <ActivationsLab />;
}
