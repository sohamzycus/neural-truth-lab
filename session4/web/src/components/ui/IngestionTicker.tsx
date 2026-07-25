import { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Radio } from "lucide-react";
import type { RawObservation } from "../../types";

export function IngestionTicker({
  observations,
  totalCorpus,
  label = "Live ingestion stream",
}: {
  observations: RawObservation[];
  totalCorpus: number;
  label?: string;
}) {
  const [idx, setIdx] = useState(0);
  const pool = useMemo(() => observations.slice(0, 200), [observations]);

  useEffect(() => {
    if (!pool.length) return;
    const id = setInterval(() => setIdx((i) => (i + 1) % pool.length), 2800);
    return () => clearInterval(id);
  }, [pool.length]);

  const current = pool[idx];
  if (!current) return null;

  const corpusIdx = current.meta?.corpusIndex ?? idx;

  return (
    <div className="overflow-hidden rounded-xl border border-[var(--color-accent)]/25 bg-[var(--color-accent)]/5">
      <div className="flex items-center gap-2 border-b border-[var(--color-accent)]/15 px-4 py-2">
        <span className="relative flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[var(--color-ok)] opacity-60" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-[var(--color-ok)]" />
        </span>
        <Radio className="h-3.5 w-3.5 text-[var(--color-accent)]" />
        <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-[var(--color-accent)]">{label}</span>
        <span className="ml-auto font-mono text-[10px] text-[var(--color-muted)]">
          #{corpusIdx.toLocaleString()} / {totalCorpus.toLocaleString()}
        </span>
      </div>
      <div className="relative min-h-[3.25rem] px-4 py-3">
        <AnimatePresence mode="wait">
          <motion.div
            key={current.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.35 }}
            className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm"
          >
            <span className="font-medium text-[var(--color-text)]">{current.meta?.species ?? current.title}</span>
            <span className="text-xs text-[var(--color-accent)]">{current.meta?.location}</span>
            <span className="max-w-xl truncate text-xs text-[var(--color-muted)]">{current.text}</span>
            {current.issues.slice(0, 2).map((issue) => (
              <span
                key={issue}
                className="rounded border border-[var(--color-warn)]/40 px-1.5 py-0.5 font-mono text-[9px] uppercase text-[var(--color-warn)]"
              >
                {issue}
              </span>
            ))}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

export function MarqueeTicker({ observations }: { observations: RawObservation[] }) {
  const items = useMemo(
    () =>
      observations
        .slice(0, 40)
        .map((o) => `${o.meta?.species ?? o.title} · ${o.meta?.location ?? "—"} · ${o.issues[0]}`)
        .join("   ◆   "),
    [observations],
  );

  return (
    <div className="relative mt-8 overflow-hidden border-y border-[var(--color-border)] bg-black/20 py-2.5">
      <div className="ticker-track whitespace-nowrap font-mono text-[11px] text-[var(--color-muted)]">
        <span>{items}</span>
        <span aria-hidden>{items}</span>
      </div>
    </div>
  );
}
