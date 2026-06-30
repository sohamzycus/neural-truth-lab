import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { LABS, SITE } from "@/lib/constants";
import { Button } from "@/components/ui/button";
import { Section } from "@/components/layout/section";
import { LabCard } from "@/components/landing/lab-card";

export default function HomePage(): React.ReactElement {
  return (
    <>
      <section className="relative flex min-h-[85vh] flex-col items-center justify-center overflow-hidden px-4 py-24 text-center">
        <div
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(99,102,241,0.12)_0%,transparent_70%)]"
          aria-hidden
        />
        <div className="relative z-10 mx-auto max-w-4xl">
          <p className="mb-4 text-sm font-medium uppercase tracking-widest text-[var(--text-muted)]">
            Interactive deep learning
          </p>
          <h1 className="text-5xl font-bold tracking-tight md:text-7xl">
            <span className="gradient-hero-text">{SITE.name}</span>
          </h1>
          <p className="mx-auto mt-6 max-w-xl text-lg text-[var(--text-secondary)] md:text-xl">
            {SITE.shortTagline}
          </p>
          <p className="mx-auto mt-2 max-w-lg text-sm text-[var(--text-muted)]">
            Don&apos;t just read about it — discover four fundamental truths through
            live experiments.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button size="lg" asChild>
              <Link href="/labs">
                Start Experiment
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button variant="secondary" size="lg" asChild>
              <Link href="/lab/activations">Jump to Lab 1</Link>
            </Button>
          </div>
        </div>
      </section>

      <Section
        eyebrow="Four truths"
        title="Choose your experiment"
        className="border-t border-[var(--border)] bg-[var(--background-elevated)]"
      >
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {LABS.map((lab) => (
            <LabCard key={lab.id} lab={lab} />
          ))}
        </div>
      </Section>
    </>
  );
}
