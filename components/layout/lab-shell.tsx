"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import { labShellReveal } from "@/animations/variants";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface LabShellProps {
  labNumber: number;
  title: string;
  subtitle: string;
  accentClass?: string;
  children: React.ReactNode;
}

export function LabShell({
  labNumber,
  title,
  subtitle,
  accentClass,
  children,
}: LabShellProps): React.ReactElement {
  return (
    <div className="flex h-[calc(100dvh-4rem)] flex-col overflow-hidden bg-[var(--background)]">
      <motion.div
        initial="hidden"
        animate="visible"
        variants={labShellReveal}
        className="shrink-0 border-b border-[var(--border)] bg-[var(--background-elevated)]"
      >
        <div className="flex items-center gap-2 px-2 py-1.5 sm:px-3">
          <Button variant="ghost" size="sm" className="h-8 shrink-0 px-2" asChild>
            <Link href="/labs">
              <ArrowLeft className="h-4 w-4" />
              <span className="hidden sm:inline">Labs</span>
            </Link>
          </Button>
          <div className="min-w-0 flex-1">
            <p
              className={cn(
                "font-mono text-[10px] font-semibold uppercase tracking-widest leading-none",
                accentClass ?? "text-[var(--text-muted)]"
              )}
            >
              EXP {String(labNumber).padStart(2, "0")}
            </p>
            <h1 className="font-display truncate text-sm font-semibold text-[var(--text-primary)]">
              {title}
            </h1>
          </div>
          <p className="hidden max-w-xs truncate font-mono text-[10px] text-[var(--text-muted)] xl:block">
            {subtitle}
          </p>
        </div>
      </motion.div>
      <div className="min-h-0 flex-1">{children}</div>
    </div>
  );
}
