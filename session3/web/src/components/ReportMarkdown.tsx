import { Children, isValidElement, memo, type ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { MermaidDiagram } from "./MermaidDiagram";

function childText(node: ReactNode): string {
  if (typeof node === "string") return node;
  if (Array.isArray(node)) return node.map(childText).join("");
  if (isValidElement<{ children?: ReactNode }>(node)) return childText(node.props.children);
  return "";
}

type CalloutKind = "insight" | "decision" | "warning" | "law" | "takeaway" | "exec";

function calloutKind(text: string): CalloutKind | null {
  const t = text.trim();
  if (/^executive summary/i.test(t)) return "exec";
  if (/^key insight/i.test(t)) return "insight";
  if (/^decision/i.test(t)) return "decision";
  if (/^warning/i.test(t)) return "warning";
  if (/^engineering law/i.test(t)) return "law";
  if (/^key takeaway/i.test(t)) return "takeaway";
  return null;
}

const CALLOUT_LABEL: Record<CalloutKind, string> = {
  exec: "Executive Summary",
  insight: "Key Insight",
  decision: "Decision",
  warning: "Warning",
  law: "Engineering Law",
  takeaway: "Key Takeaway",
};

function Callout({ kind, children }: { kind: CalloutKind; children: ReactNode }) {
  return (
    <div className={`callout callout--${kind}`} role="note">
      <p className="callout__label">{CALLOUT_LABEL[kind]}</p>
      <div className="callout__body">{children}</div>
    </div>
  );
}

export const ReportMarkdown = memo(function ReportMarkdown({ markdown }: { markdown: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children }) => <h1 className="report-h1">{children}</h1>,
        h2: ({ children }) => <h2 className="report-h2">{children}</h2>,
        h3: ({ children }) => <h3 className="report-h3">{children}</h3>,
        p: ({ children }) => <p className="report-p">{children}</p>,
        blockquote: ({ children }) => {
          const raw = childText(children).trim();
          const kind = calloutKind(raw);
          if (!kind) return <blockquote className="report-quote">{children}</blockquote>;
          const body = raw.replace(/^[^:]+:\s*/i, "").trim();
          return (
            <Callout kind={kind}>
              <p>{body || children}</p>
            </Callout>
          );
        },
        table: ({ children }) => (
          <div className="table-wrap">
            <table>{children}</table>
          </div>
        ),
        pre: ({ children }) => {
          const child = Children.toArray(children)[0];
          if (isValidElement<{ className?: string; children?: ReactNode }>(child)) {
            const cls = child.props.className ?? "";
            if (cls.includes("language-mermaid")) {
              const code = childText(child.props.children).trim();
              return <MermaidDiagram code={code} title="Diagram" />;
            }
          }
          return <pre className="report-pre">{children}</pre>;
        },
      }}
    >
      {markdown}
    </ReactMarkdown>
  );
});
