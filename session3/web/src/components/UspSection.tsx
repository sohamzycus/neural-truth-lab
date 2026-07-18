const USPS = [
  {
    n: "01",
    title: "Spec-driven quant pipeline",
    body: "specs/ → Python models → derive_all.py → JSON. Change a signal, regenerate — the report never invents numbers.",
  },
  {
    n: "02",
    title: "Fertility is a budget line item",
    body: "India-first 128k tokenizer cuts Indic fertility 1.46 → 1.14 tokens/word — $13.5M/yr TCO savings at Year-2 scale.",
  },
  {
    n: "03",
    title: "Anti-population weighting",
    body: "Hindi 39.2% census → 17.9% MCDA. Dravidian languages gain +11pp because deployment demand beats headcount.",
  },
  {
    n: "04",
    title: "Stress-testable decisions",
    body: "12 decision matrices with adjustable criterion weights — prove tokenizer, alignment, and code-mix choices survive perturbation.",
  },
  {
    n: "05",
    title: "Pyramid eval gates",
    body: "5 original scorecards (Indic-Faithfulness, Code-Switch, Gov/Edu, Agent Recovery, Inference Efficiency) gate L1→L3 release.",
  },
  {
    n: "06",
    title: "Session2 → Session3 arc",
    body: "SamaBPE tokenizer fertility work closes the loop: subword design → deployment economics for a $100M India-first 40B.",
  },
];

export function UspSection() {
  return (
    <section className="rounded-lg border border-[var(--border)] bg-white p-6 shadow-sm">
      <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[var(--accent)]">
        Why this is not a blog post
      </p>
      <h2 className="mt-2 font-serif text-2xl font-bold" style={{ fontFamily: "Source Serif 4, serif" }}>
        Six reasons this submission is different
      </h2>
      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {USPS.map((u) => (
          <div
            key={u.n}
            className="rounded border border-[var(--border)] bg-[var(--paper)] p-4"
          >
            <span className="font-mono text-xs font-bold text-[var(--accent-2)]">{u.n}</span>
            <h3 className="mt-1 text-sm font-semibold">{u.title}</h3>
            <p className="mt-2 text-xs leading-relaxed text-[var(--muted)]">{u.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
