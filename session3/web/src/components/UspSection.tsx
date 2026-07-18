const USPS = [
  { n: "01", title: "Spec-driven quant pipeline", body: "Python owns every number — web never invents metrics.", color: "var(--color-indigo)" },
  { n: "02", title: "Fertility = budget line item", body: "128k India tokenizer → 22% Year-2 TCO savings.", color: "var(--color-saffron)" },
  { n: "03", title: "Anti-population weighting", body: "Hindi 39% census → 18% MCDA. Dravidian +11pp.", color: "var(--color-leaf)" },
  { n: "04", title: "Stress-testable decisions", body: "12 matrices with adjustable weights.", color: "var(--color-indigo)" },
  { n: "05", title: "Pyramid eval gates", body: "5 scorecards gate L1→L3 release.", color: "var(--color-saffron)" },
  { n: "06", title: "Session2 → Session3 arc", body: "SamaBPE fertility → $100M deployment economics.", color: "var(--color-leaf)" },
];

export function UspSection() {
  return (
    <section className="card p-4 md:p-5">
      <h2 className="section-title">Why this submission is different</h2>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {USPS.map((u) => (
          <div
            key={u.n}
            className="rounded-md border border-[var(--border)] bg-white p-3"
            style={{ borderLeftWidth: 3, borderLeftColor: u.color }}
          >
            <span className="font-mono text-[10px] font-bold" style={{ color: u.color }}>{u.n}</span>
            <h3 className="mt-1 text-sm font-bold">{u.title}</h3>
            <p className="mt-1 text-xs text-[var(--muted)]">{u.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
