import type { Metadata } from "next";
import { LABS, SITE } from "@/lib/constants";
import { Section } from "@/components/layout/section";
import { LabCard } from "@/components/landing/lab-card";

export const metadata: Metadata = {
  title: "Labs",
  description: `Explore all interactive labs — ${SITE.tagline}`,
};

export default function LabsPage(): React.ReactElement {
  return (
    <Section
      eyebrow="Experiments"
      title="All labs"
      className="min-h-[60vh]"
    >
      <p className="mb-10 max-w-2xl text-[var(--text-secondary)]">
        Four interactive experiments. Each lab proves one fundamental truth of deep
        learning through live training and visual proof.
      </p>
      <div className="grid gap-6 sm:grid-cols-2">
        {LABS.map((lab) => (
          <LabCard key={lab.id} lab={lab} />
        ))}
      </div>
    </Section>
  );
}
