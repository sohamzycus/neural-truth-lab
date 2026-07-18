const USPS = [
  {
    n: "01",
    title: "Spec-driven quant pipeline",
    body: "specs → Python → derive_all.py → JSON. Change a signal, regenerate — the web never invents numbers.",
    color: "var(--color-indigo)",
  },
  {
    n: "02",
    title: "Fertility = budget line item",
    body: "India-first 128k cuts Indic fertility 1.46 → 1.14 — $13.5M/yr TCO savings at Year-2 scale.",
    color: "var(--color-saffron)",
  },
  {
    n: "03",
    title: "Anti-population weighting",
    body: "Hindi 39.2% census → 17.9% MCDA. Dravidian languages gain +11pp on deployment demand.",
    color: "var(--color-leaf)",
  },
  {
    n: "04",
    title: "Stress-testable decisions",
    body: "12 decision matrices with adjustable weights — prove tokenizer & alignment choices survive.",
    color: "var(--color-indigo)",
  },
  {
    n: "05",
    title: "Pyramid eval gates",
    body: "5 original scorecards gate L1→L3 release — not benchmark-chasing.",
    color: "var(--color-saffron)",
  },
  {
    n: "06",
    title: "Session2 → Session3 arc",
    body: "SamaBPE fertility work closes the loop: subword design → $100M deployment economics.",
    color: "var(--color-leaf)",
  },
];

export function UspSection() {
  return (
    <section className="card relative overflow-hidden p-6 md:p-8">
      <span className="script-watermark right-4 top-2 font-[family-name:var(--font-serif)]">भारत</span>
      <p className="text-[10px] font-bold uppercase tracking-[0.25em] text-[var(--color-saffron)]">
        Why this is not a blog post
      </p>
      <h2 className="mt-2 font-serif text-2xl font-bold md:text-3xl" style={{ fontFamily: "Instrument Serif, serif" }}>
        Six reasons this submission is different
      </h2>
      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {USPS.map((u) => (
          <div
            key={u.n}
            className="group rounded-xl border border-[var(--border)] bg-white/80 p-4 transition hover:-translate-y-0.5 hover:shadow-lg"
            style={{ borderTopWidth: 3, borderTopColor: u.color }}
          >
            <span className="font-mono text-xs font-bold" style={{ color: u.color }}>
              {u.n}
            </span>
            <h3 className="mt-2 text-sm font-bold">{u.title}</h3>
            <p className="mt-2 text-xs leading-relaxed text-[var(--muted)]">{u.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
