const USPS = [
  {
    n: "01",
    title: "Spec-driven quant pipeline",
    body: "specs → Python → derive_all.py → JSON. Change a signal, regenerate — the web never invents numbers.",
    color: "var(--color-indigo)",
    icon: "⚙",
  },
  {
    n: "02",
    title: "Fertility = budget line item",
    body: "India-first 128k cuts Indic fertility 1.46 → 1.14 — $13.5M/yr TCO savings at Year-2 scale.",
    color: "var(--color-saffron)",
    icon: "₹",
  },
  {
    n: "03",
    title: "Anti-population weighting",
    body: "Hindi 39.2% census → 17.9% MCDA. Dravidian languages gain +11pp on deployment demand.",
    color: "var(--color-leaf)",
    icon: "⚖",
  },
  {
    n: "04",
    title: "Stress-testable decisions",
    body: "12 decision matrices with adjustable weights — prove tokenizer & alignment choices survive.",
    color: "var(--color-indigo)",
    icon: "◈",
  },
  {
    n: "05",
    title: "Pyramid eval gates",
    body: "5 original scorecards gate L1→L3 release — not benchmark-chasing.",
    color: "var(--color-saffron)",
    icon: "▲",
  },
  {
    n: "06",
    title: "Session2 → Session3 arc",
    body: "SamaBPE fertility work closes the loop: subword design → $100M deployment economics.",
    color: "var(--color-leaf)",
    icon: "∞",
  },
];

export function UspSection() {
  return (
    <section className="card card-glow relative overflow-hidden p-6 md:p-8">
      <span className="script-watermark right-2 top-0 font-devanagari">भारत</span>
      <div className="relative">
        <p className="text-[10px] font-bold uppercase tracking-[0.28em] text-[var(--color-saffron)]">
          Why this is not a blog post
        </p>
        <h2 className="font-display mt-2 text-2xl font-bold md:text-3xl">
          Six reasons this submission is different
        </h2>
        <p className="mt-2 max-w-xl text-sm text-[var(--muted)]">
          Quantitative models, not prose. Every claim traces to a Python derivation.
        </p>
      </div>
      <div className="relative mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {USPS.map((u) => (
          <div
            key={u.n}
            className="usp-card group rounded-xl border border-[var(--border)] bg-white/85 p-4"
            style={{ borderTopWidth: 3, borderTopColor: u.color }}
          >
            <div className="flex items-start justify-between gap-2">
              <span className="font-mono text-xs font-bold" style={{ color: u.color }}>
                {u.n}
              </span>
              <span
                className="flex h-7 w-7 items-center justify-center rounded-lg text-sm"
                style={{ backgroundColor: `color-mix(in srgb, ${u.color} 12%, white)` }}
              >
                {u.icon}
              </span>
            </div>
            <h3 className="mt-2 text-sm font-bold">{u.title}</h3>
            <p className="mt-2 text-xs leading-relaxed text-[var(--muted)]">{u.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
