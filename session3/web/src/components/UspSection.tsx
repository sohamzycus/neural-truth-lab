const LAWS = [
  { id: "L1", text: "Capabilities define data—not the reverse." },
  { id: "L2", text: "Ship on deployment gates; benchmarks inform only." },
  { id: "L3", text: "Inference tokens are deployment currency." },
  { id: "L4", text: "Tokenizer is permanent infrastructure." },
  { id: "L5", text: "Unmeasured capability is uncommitted." },
];

const KPIS = [
  { label: "Fertility", value: "1.14" },
  { label: "Year-2 TCO", value: "$19M" },
  { label: "Budget", value: "$100M" },
  { label: "Gov gate", value: "≥0.78" },
];

export function UspSection() {
  return (
    <section className="hero-panel">
      <p className="hero-panel__eyebrow">Deployable Intelligence</p>
      <h2 className="hero-panel__title">
        Useful work per rupee of inference—not MMLU rank.
      </h2>
      <p className="hero-panel__sub">
        IndiaOne co-designs tokenizer, capabilities, and ship gates for Mumbai GPUs under bandwidth and code-switch constraints.
      </p>
      <div className="hero-panel__kpis">
        {KPIS.map((k) => (
          <div key={k.label} className="kpi-card">
            <span className="kpi-card__value">{k.value}</span>
            <span className="kpi-card__label">{k.label}</span>
          </div>
        ))}
      </div>
      <div className="hero-panel__laws">
        {LAWS.map((l) => (
          <div key={l.id} className="law-card">
            <span className="law-card__id">{l.id}</span>
            <span className="law-card__text">{l.text}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
