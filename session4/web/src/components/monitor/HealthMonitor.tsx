import { useCallback, useEffect, useState } from "react";
import { Activity, ChevronDown, ChevronUp, RefreshCw } from "lucide-react";
import { animate, motion, useMotionValue, useTransform } from "framer-motion";
import { computeCorpusHealth, type HealthMetric } from "../../lib/corpusHealth";
import type { CorpusStats, DatasetStats, HealthSyncConfig, RawObservation, SurgeryMetrics } from "../../types";

function Meter({ label, value, invert }: { label: string; value: number; invert?: boolean }) {
  const mv = useMotionValue(value);
  const display = useTransform(mv, (v) => Math.round(v));
  const [text, setText] = useState(String(Math.round(value)));

  useEffect(() => {
    const controls = animate(mv, value, { duration: 0.45, ease: "easeOut" });
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

async function loadJson<T>(path: string): Promise<T> {
  const res = await fetch(`${path}?sync=${Date.now()}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to sync ${path}`);
  return res.json() as Promise<T>;
}

export function HealthMonitor({ config }: { config: HealthSyncConfig }) {
  const [open, setOpen] = useState(true);
  const [metrics, setMetrics] = useState<HealthMetric[]>([]);
  const [syncing, setSyncing] = useState(false);
  const [lastSync, setLastSync] = useState<Date | null>(null);
  const [syncError, setSyncError] = useState<string | null>(null);

  const sync = useCallback(async () => {
    setSyncing(true);
    setSyncError(null);
    try {
      const [surgery, stats, dataset, raw] = await Promise.all([
        loadJson<SurgeryMetrics>("/data/surgery_metrics.json"),
        loadJson<CorpusStats>("/data/corpus_stats.json"),
        loadJson<DatasetStats>("/data/dataset_stats.json"),
        loadJson<RawObservation[]>("/data/raw_observations.json"),
      ]);
      setMetrics(computeCorpusHealth(surgery, stats, dataset, raw));
      setLastSync(new Date());
    } catch (e) {
      setSyncError(e instanceof Error ? e.message : "Sync failed");
    } finally {
      setSyncing(false);
    }
  }, []);

  useEffect(() => {
    sync();
    const id = window.setInterval(sync, config.intervalMs);
    return () => window.clearInterval(id);
  }, [sync, config.intervalMs]);

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
            {metrics.map((m) => (
              <Meter key={m.key} label={m.label} value={m.value} invert={m.invert} />
            ))}
            <div className="flex items-center justify-between gap-2 pt-1">
              <div className="font-mono text-[10px] uppercase tracking-wider text-[var(--color-muted)]">
                <span className={syncing ? "text-[var(--color-accent)]" : "text-[var(--color-ok)]"}>
                  {syncing ? "Syncing" : "Live"}
                </span>
                {" · corpus manifests"}
              </div>
              <button
                type="button"
                onClick={() => sync()}
                disabled={syncing}
                className="rounded p-1 text-[var(--color-muted)] transition hover:text-[var(--color-accent)] disabled:opacity-40"
                aria-label="Sync now"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${syncing ? "animate-spin" : ""}`} />
              </button>
            </div>
            {lastSync ? (
              <div className="font-mono text-[10px] text-[var(--color-muted)]">
                Last sync {lastSync.toLocaleTimeString()}
              </div>
            ) : null}
            {syncError ? <div className="text-[10px] text-[var(--color-danger)]">{syncError}</div> : null}
          </div>
        ) : null}
      </div>
    </div>
  );
}
