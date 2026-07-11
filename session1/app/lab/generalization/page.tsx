import type { Metadata } from "next";
import { LabShell } from "@/components/layout/lab-shell";
import { GeneralizationLabClient } from "@/components/labs/generalization-lab-client";

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
      <GeneralizationLabClient />
    </LabShell>
  );
}
