import { useEffect, useState } from "react";

type Node = {
  id: string;
  label: string;
  sub?: string;
  x: number;
  y: number;
  accent?: boolean;
  w?: number;
};

type DiagramDef = {
  id: string;
  title: string;
  subtitle?: string;
  nodes: Node[];
  edges: [string, string][];
  width?: number;
  height?: number;
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
  diagram,
  uid,
  expanded = false,
  onExpand,
}: {
  diagram: DiagramDef;
  uid: string;
  expanded?: boolean;
  onExpand?: () => void;
}) {
  const { title, subtitle, nodes, edges, width = 760, height = 200 } = diagram;
  const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
  const nw = 120;
  const nh = 44;
  const scale = expanded ? 1.35 : 1;
  const vbW = width * scale;
  const vbH = height * scale;

  return (
    <figure className="card overflow-hidden">
      <figcaption className="flex items-center justify-between gap-2 border-b border-[var(--border)] bg-[var(--color-parchment)]/60 px-3 py-2">
        <div className="min-w-0">
          <p className="truncate text-sm font-bold text-[var(--color-indigo)]">{title}</p>
          {subtitle && <p className="truncate text-[10px] text-[var(--muted)]">{subtitle}</p>}
        </div>
        {onExpand && (
          <button type="button" className="diagram-expand-btn shrink-0" onClick={onExpand} aria-label={`Expand ${title}`}>
            {expanded ? "Close" : "Expand"}
          </button>
        )}
      </figcaption>
      <svg
        viewBox={`0 0 ${vbW} ${vbH}`}
        className="pipeline-canvas w-full"
        style={{ minHeight: expanded ? 280 : 120 }}
        role="img"
        aria-label={title}
      >
        <defs>
          <marker id={`arrow-${uid}`} markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
            <polygon points="0 0, 6 3, 0 6" fill="#2c3e6b" />
          </marker>
        </defs>
        <g transform={expanded ? `scale(${scale})` : undefined}>
          {edges.map(([a, b], i) => {
            const A = byId[a];
            const B = byId[b];
            if (!A || !B) return null;
            return (
              <path
                key={i}
                d={edgePath(A, B, nw, nh)}
                className="pipeline-edge"
                markerEnd={`url(#arrow-${uid})`}
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
                rx={8}
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
        </g>
      </svg>
    </figure>
  );
}

const DIAGRAMS: DiagramDef[] = [
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
    ],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"]],
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
    ],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"], ["e", "f"]],
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
    ],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"], ["e", "f"]],
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
    ],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"]],
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
    ],
    edges: [["d", "c"], ["c", "b"], ["b", "a"]],
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
    ],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"]],
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
    ],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"]],
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
    ],
    edges: [["a", "b"], ["b", "c"], ["c", "d"], ["d", "e"], ["e", "a"]],
    width: 780,
  },
];

function DiagramModal({ diagram, onClose }: { diagram: DiagramDef; onClose: () => void }) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKey);
    };
  }, [onClose]);

  return (
    <div className="diagram-modal" role="dialog" aria-modal onClick={onClose}>
      <div className="diagram-modal-inner" onClick={(e) => e.stopPropagation()}>
        <PipelineSvg diagram={diagram} uid={`modal-${diagram.id}`} expanded onExpand={onClose} />
      </div>
    </div>
  );
}

export function DiagramGallery({ featuredOnly = false }: { featuredOnly?: boolean }) {
  const [expanded, setExpanded] = useState<DiagramDef | null>(null);
  const list = featuredOnly ? [DIAGRAMS[1]] : DIAGRAMS;

  return (
    <>
      <div className={featuredOnly ? "" : "grid gap-4 lg:grid-cols-2"}>
        {list.map((d) => (
          <PipelineSvg key={d.id} diagram={d} uid={d.id} onExpand={() => setExpanded(d)} />
        ))}
      </div>
      {expanded && <DiagramModal diagram={expanded} onClose={() => setExpanded(null)} />}
    </>
  );
}

export function DiagramTabs() {
  const [active, setActive] = useState(0);
  const [expanded, setExpanded] = useState(false);
  const d = DIAGRAMS[active];

  return (
    <section className="space-y-3">
      <div className="flex flex-wrap gap-1.5">
        {DIAGRAMS.map((diag, i) => (
          <button
            key={diag.id}
            type="button"
            onClick={() => setActive(i)}
            className={`diagram-tab ${i === active ? "diagram-tab-active" : ""}`}
          >
            {diag.title}
          </button>
        ))}
      </div>
      <PipelineSvg diagram={d} uid={`tab-${d.id}`} onExpand={() => setExpanded(true)} />
      {expanded && <DiagramModal diagram={d} onClose={() => setExpanded(false)} />}
    </section>
  );
}
