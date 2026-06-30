"use client";

import Link from "next/link";
import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { SITE } from "@/lib/constants";
import {
  heroBody,
  heroCta,
  heroEyebrow,
  heroSubtitle,
  heroTitle,
} from "@/animations/variants";
import { Button } from "@/components/ui/button";

const HeroAnimation = dynamic(
  () =>
    import("@/components/landing/hero-animation").then((m) => ({
      default: m.HeroAnimation,
    })),
  { ssr: false }
);

export function HeroSection(): React.ReactElement {
  return (
    <section className="relative flex min-h-[90vh] flex-col items-center justify-center overflow-hidden px-4 py-24 text-center">
      <HeroAnimation />
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(99,102,241,0.08)_0%,transparent_65%)]"
        aria-hidden
      />

      <motion.div
        className="relative z-10 mx-auto max-w-4xl"
        initial="hidden"
        animate="visible"
      >
        <motion.p
          variants={heroEyebrow}
          className="mb-4 text-sm font-medium uppercase tracking-widest text-[var(--text-muted)]"
        >
          Interactive deep learning
        </motion.p>

        <motion.h1
          variants={heroTitle}
          className="text-5xl font-bold tracking-tight md:text-7xl"
        >
          <span className="gradient-hero-text">{SITE.name}</span>
        </motion.h1>

        <motion.p
          variants={heroSubtitle}
          className="mx-auto mt-6 max-w-xl text-lg text-[var(--text-secondary)] md:text-xl"
        >
          {SITE.shortTagline}
        </motion.p>

        <motion.p
          variants={heroBody}
          className="mx-auto mt-2 max-w-lg text-sm text-[var(--text-muted)]"
        >
          Don&apos;t just read about it — discover four fundamental truths through
          live experiments.
        </motion.p>

        <motion.div
          variants={heroCta}
          className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row"
        >
          <Button size="lg" asChild>
            <Link href="/labs">
              Start Experiment
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
          <Button variant="secondary" size="lg" asChild>
            <Link href="/lab/activations">Jump to Lab 1</Link>
          </Button>
        </motion.div>
      </motion.div>
    </section>
  );
}
