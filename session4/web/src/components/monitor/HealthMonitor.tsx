import { useEffect, useState } from "react";
import { Activity, ChevronDown, ChevronUp } from "lucide-react";
import { animate, motion, useMotionValue, useTransform } from "framer-motion";
import type { HealthBaseline } from "../../types";

function Meter({ label, value, invert }: { label: string; value: number; invert?: boolean }) {
  const mv = useMotionValue(value);
  const display = useTransform(mv, (v) => Math.round(v));
  const [text, setText] = useState(String(Math.round(value)));

  useEffect(() => {
    const controls = animate(mv, value, { duration: 0.6, ease: "easeOut" });
    const unsub = display.on("change", (v) => setText(String(v)));
    return () => {
      controls.stop();
      unsub();
    };
  }, [value, mv, display]);

  const tone = invert
    ? value > 55
      ? "var(--color-danger)"
      : value > 35
        ? "var(--color-warn)"
        : "var(--color-ok)"
    : value > 70
      ? "var(--color-ok)"
      : value > 45
        ? "var(--color-warn)"
        : "var(--color-danger)";

  return (
    <div>
      <div className="mb-1 flex items-center justify-between gap-2 text-[11px]">
        <span className="text-[var(--color-muted)]">{label}</span>
        <span className="font-mono" style={{ color: tone }}>
          {text}
        </span>
      </div>
      <div className="h-1 overflow-hidden rounded-full bg-white/[0.06]">
        <motion.div
          className="h-full rounded-full"
          style={{ background: tone, width: `${Math.min(100, Math.max(0, value))}%` }}
          layout
        />
      </div>
    </div>
  );
}

export function HealthMonitor({ baseline }: { baseline: HealthBaseline }) {
  const [open, setOpen] = useState(true);
  const [values, setValues] = useState(() =>
    Object.fromEntries(baseline.metrics.map((m) => [m.key, m.value])),
  );

  useEffect(() => {
    const id = window.setInterval(() => {
      setValues((prev) => {
        const next = { ...prev };
        for (const m of baseline.metrics) {
          const jitter = (Math.random() * 2 - 1) * m.jitter;
          next[m.key] = Math.min(100, Math.max(0, (prev[m.key] ?? m.value) + jitter));
        }
        return next;
      });
    }, baseline.intervalMs);
    return () => window.clearInterval(id);
  }, [baseline]);

  return (
    <div className="fixed bottom-4 right-4 z-50 w-[min(100%-2rem,20rem)]">
      <div className="panel shadow-2xl shadow-black/40">
        <button
          type="button"
          onClick={() => setOpen((o) => !o)}
          className="flex w-full items-center justify-between gap-2 px-4 py-3 text-left"
        >
          <span className="flex items-center gap-2 text-sm font-medium">
            <Activity className="h-4 w-4 text-[var(--color-accent)]" />
            Corpus Health Monitor
          </span>
          {open ? <ChevronDown className="h-4 w-4 text-[var(--color-muted)]" /> : <ChevronUp className="h-4 w-4 text-[var(--color-muted)]" />}
        </button>
        {open ? (
          <div className="space-y-3 border-t border-[var(--color-border)] px-4 py-3">
            {baseline.metrics.map((m) => (
              <Meter key={m.key} label={m.label} value={values[m.key] ?? m.value} invert={m.invert} />
            ))}
            <div className="pt-1 font-mono text-[10px] uppercase tracking-wider text-[var(--color-muted)]">
              Live · simulated stream
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
