import { useEffect, useRef, useState } from "react";
import type { SurgeryMetrics } from "../../types";
import { Section } from "../shell/AppShell";
import { MetricCounter } from "../ui";

function useCountUp(target: number, enabled: boolean, decimals = 0) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    if (!enabled) return;
    let raf = 0;
    const start = performance.now();
    const dur = 900;
    const tick = (t: number) => {
      const p = Math.min(1, (t - start) / dur);
      const eased = 1 - Math.pow(1 - p, 3);
      setValue(target * eased);
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, enabled]);
  return decimals > 0 ? value.toFixed(decimals) : Math.round(value).toLocaleString();
}

function AnimatedMetric({
  label,
  target,
  enabled,
  decimals,
}: {
  label: string;
  target: number;
  enabled: boolean;
  decimals?: number;
}) {
  const display = useCountUp(target, enabled, decimals);
  return <MetricCounter value={display} label={label} />;
}

export function SurgerySection({ metrics }: { metrics: SurgeryMetrics }) {
  const ref = useRef<HTMLDivElement>(null);
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([e]) => {
        if (e?.isIntersecting) setEnabled(true);
      },
      { threshold: 0.25 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  const rows: { key: keyof SurgeryMetrics; label: string; decimals?: number }[] = [
    { key: "observations", label: "Observations" },
    { key: "languages", label: "Languages" },
    { key: "species", label: "Species" },
    { key: "duplicateClusters", label: "Duplicate clusters" },
    { key: "piiRemoved", label: "PII removed" },
    { key: "unicodeFixes", label: "Unicode fixes" },
    { key: "gpsMasked", label: "GPS masked" },
    { key: "scientificNamesNormalized", label: "Scientific names normalized" },
    { key: "averageQualityScore", label: "Average quality score", decimals: 2 },
  ];

  return (
    <Section
      id="surgery"
      eyebrow="Run metrics"
      title="Corpus Surgery Dashboard"
      subtitle="Animated counters from the cleaning run — curated metrics for the demo corpus."
    >
      <div ref={ref} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {rows.map((r) => (
          <AnimatedMetric
            key={r.key}
            label={r.label}
            target={Number(metrics[r.key])}
            enabled={enabled}
            decimals={r.decimals}
          />
        ))}
      </div>
    </Section>
  );
}
