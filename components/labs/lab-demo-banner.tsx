"use client";

import { motion } from "framer-motion";
import type { LabId } from "@/lib/constants";
import type { LabDemoContent } from "@/lib/lab-demos";
import { TheoryInfographic } from "@/components/labs/theory-infographic";
import { cn } from "@/lib/utils";

interface LabDemoBannerProps {
  labId: LabId;
  demo: LabDemoContent;
  experiment?: string;
  problem: string;
  solution: string;
  accentClass?: string;
  stats?: React.ReactNode;
  className?: string;
}

export function LabDemoBanner({
  labId,
  demo,
  experiment,
  problem,
  solution,
  accentClass,
  stats,
  className,
}: LabDemoBannerProps): React.ReactElement {
  return (
    <div
      className={cn(
        "rounded-lg border border-[var(--border)] bg-[var(--background-elevated)] shadow-sm",
        className
      )}
    >
      <div className="grid gap-3 p-3 lg:grid-cols-[minmax(140px,180px)_1fr_auto] lg:items-center lg:gap-4">
        <TheoryInfographic labId={labId} className="h-[88px] w-full lg:h-[100px]" />

        <div className="min-w-0">
          <p
            className={cn(
              "text-[10px] font-bold uppercase tracking-widest",
              accentClass ?? "text-[var(--accent-primary)]"
            )}
          >
            {experiment ? `${experiment} · ` : ""}
            {demo.sessionConcept}
          </p>
          <p className="mt-0.5 text-sm font-semibold leading-snug text-[var(--text-primary)]">
            {problem}
          </p>
          <p className="mt-0.5 text-xs leading-snug text-[var(--text-secondary)]">
            {solution}
          </p>
          <div className="mt-1.5 flex flex-wrap items-center gap-1.5 text-[10px] font-medium uppercase">
            <span className="rounded border border-[var(--border)] bg-[var(--surface)] px-1.5 py-0.5 text-[var(--text-muted)]">
              {demo.beforeLabel}
            </span>
            <span className="text-[var(--text-muted)]">→</span>
            <span
              className={cn(
                "rounded border px-1.5 py-0.5",
                accentClass
                  ? `${accentClass} border-current/20 bg-current/5`
                  : "border-[var(--accent-primary)]/20 bg-[var(--accent-primary)]/5 text-[var(--accent-primary)]"
              )}
            >
              {demo.afterLabel}
            </span>
          </div>
        </div>

        {stats ? (
          <div className="flex flex-wrap gap-1.5 lg:justify-end">{stats}</div>
        ) : null}
      </div>

      <div className="border-t border-[var(--border)] px-3 py-2">
        <ul className="grid gap-1 sm:grid-cols-3">
          {demo.watchFor.map((item, i) => (
            <motion.li
              key={item}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
              className="flex gap-1.5 text-[11px] leading-snug text-[var(--text-secondary)]"
            >
              <span className={cn("shrink-0 font-bold", accentClass ?? "text-[var(--accent-primary)]")}>
                {i + 1}.
              </span>
              {item}
            </motion.li>
          ))}
        </ul>
      </div>
    </div>
  );
}
