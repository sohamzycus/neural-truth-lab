"use client";

import dynamic from "next/dynamic";

const DepthLab = dynamic(
  () => import("@/components/labs/depth-lab").then((m) => ({ default: m.DepthLab })),
  {
    ssr: false,
    loading: () => (
      <p className="px-4 py-16 text-center text-[var(--text-muted)]">
        Loading TensorFlow.js…
      </p>
    ),
  }
);

export function DepthLabClient(): React.ReactElement {
  return <DepthLab />;
}
