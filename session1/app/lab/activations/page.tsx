import type { Metadata } from "next";
import { LabShell } from "@/components/layout/lab-shell";
import { ActivationsLabClient } from "@/components/labs/activations-lab-client";

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
      <ActivationsLabClient />
    </LabShell>
  );
}
