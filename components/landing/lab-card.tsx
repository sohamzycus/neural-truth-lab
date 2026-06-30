"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Zap, Layers, Sparkles, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";
import type { LabId } from "@/lib/constants";
import { cardItem } from "@/animations/variants";

const ICONS: Record<LabId, React.ComponentType<{ className?: string }>> = {
  activations: Zap,
  depth: Layers,
  embeddings: Sparkles,
  generalization: TrendingUp,
};

const GLOW: Record<LabId, string> = {
  activations: "rgba(249, 115, 22, 0.25)",
  depth: "rgba(6, 182, 212, 0.25)",
  embeddings: "rgba(168, 85, 247, 0.25)",
  generalization: "rgba(16, 185, 129, 0.25)",
};

interface LabCardLab {
  id: LabId;
  number: number;
  title: string;
  description: string;
  href: string;
  accentClass: string;
  borderClass: string;
}

interface LabCardProps {
  lab: LabCardLab;
}

export function LabCard({ lab }: LabCardProps): React.ReactElement {
  const Icon = ICONS[lab.id];

  return (
    <motion.div variants={cardItem} className="h-full">
      <motion.div
        className="h-full"
        whileHover={{
          y: -4,
          boxShadow: `0 12px 40px ${GLOW[lab.id]}, 0 8px 32px rgba(0,0,0,0.4)`,
        }}
        transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
      >
        <Link
          href={lab.href}
          className={cn(
            "glass-panel group flex h-full flex-col border-l-4 p-6 transition-colors duration-300",
            "hover:border-[var(--border-strong)]",
            lab.borderClass
          )}
        >
          <motion.div
            className={cn(
              "mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--surface)]",
              lab.accentClass
            )}
            whileHover={{ rotate: 5, scale: 1.1 }}
            transition={{ duration: 0.25 }}
          >
            <Icon className="h-5 w-5" />
          </motion.div>
          <p className="text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
            Lab {String(lab.number).padStart(2, "0")}
          </p>
          <h3 className="mt-1 text-lg font-semibold text-[var(--text-primary)]">
            {lab.title}
          </h3>
          <p className="mt-2 flex-1 text-sm leading-relaxed text-[var(--text-secondary)]">
            {lab.description}
          </p>
          <span
            className={cn(
              "mt-4 text-sm font-medium transition-colors group-hover:brightness-125",
              lab.accentClass
            )}
          >
            Open lab →
          </span>
        </Link>
      </motion.div>
    </motion.div>
  );
}
