import { useState } from "react";

type Node = {
  id: string;
  label: string;
  sub?: string;
  x: number;
  y: number;
  accent?: boolean;
  w?: number;
};

function edgePath(a: Node, b: Node, aw = 120, ah = 44) {
  const x1 = a.x + (a.w ?? aw);
  const y1 = a.y + ah / 2;
  const x2 = b.x;
  const y2 = b.y + ah / 2;
  const mx = (x1 + x2) / 2;
  return `M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}`;
}

function PipelineSvg({
  title,
  subtitle,
  nodes,
  edges,
  width = 760,
  height = 200,
}: {
  title: string;
  subtitle?: string;
  nodes: Node[];
  edges: [string, string][];
  width?: number;
  height?: number;
}) {
  const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
  const nw = 120;
  const nh = 44;

  return (
    <figure className="card card-glow overflow-hidden">
      <figcaption className="flex items-baseline justify-between gap-3 border-b border-[var(--border)] bg-gradient-to-r from-[var(--color-parchment)] to-white px-5 py-3">
        <div>
          <p className="font-display text-sm font-bold tracking-tight text-[var(--color-indigo)]">{title}</p>
          {subtitle && <p className="mt-0.5 text-[10px] text-[var(--muted)]">{subtitle}</p>}
        </div>
        <span className="rounded-full bg-[var(--color-indigo)]/10 px-2 py-0.5 font-mono text-[9px] font-semibold text-[var(--color-indigo)]">
          {nodes.length} stages
        </span>
      </figcaption>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="pipeline-canvas w-full"
        role="img"
        aria-label={title}
      >
        <defs>
          <linearGradient id="nodeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#ffffff" />
            <stop offset="100%" stopColor="#f0ebe0" />
          </linearGradient>
          <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#fff4eb" />
            <stop offset="100%" stopColor="#ffe8d4" />
          </linearGradient>
          <linearGradient id="edgeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#2c3e6b" stopOpacity="0.3" />
            <stop offset="50%" stopColor="#e86f2a" stopOpacity="0.7" />
            <stop offset="100%" stopColor="#2c3e6b" stopOpacity="0.3" />
          </linearGradient>
          <marker id="arrowDot" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
            <circle cx="3" cy="3" r="2.5" fill="#e86f2a" />
          </marker>
        </defs>
        {edges.map(([a, b], i) => {
          const A = byId[a];
          const B = byId[b];
          if (!A || !B) return null;
          return (
            <path
              key={i}
              d={edgePath(A, B, nw, nh)}
              className="pipeline-edge"
              markerEnd="url(#arrowDot)"
            />
          );
        })}
        {nodes.map((n) => (
          <g key={n.id}>
            <rect
              x={n.x}
              y={n.y}
              width={n.w ?? nw}
              height={nh}
              rx={10}
              className={n.accent ? "pipeline-stage-accent" : "pipeline-stage"}
            />
            <text x={n.x + (n.w ?? nw) / 2} y={n.y + (n.sub ? 18 : 26)} textAnchor="middle" className="pipeline-label">
              {n.label}
            </text>
            {n.sub && (
              <text x={n.x + (n.w ?? nw) / 2} y={n.y + 32} textAnchor="middle" className="pipeline-sublabel">
                {n.sub}
              </text>
            )}
          </g>
        ))}
      </svg>
    </figure>
  );
}

