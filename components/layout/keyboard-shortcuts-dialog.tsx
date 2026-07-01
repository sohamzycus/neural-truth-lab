"use client";

import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

const SHORTCUTS = [
  { keys: "?", description: "Open keyboard shortcuts" },
  { keys: "F", description: "Toggle fullscreen (lab pages)" },
  { keys: "Esc", description: "Close panel or exit fullscreen" },
] as const;

interface KeyboardShortcutsDialogProps {
  open: boolean;
  onClose: () => void;
}

export function KeyboardShortcutsDialog({
  open,
  onClose,
}: KeyboardShortcutsDialogProps): React.ReactElement {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog
      ref={ref}
      onClose={onClose}
      className="max-h-[90vh] w-[min(100%,26rem)] max-w-[calc(100vw-2rem)] rounded-xl border border-[var(--border)] bg-[var(--background-elevated)] p-0 text-[var(--text-primary)] shadow-2xl backdrop:bg-stone-900/30 backdrop:backdrop-blur-sm"
      aria-labelledby="shortcuts-title"
    >
      <AnimatePresence>
        {open ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 8 }}
            className="p-5"
          >
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--accent-primary)]/10 text-sm font-bold text-[var(--accent-primary)]">
                ?
              </div>
              <div>
                <h2 id="shortcuts-title" className="text-base font-semibold">
                  Keyboard shortcuts
                </h2>
                <p className="text-xs text-[var(--text-muted)]">
                  Outside text inputs only
                </p>
              </div>
            </div>
            <ul className="mt-4 space-y-2">
              {SHORTCUTS.map((s) => (
                <li
                  key={s.keys}
                  className="flex items-center justify-between gap-3 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-sm"
                >
                  <span className="text-[var(--text-secondary)]">{s.description}</span>
                  <kbd className="rounded border border-[var(--border-strong)] bg-[var(--surface)] px-2 py-0.5 font-mono text-xs font-semibold text-[var(--text-primary)] shadow-sm">
                    {s.keys}
                  </kbd>
                </li>
              ))}
            </ul>
            <button
              type="button"
              onClick={onClose}
              className="mt-4 w-full rounded-lg bg-[var(--accent-primary)] px-4 py-2 text-sm font-medium text-white hover:opacity-90"
            >
              Got it
            </button>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </dialog>
  );
}
