import { useEffect, useId, useState } from "react";
import mermaid from "mermaid";

let mermaidReady = false;
const svgCache = new Map<string, string>();

function ensureMermaid() {
  if (!mermaidReady) {
    mermaid.initialize({
      startOnLoad: false,
      theme: "base",
      themeVariables: {
        primaryColor: "#ebe4d4",
        primaryTextColor: "#1a1410",
        primaryBorderColor: "#2c3e6b",
        lineColor: "#2c3e6b",
        secondaryColor: "#fff7f0",
        tertiaryColor: "#f7f3e8",
        fontFamily: "Manrope, sans-serif",
      },
      securityLevel: "loose",
    });
    mermaidReady = true;
  }
}

export function MermaidDiagram({ code, title }: { code: string; title: string }) {
  const id = useId().replace(/:/g, "");
  const [svg, setSvg] = useState(() => svgCache.get(code) ?? "");
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    const hit = svgCache.get(code);
    if (hit) {
      setSvg(hit);
      setErr(null);
      return;
    }
    ensureMermaid();
    let cancelled = false;
    mermaid
      .render(`mmd-${id}-${svgCache.size}`, code)
      .then(({ svg: s }) => {
        if (!cancelled) {
          svgCache.set(code, s);
          setSvg(s);
          setErr(null);
        }
      })
      .catch((e) => {
        if (!cancelled) setErr(String(e));
      });
    return () => {
      cancelled = true;
    };
  }, [code, id]);

  return (
    <figure className="mermaid-figure">
      <figcaption className="mermaid-figure__caption">{title}</figcaption>
      <div className="mermaid-figure__body">
        {err ? (
          <pre className="text-xs text-red-600">{err}</pre>
        ) : svg ? (
          <div dangerouslySetInnerHTML={{ __html: svg }} />
        ) : (
          <span className="mermaid-figure__loading">Rendering diagram…</span>
        )}
      </div>
    </figure>
  );
}
