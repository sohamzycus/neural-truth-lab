"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Trophy, X } from "lucide-react";
import { ACHIEVEMENTS } from "@/lib/achievements";
import { useAchievementList } from "@/hooks/useProgress";
import { cn } from "@/lib/utils";

interface AchievementsPanelProps {
  open: boolean;
  onClose: () => void;
}

export function AchievementsPanel({
  open,
  onClose,
}: AchievementsPanelProps): React.ReactElement {
  const { unlocked, all } = useAchievementList();

  return (
    <AnimatePresence>
      {open ? (
        <div
          className="fixed inset-0 z-[90] flex justify-end"
          role="dialog"
          aria-labelledby="achievements-title"
          aria-modal="true"
        >
          <motion.button
            type="button"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-stone-900/25 backdrop-blur-[2px]"
            aria-label="Close achievements"
            onClick={onClose}
          />
          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 28, stiffness: 320 }}
            className="relative z-10 flex h-full w-full max-w-sm flex-col border-l border-[var(--border)] bg-[var(--background-elevated)] shadow-2xl"
          >
            <div className="flex items-center justify-between border-b border-[var(--border)] bg-[var(--surface)] px-5 py-3">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--accent-primary)]/10">
                  <Trophy className="h-4 w-4 text-[var(--accent-primary)]" />
                </div>
                <h2 id="achievements-title" className="font-semibold text-[var(--text-primary)]">
                  Achievements
                </h2>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg p-2 text-[var(--text-muted)] transition-colors hover:bg-[var(--surface-hover)] hover:text-[var(--text-primary)]"
                aria-label="Close achievements panel"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <ul className="flex-1 space-y-2 overflow-y-auto scrollbar-hide p-4">
              {Object.values(all).map((a, i) => {
                const earned = unlocked.includes(a.id);
                return (
                  <motion.li
                    key={a.id}
                    initial={{ opacity: 0, x: 12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className={cn(
                      "rounded-lg border p-3",
                      earned
                        ? "border-[var(--accent-primary)]/30 bg-[var(--accent-primary)]/5"
                        : "border-[var(--border)] bg-[var(--background)] opacity-70"
                    )}
                  >
                    <p className="text-sm font-medium text-[var(--text-primary)]">
                      {a.title}
                    </p>
                    <p className="mt-0.5 text-xs text-[var(--text-muted)]">
                      {a.description}
                    </p>
                  </motion.li>
                );
              })}
            </ul>
            <p className="border-t border-[var(--border)] bg-[var(--surface)] px-5 py-2.5 text-center text-xs text-[var(--text-muted)]">
              {unlocked.length} of {Object.keys(ACHIEVEMENTS).length} unlocked
            </p>
          </motion.aside>
        </div>
      ) : null}
    </AnimatePresence>
  );
}
