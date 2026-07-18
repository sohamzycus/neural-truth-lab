import { useState } from "react";

type Node = { id: string; label: string; x: number; y: number; accent?: boolean };

function PipelineSvg({
  title,
  nodes,
  edges,
  width = 720,
  height = 200,
}: {
  title: string;
  nodes: Node[];
  edges: [string, string][];
  width?: number;
  height?: number;
}) {
  const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
  return (
    <figure className="card overflow-hidden">
      <figcaption className="border-b border-[var(--border)] bg-[var(--color-parchment)]/80 px-4 py-2.5 text-xs font-bold uppercase tracking-widest text-[var(--color-indigo)]">
        {title}
      </figcaption>
      <svg viewBox={`0 0 ${width} ${height}`} className="pipeline-svg w-full bg-white/90" role="img" aria-label={title}>
        <defs>
          <marker id="arrowhead" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
            <polygon points="0 0, 8 3, 0 6" fill="#2c3e6b" />
          </marker>
        </defs>
        {edges.map(([a, b], i) => {
          const A = byId[a];
          const B = byId[b];
          if (!A || !B) return null;
          return (
            <line key={i} x1={A.x + 56} y1={A.y + 18} x2={B.x} y2={B.y + 18} className="arrow" />
          );
        })}
        {nodes.map((n) => (
          <g key={n.id}>
            <rect x={n.x} y={n.y} width={112} height={36} rx={8} className={n.accent ? "node-accent" : "node"} />
            <text x={n.x + 56} y={n.y + 22} textAnchor="middle" fontWeight="600">
              {n.label}
            </text>
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
    nodes: [
      { id: "a", label: "Web + Repos", x: 8, y: 80 },
      { id: "b", label: "License filter", x: 140, y: 80 },
      { id: "c", label: "MCDA mix", x: 272, y: 80, accent: true },
      { id: "d", label: "1.2T pretrain", x: 404, y: 80 },
      { id: "e", label: "Shard + clean", x: 536, y: 80 },
    ] as Node[],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"]] as [string, string][],
  },
  {
    id: "training",
    title: "Training Pipeline",
    nodes: [
      { id: "a", label: "Pretrain 1.2T", x: 8, y: 80 },
      { id: "b", label: "SFT 40B", x: 128, y: 80 },
      { id: "c", label: "DPO 200M", x: 248, y: 80, accent: true },
      { id: "d", label: "Safety RLHF", x: 368, y: 80 },
      { id: "e", label: "Pyramid eval", x: 488, y: 80 },
      { id: "f", label: "Export", x: 608, y: 80 },
    ] as Node[],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"], ["e", "f"]] as [string, string][],
    width: 760,
  },
  {
    id: "cleaning",
    title: "Cleaning Pipeline",
    nodes: [
      { id: "a", label: "L1 Lang ID", x: 8, y: 30 },
      { id: "b", label: "L2 Dedup", x: 128, y: 30 },
      { id: "c", label: "L3 PII", x: 248, y: 30 },
      { id: "d", label: "L4 Quality", x: 368, y: 30 },
      { id: "e", label: "L5 OCR", x: 488, y: 30 },
      { id: "f", label: "L6 Provenance", x: 580, y: 30, accent: true },
    ] as Node[],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"], ["e", "f"]] as [string, string][],
    width: 760,
    height: 100,
  },
  {
    id: "tokenizer",
    title: "Tokenizer Optimization",
    nodes: [
      { id: "a", label: "Unicode", x: 20, y: 80 },
      { id: "b", label: "Exposure", x: 160, y: 80 },
      { id: "c", label: "Unigram+BPE", x: 300, y: 80, accent: true },
      { id: "d", label: "128k vocab", x: 440, y: 80 },
      { id: "e", label: "Fertility ↓", x: 580, y: 80 },
    ] as Node[],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"]] as [string, string][],
    width: 760,
  },
  {
    id: "eval",
    title: "Evaluation Pyramid",
    nodes: [
      { id: "a", label: "L4 Benchmarks", x: 280, y: 20 },
      { id: "b", label: "L3 Agents", x: 280, y: 70 },
      { id: "c", label: "L2 Indic", x: 280, y: 120, accent: true },
      { id: "d", label: "L1 Safety", x: 280, y: 170 },
    ] as Node[],
    edges: [["d", "c"], ["c", "b"], ["b", "a"]] as [string, string][],
    width: 720,
    height: 220,
  },
  {
    id: "flywheel",
    title: "Data Flywheel",
    nodes: [
      { id: "a", label: "Deploy", x: 40, y: 80 },
      { id: "b", label: "Logs", x: 180, y: 80 },
      { id: "c", label: "Filter", x: 320, y: 80 },
      { id: "d", label: "SFT + DPO", x: 460, y: 80, accent: true },
      { id: "e", label: "Redeploy", x: 600, y: 80 },
    ] as Node[],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"]] as [string, string][],
    width: 760,
  },
];

export function DiagramGallery({ featuredOnly = false }: { featuredOnly?: boolean }) {
  if (featuredOnly) {
    const d = DIAGRAMS[1];
    return <PipelineSvg title={d.title} nodes={d.nodes} edges={d.edges} width={d.width} />;
  }
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {DIAGRAMS.map((d) => (
        <PipelineSvg key={d.id} title={d.title} nodes={d.nodes} edges={d.edges} width={d.width} height={d.height} />
      ))}
    </div>
  );
}

export function DiagramTabs() {
  const [active, setActive] = useState(0);
  const d = DIAGRAMS[active];
  return (
    <section className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {DIAGRAMS.map((diag, i) => (
          <button
            key={diag.id}
            type="button"
            onClick={() => setActive(i)}
            className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${
              i === active
                ? "bg-[var(--color-indigo)] text-white shadow-md"
                : "card text-[var(--muted)] hover:text-[var(--color-ink)]"
            }`}
          >
            {diag.title}
          </button>
        ))}
      </div>
      <PipelineSvg title={d.title} nodes={d.nodes} edges={d.edges} width={d.width} height={d.height} />
    </section>
  );
}
