import type { ReactNode } from "react";
import type { InferenceCosts, Scorecards, TrainingBudget } from "../types";

function Panel({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
}) {
  return (
    <figure className="infographic-panel">
      <figcaption className="infographic-panel__head">
        <p className="infographic-panel__title">{title}</p>
        {subtitle && <p className="infographic-panel__sub">{subtitle}</p>}
      </figcaption>
      <div className="infographic-panel__body">{children}</div>
    </figure>
  );
}

const STACK_LAYERS = [
  { label: "Deployment reality", detail: "Mumbai GPUs · 800ms p50 · INT4", tone: "indigo" as const },
  { label: "Tokenizer (L4)", detail: "128k India-first · fertility 1.14", tone: "saffron" as const },
  { label: "Capabilities (L2–L3)", detail: "Gov/edu · code-switch · agents", tone: "leaf" as const },
  { label: "Ship gates (L1)", detail: "Safety + regional policy first", tone: "ink" as const },
];

function ConstraintStack() {
  return (
    <Panel title="Deployable Intelligence stack" subtitle="Constraints drive design — not benchmark leaderboards">
      <ul className="info-stack">
        {STACK_LAYERS.map((layer, i) => (
          <li
            key={layer.label}
            className={`info-stack__layer info-stack__layer--${layer.tone}`}
            style={{ width: `${100 - i * 6}%` }}
          >
            <span className="info-stack__label">{layer.label}</span>
            <span className="info-stack__detail">{layer.detail}</span>
          </li>
        ))}
      </ul>
      <p className="info-footnote">Maximize useful work per inference rupee</p>
    </Panel>
  );
}

function TcoBars({ inference }: { inference: InferenceCosts }) {
  const baseline = inference.annual_tco_usd_millions["40b_int4_baseline"];
  const savings = inference.india_tokenizer_savings_vs_generic_usd_m;
  const india = baseline - savings;

  const rows = [
    { label: "Generic tokenizer", value: baseline, pct: 100, tone: "muted" as const },
    {
      label: "India-first 128k",
      value: india,
      pct: (india / baseline) * 100,
      tone: "india" as const,
      delta: savings,
    },
  ];

  return (
    <Panel title="Year-2 inference TCO" subtitle="Tokenizer is a permanent budget line item">
      <div className="info-bars">
        {rows.map((row) => (
          <div key={row.label} className="info-bars__row">
            <div className="info-bars__meta">
              <span className="info-bars__label">{row.label}</span>
              <span className="info-bars__value">${row.value.toFixed(1)}M/yr</span>
            </div>
            <div className="info-bars__track">
              <div
                className={`info-bars__fill info-bars__fill--${row.tone}`}
                style={{ width: `${row.pct}%` }}
              />
            </div>
            {row.delta != null && (
              <p className="info-bars__delta">Saves ${row.delta.toFixed(1)}M/yr vs generic</p>
            )}
          </div>
        ))}
      </div>
      <p className="info-footnote">22% TCO reduction at 30M queries/day · 1.2k tokens/query</p>
    </Panel>
  );
}

function Flywheel() {
  const steps = ["Deploy", "Observe", "Curate", "Retrain"];
  return (
    <Panel title="Data flywheel" subtitle="Production logs close the capability loop">
      <div className="info-flywheel">
        {steps.map((step, i) => (
          <div key={step} className="info-flywheel__step">
            <span className="info-flywheel__node">{step}</span>
            {i < steps.length - 1 && <span className="info-flywheel__arrow" aria-hidden>→</span>}
          </div>
        ))}
        <span className="info-flywheel__loop" aria-hidden>↺</span>
      </div>
      <p className="info-flywheel__center">India production deploy</p>
      <p className="info-footnote">Incident logs → curated SFT/DPO → redeploy</p>
    </Panel>
  );
}

