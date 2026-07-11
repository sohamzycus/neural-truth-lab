"use client";

import Link from "next/link";
import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { SITE, LABS } from "@/lib/constants";
import {
  heroBody,
  heroCta,
  heroEyebrow,
  heroSubtitle,
  heroTitle,
  listItem,
  listStagger,
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
    <section className="relative overflow-hidden border-b border-[var(--border)] px-4 py-16 sm:py-20">
      <HeroAnimation />
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(29,78,216,0.07)_0%,transparent_55%)]"
        aria-hidden
      />

      <div className="relative z-10 mx-auto grid max-w-6xl gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <motion.div initial="hidden" animate="visible">
          <motion.p
            variants={heroEyebrow}
            className="mb-3 font-mono text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)]"
          >
            Four executable experiments · runs live in-browser
          </motion.p>

          <motion.h1
            variants={heroTitle}
            className="font-display text-4xl font-bold tracking-tight text-[var(--text-primary)] md:text-5xl lg:text-6xl"
          >
            Things that make{" "}
            <span className="gradient-hero-text">deep learning work</span>
          </motion.h1>

          <motion.p
            variants={heroSubtitle}
            className="mt-5 max-w-xl text-base leading-relaxed text-[var(--text-secondary)] md:text-lg"
          >
            {SITE.tagline} Run each proof yourself — watch boundaries form, gaps
            close, and embeddings cluster. No slides, just live TensorFlow.js.
          </motion.p>

          <motion.p variants={heroBody} className="mt-2 text-sm text-[var(--text-muted)]">
            {SITE.name}
          </motion.p>

          <motion.div
            variants={heroCta}
            className="mt-8 flex flex-col gap-3 sm:flex-row"
          >
            <Button size="lg" asChild>
              <Link href="/lab/activations">
                Run first experiment
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button variant="secondary" size="lg" asChild>
              <Link href="/labs">Browse all labs</Link>
            </Button>
          </motion.div>
        </motion.div>

        <motion.ol
          variants={listStagger}
          initial="hidden"
          animate="visible"
          className="grid gap-2 sm:grid-cols-2 lg:grid-cols-1"
        >
          {LABS.map((lab) => (
            <motion.li key={lab.id} variants={listItem}>
              <Link
                href={lab.href}
                className={`group flex items-center gap-3 rounded-lg border border-[var(--border)] bg-[var(--background-elevated)] px-4 py-3 shadow-sm transition-colors hover:border-[var(--border-strong)] ${lab.borderClass}`}
              >
                <span
                  className={`font-mono text-xs font-semibold ${lab.accentClass}`}
                >
                  EXP {String(lab.number).padStart(2, "0")}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm font-medium text-[var(--text-primary)] group-hover:text-[var(--accent-primary)]">
                    {lab.title}
                  </span>
                  <span className="block truncate text-xs text-[var(--text-muted)]">
                    {lab.headline}
                  </span>
                </span>
                <ArrowRight className="h-4 w-4 shrink-0 text-[var(--text-muted)] opacity-0 transition-opacity group-hover:opacity-100" />
              </Link>
            </motion.li>
          ))}
        </motion.ol>
      </div>
    </section>
  );
}
