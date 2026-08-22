import { motion } from "framer-motion";
import { PRESSURE_ERAS } from "../../data/chronology";

const PRESSURES = ["QUALITY", "COMPUTE", "MEMORY", "CONTEXT", "LATENCY"] as const;

export function PressureBar({ year }: { year: number }) {
  const era = Object.entries(PRESSURE_ERAS)
    .map(([y, p]) => ({ year: Number(y), pressures: p }))
    .filter((e) => e.year <= year)
    .at(-1);

  const active = new Set(era?.pressures ?? ["QUALITY"]);

  return (
    <div className="panel p-4" aria-label={`Optimization pressures around ${year}`}>
      <p className="mb-3 text-xs font-medium uppercase tracking-widest text-muted">
        What did we actually optimize? · ~{year}
      </p>
      <div className="flex flex-wrap gap-2">
        {PRESSURES.map((p) => {
          const on = active.has(p) || era?.pressures.some((ap) => ap.includes(p.split(" ")[0]));
          return (
            <motion.span
              key={p}
              layout
              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                on
                  ? "bg-cyan/20 text-cyan ring-1 ring-cyan/40"
                  : "bg-white/5 text-muted"
              }`}
            >
              {p}
            </motion.span>
          );
        })}
      </div>
    </div>
  );
}
