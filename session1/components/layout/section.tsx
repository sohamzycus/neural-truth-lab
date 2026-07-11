"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { cn } from "@/lib/utils";
import { sectionReveal } from "@/animations/variants";

interface SectionProps {
  id?: string;
  title?: string;
  eyebrow?: string;
  children: React.ReactNode;
  className?: string;
}

export function Section({
  id,
  title,
  eyebrow,
  children,
  className,
}: SectionProps): React.ReactElement {
  const ref = useRef<HTMLElement>(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });

  return (
    <section id={id} ref={ref} className={cn("py-16 md:py-24", className)}>
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {(eyebrow || title) && (
          <motion.header
            className="mb-8 md:mb-12"
            variants={sectionReveal}
            initial="hidden"
            animate={inView ? "visible" : "hidden"}
          >
            {eyebrow ? (
              <p className="mb-2 font-mono text-xs font-medium uppercase tracking-widest text-[var(--text-muted)]">
                {eyebrow}
              </p>
            ) : null}
            {title ? (
              <h2 className="font-display text-2xl font-semibold tracking-tight text-[var(--text-primary)] md:text-3xl">
                {title}
              </h2>
            ) : null}
          </motion.header>
        )}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 16 }}
          transition={{ duration: 0.45, delay: 0.1 }}
        >
          {children}
        </motion.div>
      </div>
    </section>
  );
}
