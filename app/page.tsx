import { HeroSection } from "@/components/landing/hero-section";
import { LabCardsSection } from "@/components/landing/lab-cards-section";

export default function HomePage(): React.ReactElement {
  return (
    <>
      <HeroSection />
      <LabCardsSection
        eyebrow="Four truths"
        title="Choose your experiment"
        columns="four"
        className="border-t border-[var(--border)] bg-[var(--background-elevated)] py-16 md:py-24"
      />
    </>
  );
}
