import { useEffect, useState } from "react";
import { MermaidDiagram } from "./MermaidDiagram";

const DIAGRAM_META: { file: string; title: string }[] = [
  { file: "data-pipeline", title: "Data Pipeline" },
  { file: "training-pipeline", title: "Training Pipeline" },
  { file: "cleaning-pipeline", title: "Cleaning Pipeline" },
  { file: "tokenizer-optimization", title: "Tokenizer Optimization" },
  { file: "evaluation-pyramid", title: "Evaluation Pyramid" },
  { file: "failure-feedback-loop", title: "Failure Feedback Loop" },
  { file: "data-flywheel", title: "Data Flywheel" },
  { file: "alignment-pipeline", title: "Alignment Pipeline" },
];

export function DiagramGallery({ compact = false }: { compact?: boolean }) {
  const [diagrams, setDiagrams] = useState<{ title: string; code: string }[]>([]);
  const [active, setActive] = useState(0);

  useEffect(() => {
    Promise.all(
      DIAGRAM_META.map(async ({ file, title }) => {
        const res = await fetch(`/diagrams/${file}.mmd`);
        const code = res.ok ? await res.text() : `flowchart LR\n  ERR[Missing ${file}]`;
        return { title, code };
      }),
    ).then(setDiagrams);
  }, []);

  if (diagrams.length === 0) {
    return <p className="text-sm text-[var(--muted)]">Loading architecture diagrams…</p>;
  }

  if (compact) {
    return <MermaidDiagram code={diagrams[active].code} title={diagrams[active].title} />;
  }

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap gap-2">
        {diagrams.map((d, i) => (
          <button
            key={d.title}
            type="button"
            onClick={() => setActive(i)}
            className={`rounded-full px-3 py-1.5 text-xs font-medium transition ${
              active === i
                ? "bg-[var(--ink)] text-white"
                : "border border-[var(--border)] bg-white text-[var(--muted)] hover:border-[var(--accent)]"
            }`}
          >
            {d.title}
          </button>
        ))}
      </div>

      <MermaidDiagram code={diagrams[active].code} title={diagrams[active].title} />

      <div className="grid gap-6 lg:grid-cols-2">
        {diagrams.map((d) => (
          <MermaidDiagram key={d.title} code={d.code} title={d.title} />
        ))}
      </div>
    </section>
  );
}
