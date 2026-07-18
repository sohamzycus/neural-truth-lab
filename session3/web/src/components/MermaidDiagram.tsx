import { useEffect, useId, useState } from "react";
import mermaid from "mermaid";

let mermaidReady = false;

function ensureMermaid() {
  if (!mermaidReady) {
    mermaid.initialize({
      startOnLoad: false,
      theme: "neutral",
      securityLevel: "loose",
      fontFamily: "IBM Plex Sans, sans-serif",
    });
    mermaidReady = true;
  }
}

export function MermaidDiagram({ code, title }: { code: string; title: string }) {
  const id = useId().replace(/:/g, "");
  const [svg, setSvg] = useState<string>("");
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    ensureMermaid();
    let cancelled = false;
    mermaid
      .render(`mmd-${id}`, code)
      .then(({ svg: s }) => {
        if (!cancelled) setSvg(s);
      })
      .catch((e) => {
        if (!cancelled) setErr(String(e));
      });
    return () => {
      cancelled = true;
    };
  }, [code, id]);

  return (
    <figure className="overflow-hidden rounded-lg border border-[var(--border)] bg-white">
      <figcaption className="border-b border-[var(--border)] bg-[var(--paper)] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-[var(--accent-2)]">
        {title}
      </figcaption>
      <div className="flex min-h-[200px] items-center justify-center overflow-x-auto p-4">
        {err ? (
          <pre className="text-xs text-red-600">{err}</pre>
        ) : svg ? (
          <div dangerouslySetInnerHTML={{ __html: svg }} />
        ) : (
          <span className="text-sm text-[var(--muted)]">Rendering diagram…</span>
        )}
      </div>
    </figure>
  );
}