const DIAGRAMS = [
  {
    id: "data",
    title: "Data Pipeline",
    subtitle: "Corpus → MCDA mix → 1.2T shards",
    nodes: [
      { id: "a", label: "Web + Repos", sub: "licensed", x: 12, y: 78 },
      { id: "b", label: "License filter", x: 148, y: 78 },
      { id: "c", label: "MCDA mix", sub: "7 factors", x: 284, y: 78, accent: true },
      { id: "d", label: "1.2T pretrain", x: 420, y: 78 },
      { id: "e", label: "Shard + clean", x: 556, y: 78 },
    ] as Node[],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"]] as [string, string][],
  },
  {
    id: "training",
    title: "Training Pipeline",
    subtitle: "Pretrain → alignment → export",
    nodes: [
      { id: "a", label: "Pretrain 1.2T", x: 8, y: 78 },
      { id: "b", label: "SFT 40B", x: 132, y: 78 },
      { id: "c", label: "DPO 200M", sub: "preference", x: 256, y: 78, accent: true },
      { id: "d", label: "Safety RLHF", x: 380, y: 78 },
      { id: "e", label: "Pyramid eval", x: 504, y: 78 },
      { id: "f", label: "Export", x: 628, y: 78 },
    ] as Node[],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"], ["e", "f"]] as [string, string][],
    width: 780,
  },
  {
    id: "cleaning",
    title: "Cleaning Pipeline",
    subtitle: "Six-layer quality gate",
    nodes: [
      { id: "a", label: "L1 Lang ID", x: 8, y: 28 },
      { id: "b", label: "L2 Dedup", x: 132, y: 28 },
      { id: "c", label: "L3 PII", x: 256, y: 28 },
      { id: "d", label: "L4 Quality", x: 380, y: 28 },
      { id: "e", label: "L5 OCR", x: 504, y: 28 },
      { id: "f", label: "L6 Provenance", sub: "audit", x: 600, y: 28, accent: true, w: 130 },
    ] as Node[],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"], ["e", "f"]] as [string, string][],
    width: 780,
    height: 110,
  },
  {
    id: "tokenizer",
    title: "Tokenizer Optimization",
    subtitle: "128k India-first vocab",
    nodes: [
      { id: "a", label: "Unicode", sub: "NFC", x: 20, y: 78 },
      { id: "b", label: "Exposure", x: 156, y: 78 },
      { id: "c", label: "Unigram+BPE", sub: "hybrid", x: 292, y: 78, accent: true },
      { id: "d", label: "128k vocab", x: 428, y: 78 },
      { id: "e", label: "Fertility ↓", sub: "1.46→1.14", x: 564, y: 78 },
    ] as Node[],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"]] as [string, string][],
    width: 780,
  },
  {
    id: "eval",
    title: "Evaluation Pyramid",
    subtitle: "L1 safety gates L4 benchmarks",
    nodes: [
      { id: "a", label: "L4 Benchmarks", sub: "MMLU, GSM", x: 300, y: 12 },
      { id: "b", label: "L3 Agents", x: 300, y: 62 },
      { id: "c", label: "L2 Indic", sub: "IN-Eval", x: 300, y: 112, accent: true },
      { id: "d", label: "L1 Safety", sub: "red-team", x: 300, y: 162 },
    ] as Node[],
    edges: [["d", "c"], ["c", "b"], ["b", "a"]] as [string, string][],
    width: 720,
    height: 230,
  },
  {
    id: "flywheel",
    title: "Data Flywheel",
    subtitle: "Deploy → learn → redeploy",
    nodes: [
      { id: "a", label: "Deploy", x: 40, y: 78 },
      { id: "b", label: "Logs", x: 176, y: 78 },
      { id: "c", label: "Filter", x: 312, y: 78 },
      { id: "d", label: "SFT + DPO", sub: "fine-tune", x: 448, y: 78, accent: true },
      { id: "e", label: "Redeploy", x: 584, y: 78 },
    ] as Node[],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"]] as [string, string][],
    width: 780,
  },
  {
    id: "alignment",
    title: "Alignment Stack",
    subtitle: "Constitutional + regional safety",
    nodes: [
      { id: "a", label: "Base model", x: 12, y: 78 },
      { id: "b", label: "SFT", sub: "IN-culture", x: 148, y: 78 },
      { id: "c", label: "DPO", x: 284, y: 78, accent: true },
      { id: "d", label: "Safety RLHF", sub: "14 langs", x: 420, y: 78 },
      { id: "e", label: "Gate L1–L3", x: 556, y: 78 },
    ] as Node[],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"]] as [string, string][],
    width: 780,
  },
  {
    id: "failure",
    title: "Failure Feedback Loop",
    subtitle: "Production incidents → training",
    nodes: [
      { id: "a", label: "Incident", x: 40, y: 78 },
      { id: "b", label: "Triage", x: 176, y: 78 },
      { id: "c", label: "Root cause", sub: "taxonomy", x: 312, y: 78, accent: true },
      { id: "d", label: "Data patch", x: 448, y: 78 },
      { id: "e", label: "Retrain", x: 584, y: 78 },
    ] as Node[],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"], ["e", "a"]] as [string, string][],
    width: 780,
  },
];

export function DiagramGallery({ featuredOnly = false }: { featuredOnly?: boolean }) {
  if (featuredOnly) {
    const d = DIAGRAMS[1];
    return <PipelineSvg title={d.title} subtitle={d.subtitle} nodes={d.nodes} edges={d.edges} width={d.width} height={d.height} />;
  }
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {DIAGRAMS.map((d) => (
        <PipelineSvg
          key={d.id}
          title={d.title}
          subtitle={d.subtitle}
          nodes={d.nodes}
          edges={d.edges}
          width={d.width}
          height={d.height}
        />
      ))}
    </div>
  );
}

export function DiagramTabs() {
  const [active, setActive] = useState(0);
  const d = DIAGRAMS[active];
  return (
    <section className="space-y-5">
      <div className="flex flex-wrap gap-2">
        {DIAGRAMS.map((diag, i) => (
          <button
            key={diag.id}
            type="button"
            onClick={() => setActive(i)}
            className={`rounded-full px-3.5 py-2 text-xs font-semibold transition ${
              i === active ? "diagram-tab-active" : "card text-[var(--muted)] hover:text-[var(--color-ink)]"
            }`}
          >
            {diag.title}
          </button>
        ))}
      </div>
      <PipelineSvg title={d.title} subtitle={d.subtitle} nodes={d.nodes} edges={d.edges} width={d.width} height={d.height} />
    </section>
  );
}
