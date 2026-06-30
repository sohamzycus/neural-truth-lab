"use client";

import dynamic from "next/dynamic";

const GeneralizationLab = dynamic(
  () =>
    import("@/components/labs/generalization-lab").then((m) => ({
      default: m.GeneralizationLab,
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

export function GeneralizationLabClient(): React.ReactElement {
  return <GeneralizationLab />;
}
