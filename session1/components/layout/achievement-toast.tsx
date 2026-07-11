"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Trophy } from "lucide-react";
import type { Achievement } from "@/lib/achievements";

export function AchievementToast(): React.ReactElement {
  const [toast, setToast] = useState<Achievement | null>(null);

  useEffect(() => {
    const onUnlock = (e: Event): void => {
      const detail = (e as CustomEvent<Achievement>).detail;
      if (detail) setToast(detail);
    };
    window.addEventListener("ntl-achievement", onUnlock);
    return () => window.removeEventListener("ntl-achievement", onUnlock);
  }, []);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 4500);
    return () => clearTimeout(t);
  }, [toast]);

  return (
    <AnimatePresence>
      {toast ? (
        <motion.div
          role="status"
          aria-live="polite"
          initial={{ opacity: 0, y: 24, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 12, scale: 0.95 }}
          className="fixed bottom-5 right-5 z-[100] flex max-w-xs items-center gap-3 rounded-xl border border-[var(--accent-primary)]/25 bg-[var(--background-elevated)] px-4 py-3 shadow-lg"
        >
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[var(--accent-primary)]/10">
            <Trophy className="h-4 w-4 text-[var(--accent-primary)]" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-[var(--text-primary)]">
              Achievement unlocked
            </p>
            <p className="truncate text-xs text-[var(--text-muted)]">{toast.title}</p>
          </div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