function ShipPyramid({ scorecards }: { scorecards: Scorecards | null }) {
  const gates = (scorecards?.scorecards ?? []).slice(0, 4).map((g) => ({
    short: g.name.replace(/ score$/i, "").replace("Government/Education", "Gov/edu"),
    gate: g.gate,
  }));

  const fallback = [
    { short: "Indic faithfulness", gate: 0.82 },
    { short: "Code-switch", gate: 0.75 },
    { short: "Gov/edu readiness", gate: 0.78 },
    { short: "Agent recovery", gate: 0.7 },
  ];

  const items = gates.length ? gates : fallback;

  const tiers = [
    { level: "L4", label: "Benchmarks", width: 40 },
    { level: "L3", label: "Agents", width: 55 },
    { level: "L2", label: "Indic eval", width: 70 },
    { level: "L1", label: "Safety · blocks ship", width: 85, accent: true },
  ];

  return (
    <Panel title="Release gate pyramid" subtitle="Ship on deployment scorecards — benchmarks inform only">
      <div className="info-pyramid">
        {tiers.map((t) => (
          <div
            key={t.level}
            className={`info-pyramid__tier ${t.accent ? "info-pyramid__tier--accent" : ""}`}
            style={{ width: `${t.width}%` }}
          >
            <span className="info-pyramid__level">{t.level}</span>
            <span className="info-pyramid__label">{t.label}</span>
          </div>
        ))}
      </div>
      <div className="info-gates">
        {items.map((g) => (
          <div key={g.short} className="info-gates__card">
            <span className="info-gates__name">{g.short}</span>
            <span className="info-gates__gate">≥{g.gate}</span>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function BudgetRing({ budget }: { budget: TrainingBudget }) {
  const segments = [
    { label: "Pretrain", pct: 52, color: "#2c3e6b" },
    { label: "Alignment", pct: 18, color: "#c45c26" },
    { label: "Tokenizer", pct: 8, color: "#2d5a3d" },
    { label: "Eval + safety", pct: 12, color: "#5c5c66" },
    { label: "Reserve", pct: 10, color: "#d4cbb8" },
  ];

  let gradient = "conic-gradient(";
  let cursor = 0;
  segments.forEach((seg, i) => {
    const end = cursor + seg.pct;
    gradient += `${seg.color} ${cursor}% ${end}%`;
    if (i < segments.length - 1) gradient += ", ";
    cursor = end;
  });
  gradient += ")";

  return (
    <Panel title={`$${budget.total_budget_usd_m}M program budget`} subtitle={`${budget.timeline_months} months · one training run`}>
      <div className="info-budget">
        <div className="info-budget__ring" style={{ background: gradient }} aria-hidden>
          <div className="info-budget__hole">
            <span className="info-budget__total">${budget.total_budget_usd_m}M</span>
            <span className="info-budget__hint">total</span>
          </div>
        </div>
        <ul className="infographic-legend">
          {segments.map((seg) => (
            <li key={seg.label}>
              <span className="infographic-legend__swatch" style={{ background: seg.color }} />
              <span className="infographic-legend__label">{seg.label}</span>
              <span className="infographic-legend__pct">{seg.pct}%</span>
            </li>
          ))}
        </ul>
      </div>
    </Panel>
  );
}

export function InfographicPanels({
  budget,
  inference,
  scorecards,
}: {
  budget: TrainingBudget | null;
  inference: InferenceCosts | null;
  scorecards: Scorecards | null;
}) {
  if (!budget || !inference) return null;

  return (
    <section className="space-y-3">
      <div>
        <h2 className="section-title">Key infographics</h2>
        <p className="mb-3 text-sm text-[var(--muted)]">
          Visual anchors for the thesis — complementing the architecture diagrams.
        </p>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <ConstraintStack />
        <TcoBars inference={inference} />
        <Flywheel />
        <ShipPyramid scorecards={scorecards} />
        <div className="lg:col-span-2">
          <BudgetRing budget={budget} />
        </div>
      </div>
    </section>
  );
}
