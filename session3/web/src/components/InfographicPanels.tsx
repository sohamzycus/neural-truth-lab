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

function ConstraintStack() {
  const layers = [
    { label: "Deployment reality", detail: "Mumbai GPUs · 800ms p50 · INT4", tone: "indigo" },
    { label: "Tokenizer (L4)", detail: "128k India-first · fertility 1.14", tone: "saffron" },
    { label: "Capabilities (L2–L3)", detail: "Gov/edu · code-switch · agents", tone: "leaf" },
    { label: "Ship gates (L1)", detail: "Safety + regional policy first", tone: "ink" },
  ] as const;

  return (
    <Panel title="Deployable Intelligence stack" subtitle="Constraints drive design — not benchmark leaderboards">
      <svg viewBox="0 0 360 200" className="infographic-svg" role="img" aria-label="Constraint stack">
        {layers.map((layer, i) => {
          const y = 18 + i * 44;
          const w = 300 - i * 28;
          const x = (360 - w) / 2;
          const fill =
            layer.tone === "saffron"
              ? "#fff7f0"
              : layer.tone === "leaf"
                ? "#f3faf5"
                : layer.tone === "indigo"
                  ? "#eef2fb"
                  : "#f7f3e8";
          const stroke =
            layer.tone === "saffron"
              ? "#c45c26"
              : layer.tone === "leaf"
                ? "#2d5a3d"
                : layer.tone === "indigo"
                  ? "#2c3e6b"
                  : "#1a1410";
          return (
            <g key={layer.label}>
              <rect x={x} y={y} width={w} height={36} rx={8} fill={fill} stroke={stroke} strokeWidth={1.25} opacity={0.95} />
              <text x={x + 12} y={y + 15} className="infographic-label">{layer.label}</text>
              <text x={x + 12} y={y + 28} className="infographic-sublabel">{layer.detail}</text>
            </g>
          );
        })}
        <text x="180" y="192" textAnchor="middle" className="infographic-caption">
          ↑ maximize useful work per inference rupee
        </text>
      </svg>
    </Panel>
  );
}

function TcoBars({ inference }: { inference: InferenceCosts }) {
  const baseline = inference.annual_tco_usd_millions["40b_int4_baseline"];
  const savings = inference.india_tokenizer_savings_vs_generic_usd_m;
  const india = baseline - savings;
  const max = baseline * 1.05;

  const bars = [
    { label: "Generic tokenizer", value: baseline, fill: "#9aa3b8", note: "$64.4M/yr" },
    { label: "India-first 128k", value: india, fill: "#2c3e6b", note: `−$${savings}M/yr` },
  ];

  return (
    <Panel title="Year-2 inference TCO" subtitle="Tokenizer is a permanent budget line item">
      <svg viewBox="0 0 360 200" className="infographic-svg" role="img" aria-label="TCO comparison">
        {bars.map((bar, i) => {
          const barW = (bar.value / max) * 240;
          const y = 48 + i * 56;
          return (
            <g key={bar.label}>
              <text x="16" y={y - 6} className="infographic-label">{bar.label}</text>
              <rect x="16" y={y} width={barW} height={28} rx={6} fill={bar.fill} />
              <text x={16 + barW + 8} y={y + 19} className="infographic-mono">
                ${bar.value.toFixed(1)}M
              </text>
              <text x="16" y={y + 42} className="infographic-sublabel">{bar.note}</text>
            </g>
          );
        })}
        <rect x="16" y="158" width="328" height="1" fill="rgba(26,20,16,0.1)" />
        <text x="180" y="178" textAnchor="middle" className="infographic-caption">
          22% TCO reduction at 30M queries/day · 1.2k tokens/query
        </text>
      </svg>
    </Panel>
  );
}

function ShipPyramid({ scorecards }: { scorecards: Scorecards | null }) {
  const gates = scorecards?.scorecards.slice(0, 4) ?? [
    { name: "Indic faithfulness", gate: 0.82 },
    { name: "Code-switch", gate: 0.75 },
    { name: "Gov/edu readiness", gate: 0.78 },
    { name: "Agent recovery", gate: 0.7 },
  ];

  return (
    <Panel title="Release gate pyramid" subtitle="Ship on deployment scorecards — benchmarks inform only">
      <svg viewBox="0 0 360 220" className="infographic-svg" role="img" aria-label="Ship gate pyramid">
        <polygon points="180,20 300,170 60,170" fill="#eef2fb" stroke="#2c3e6b" strokeWidth="1.5" />
        <line x1="95" y1="130" x2="265" y2="130" stroke="#2c3e6b" strokeWidth="0.75" opacity="0.35" />
        <line x1="120" y1="95" x2="240" y2="95" stroke="#2c3e6b" strokeWidth="0.75" opacity="0.35" />
        <text x="180" y="42" textAnchor="middle" className="infographic-label">L4 · Benchmarks</text>
        <text x="180" y="88" textAnchor="middle" className="infographic-label">L3 · Agents</text>
        <text x="180" y="118" textAnchor="middle" className="infographic-label">L2 · Indic eval</text>
        <text x="180" y="155" textAnchor="middle" className="infographic-sublabel" fill="#c45c26">
          L1 · Safety (blocks ship)
        </text>
        <g transform="translate(16, 182)">
          {gates.map((g, i) => (
            <g key={g.name} transform={`translate(${i * 84}, 0)`}>
              <rect width="76" height="32" rx="6" fill="#fff" stroke="rgba(44,62,107,0.2)" />
              <text x="38" y="13" textAnchor="middle" className="infographic-sublabel">
                {g.name.split(" ")[0]}
              </text>
              <text x="38" y="26" textAnchor="middle" className="infographic-mono">
                ≥{g.gate}
              </text>
            </g>
          ))}
        </g>
      </svg>
    </Panel>
  );
}

