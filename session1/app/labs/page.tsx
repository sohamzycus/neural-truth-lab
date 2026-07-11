import type { Metadata } from "next";
import { SITE } from "@/lib/constants";
import { LabCardsSection } from "@/components/landing/lab-cards-section";

export const metadata: Metadata = {
  title: "Labs",
  description: `Explore all interactive labs — ${SITE.tagline}`,
};

export default function LabsPage(): React.ReactElement {
  return (
    <LabCardsSection
      eyebrow="Experiments"
      title="All labs"
      description="Four interactive experiments. Each lab proves one fundamental truth of deep learning through live training and visual proof."
      columns="two"
      className="min-h-[60vh] py-16 md:py-24"
    />
  );
}
