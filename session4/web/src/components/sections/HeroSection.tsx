import { motion } from "framer-motion";
import { ArrowDown, Bird, Database, Sparkles } from "lucide-react";
import type { RawObservation } from "../../types";
import { AnimatedCount } from "../ui/AnimatedCount";
import { MarqueeTicker } from "../ui/IngestionTicker";

const FLOW = [
  { label: "Community bird notes", detail: "eBird-style observations from India & beyond" },
  { label: "Corpus Forge", detail: "Clean, dedupe, enrich, decontaminate" },
  { label: "Training corpus", detail: "Trustworthy text for pretraining" },
  { label: "Ataavi foundation model", detail: "Multimodal bird intelligence" },
];

export function HeroSection({
  observationCount,
  observerCount,
  rawSample,
}: {
  observationCount: number;
  observerCount: number;
  rawSample: RawObservation[];
}) {
  return (
    <section id="hero" className="relative overflow-hidden px-4 pb-8 pt-16 sm:px-6 lg:px-8">
      <div className="pointer-events-none absolute -right-20 top-10 h-64 w-64 rounded-full bg-[var(--color-accent)]/10 blur-3xl" />
      <div className="pointer-events-none absolute -left-16 bottom-0 h-48 w-48 rounded-full bg-[var(--color-accent-warm)]/10 blur-3xl" />
      <div className="pointer-events-none absolute right-[12%] top-[18%] float-bird opacity-[0.07]">
        <Bird className="h-24 w-24 text-[var(--color-accent)]" />
      </div>
      <div className="pointer-events-none absolute left-[8%] top-[42%] float-bird-delay opacity-[0.05]">
        <Bird className="h-16 w-16 text-[var(--color-accent-sky)]" />
      </div>

      <div className="relative mx-auto max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center gap-2 rounded-full border border-[var(--color-accent)]/30 bg-[var(--color-accent)]/10 px-3 py-1"
        >
          <Bird className="h-3.5 w-3.5 text-[var(--color-accent)]" />
          <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-[var(--color-accent)]">
            Ataavi · Bird Intelligence Platform
          </span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="mt-6 max-w-4xl text-4xl font-semibold tracking-[-0.03em] text-[var(--color-text)] sm:text-6xl"
        >
          Corpus Forge
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="measure mt-5 text-lg text-[var(--color-muted)] sm:text-xl"
        >
          The internal data-engineering portal where we turn noisy bird observation notes into a production-ready
          knowledge corpus — the textual foundation for Ataavi&apos;s multimodal bird AI.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.12 }}
          className="mt-8 grid gap-4 sm:grid-cols-3"
        >
          <div className="panel-accent panel shimmer-border p-5 text-center sm:text-left">
            <div className="text-[10px] uppercase tracking-[0.2em] text-[var(--color-muted)]">Corpus scale</div>
            <div className="mt-2 font-mono text-4xl font-semibold tracking-tight text-[var(--color-accent)] sm:text-5xl">
              <AnimatedCount value={observationCount} compact />
            </div>
            <div className="mt-1 text-xs text-[var(--color-muted)]">raw observations ingested</div>
          </div>
          <div className="panel p-5 text-center sm:text-left">
            <div className="text-[10px] uppercase tracking-[0.2em] text-[var(--color-muted)]">Contributors</div>
            <div className="mt-2 font-mono text-3xl font-semibold text-[var(--color-text)]">
              <AnimatedCount value={observerCount} compact />
            </div>
            <div className="mt-1 text-xs text-[var(--color-muted)]">field observers worldwide</div>
          </div>
          <div className="panel p-5 text-center sm:text-left">
            <div className="text-[10px] uppercase tracking-[0.2em] text-[var(--color-muted)]">Pipeline status</div>
            <div className="mt-2 flex items-center justify-center gap-2 sm:justify-start">
              <span className="relative flex h-2.5 w-2.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[var(--color-ok)] opacity-70" />
                <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-[var(--color-ok)]" />
              </span>
              <span className="font-mono text-lg text-[var(--color-ok)]">Ingesting</span>
            </div>
            <div className="mt-1 text-xs text-[var(--color-muted)]">India-primary · global decontamination slice</div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="mt-8 grid gap-4 lg:grid-cols-3"
        >
          <div className="panel-accent panel p-5">
            <div className="flex items-center gap-2 text-[var(--color-accent-warm)]">
              <Sparkles className="h-4 w-4" />
              <span className="text-xs font-medium uppercase tracking-wider">What we&apos;re building</span>
            </div>
            <p className="mt-3 text-sm text-[var(--color-text)]">
              <strong className="font-medium">Ataavi</strong> — a foundation model that understands birds through photos,
              calls, spectrograms, habitat, migration, and field notes.
            </p>
          </div>
          <div className="panel p-5">
            <div className="flex items-center gap-2 text-[var(--color-accent)]">
              <Database className="h-4 w-4" />
              <span className="text-xs font-medium uppercase tracking-wider">What this portal is</span>
            </div>
            <p className="mt-3 text-sm text-[var(--color-muted)]">
              Corpus Forge documents and demonstrates how we engineer the <em>text</em> layer: ingest, clean, enrich,
              and ship a corpus you can actually train on.
            </p>
          </div>
          <div className="panel p-5">
            <div className="flex items-center gap-2 text-[var(--color-accent-sky)]">
              <Bird className="h-4 w-4" />
              <span className="text-xs font-medium uppercase tracking-wider">Why it matters</span>
            </div>
            <p className="mt-3 text-sm text-[var(--color-muted)]">
              Community notes carry behavior, habitat, and uncertainty that labels miss — but only after PII removal,
              dedupe, and bird-specific normalization.
            </p>
          </div>
        </motion.div>

        <div className="mt-14 flex flex-col items-start gap-2 sm:max-w-lg">
          <p className="mb-2 font-mono text-[10px] uppercase tracking-[0.2em] text-[var(--color-muted)]">
            Engineering path
          </p>
          {FLOW.map((step, i) => (
            <motion.div
              key={step.label}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.22 + i * 0.07 }}
              className="w-full"
            >
              <div className="panel ataavi-glow flex items-start gap-3 px-4 py-3">
                <span className="font-mono text-xs text-[var(--color-accent)]">{String(i + 1).padStart(2, "0")}</span>
                <div>
                  <span className="text-sm font-medium text-[var(--color-text)]">{step.label}</span>
                  <p className="text-xs text-[var(--color-muted)]">{step.detail}</p>
                </div>
              </div>
              {i < FLOW.length - 1 ? (
                <div className="flex justify-center py-1 text-[var(--color-muted)]">
                  <ArrowDown className="h-3.5 w-3.5" />
                </div>
              ) : null}
            </motion.div>
          ))}
        </div>
      </div>

      <MarqueeTicker observations={rawSample} />
    </section>
  );
}
