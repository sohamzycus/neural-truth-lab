import type { Metadata } from "next";
import { LabShell } from "@/components/layout/lab-shell";
import { DepthLabClient } from "@/components/labs/depth-lab-client";

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
      <DepthLabClient />
    </LabShell>
  );
}