function Flywheel() {
  const nodes = [
    { label: "Deploy", angle: -90 },
    { label: "Observe", angle: 0 },
    { label: "Curate", angle: 90 },
    { label: "Retrain", angle: 180 },
  ];
  const cx = 180;
  const cy = 100;
  const r = 62;

  return (
    <Panel title="Data flywheel" subtitle="Production logs close the capability loop">
      <svg viewBox="0 0 360 200" className="infographic-svg" role="img" aria-label="Data flywheel">
        <circle cx={cx} cy={cy} r={r + 18} fill="none" stroke="#c45c26" strokeWidth="1.5" strokeDasharray="6 4" opacity="0.5" />
        <circle cx={cx} cy={cy} r={28} fill="#2c3e6b" />
        <text x={cx} y={cy - 4} textAnchor="middle" fill="#fff" className="infographic-label">
          India
        </text>
        <text x={cx} y={cy + 10} textAnchor="middle" fill="#f7f3e8" className="infographic-sublabel">
          deploy
        </text>
        {nodes.map((n) => {
          const rad = (n.angle * Math.PI) / 180;
          const x = cx + (r + 4) * Math.cos(rad);
          const y = cy + (r + 4) * Math.sin(rad);
          return (
            <g key={n.label}>
              <circle cx={x} cy={y} r={22} fill="#fff7f0" stroke="#c45c26" strokeWidth="1.25" />
              <text x={x} y={y + 4} textAnchor="middle" className="infographic-label">
                {n.label}
              </text>
            </g>
          );
        })}
        <defs>
          <marker id="fly-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
            <polygon points="0 0, 6 3, 0 6" fill="#2c3e6b" />
          </marker>
        </defs>
        <path
          d={`M ${cx} ${cy - r - 18} A ${r + 18} ${r + 18} 0 0 1 ${cx + r + 18} ${cy}`}
          fill="none"
          stroke="#2c3e6b"
          strokeWidth="1.25"
          markerEnd="url(#fly-arrow)"
          opacity="0.6"
        />
      </svg>
    </Panel>
  );
}

function BudgetRing({ budget }: { budget: TrainingBudget }) {
  const segments = [
    { label: "Pretrain", pct: 52, color: "#2c3e6b" },
    { label: "Alignment", pct: 18, color: "#c45c26" },
    { label: "Tokenizer", pct: 8, color: "#2d5a3d" },
    { label: "Eval + safety", pct: 12, color: "#5c5c66" },
    { label: "Reserve", pct: 10, color: "#ebe4d4" },
  ];
  const cx = 90;
  const cy = 90;
  const outer = 70;
  const inner = 42;
  let angle = -90;

  return (
    <Panel title={`$${budget.total_budget_usd_m}M program budget`} subtitle={`${budget.timeline_months} months · one training run`}>
      <div className="infographic-split">
        <svg viewBox="0 0 180 180" className="infographic-svg infographic-svg--compact" role="img" aria-label="Budget allocation">
          {segments.map((seg) => {
            const sweep = (seg.pct / 100) * 360;
            const start = angle;
            const end = angle + sweep;
            angle = end;
            const large = sweep > 180 ? 1 : 0;
            const toRad = (deg: number) => (deg * Math.PI) / 180;
            const x1 = cx + outer * Math.cos(toRad(start));
            const y1 = cy + outer * Math.sin(toRad(start));
            const x2 = cx + outer * Math.cos(toRad(end));
            const y2 = cy + outer * Math.sin(toRad(end));
            const xi1 = cx + inner * Math.cos(toRad(end));
            const yi1 = cy + inner * Math.sin(toRad(end));
            const xi2 = cx + inner * Math.cos(toRad(start));
            const yi2 = cy + inner * Math.sin(toRad(start));
            const d = `M ${x1} ${y1} A ${outer} ${outer} 0 ${large} 1 ${x2} ${y2} L ${xi1} ${yi1} A ${inner} ${inner} 0 ${large} 0 ${xi2} ${yi2} Z`;
            return <path key={seg.label} d={d} fill={seg.color} stroke="#fff" strokeWidth="1" />;
          })}
          <text x={cx} y={cy - 2} textAnchor="middle" className="infographic-mono" fontSize="14" fontWeight="700">
            ${budget.total_budget_usd_m}M
          </text>
          <text x={cx} y={cy + 12} textAnchor="middle" className="infographic-sublabel">
            total
          </text>
        </svg>
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
