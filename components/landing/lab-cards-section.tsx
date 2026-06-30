"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { LABS } from "@/lib/constants";
import { cn } from "@/lib/utils";
import { cardsContainer, sectionReveal } from "@/animations/variants";
import { LabCard } from "@/components/landing/lab-card";

interface LabCardsSectionProps {
  eyebrow: string;
  title: string;
  description?: string;
  columns?: "four" | "two";
  className?: string;
}

export function LabCardsSection({
  eyebrow,
  title,
  description,
  columns = "four",
  className,
}: LabCardsSectionProps): React.ReactElement {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section
      ref={ref}
      className={className}
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <motion.header
          className="mb-8 md:mb-12"
          variants={sectionReveal}
          initial="hidden"
          animate={inView ? "visible" : "hidden"}
        >
          <p className="mb-2 text-xs font-medium uppercase tracking-widest text-[var(--text-muted)]">
            {eyebrow}
          </p>
          <h2 className="text-2xl font-semibold tracking-tight text-[var(--text-primary)] md:text-3xl">
            {title}
          </h2>
          {description && (
            <p className="mt-4 max-w-2xl text-[var(--text-secondary)]">
              {description}
            </p>
          )}
        </motion.header>

        <motion.div
          className={cn(
            "grid gap-6",
            columns === "four"
              ? "sm:grid-cols-2 lg:grid-cols-4"
              : "sm:grid-cols-2"
          )}
          variants={cardsContainer}
          initial="hidden"
          animate={inView ? "visible" : "hidden"}
        >
          {LABS.map((lab) => (
            <LabCard key={lab.id} lab={lab} />
          ))}
        </motion.div>
      </div>
    </section>
  );
}
