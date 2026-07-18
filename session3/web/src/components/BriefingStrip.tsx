import type { TrainingBudget, InferenceCosts, Scorecards } from "../types";

const CHAPTER_JUMP: Record<string, number> = {
  budget: 11,
  mix: 2,
  tco: 10,
  eval: 9,
};

export function BriefingStrip({
  budget,
  inference,
  scorecards,
  onJump,
}: {
  budget: TrainingBudget | null;
  inference: InferenceCosts | null;
  scorecards: Scorecards | null;
  onJump: (chapter: number) => void;
}) {
  if (!budget || !inference) return null;

  const cards = [
    {
      id: "budget",
      label: "Program budget",
      value: `$${budget.total_budget_usd_m}M`,
      detail: `${budget.timeline_months}mo · ${budget.billable_gpu_hours_one_run.toLocaleString()} H100-hr/run`,
      jump: CHAPTER_JUMP.budget,
    },
    {
      id: "mix",
      label: "Pretrain corpus",
      value: "1.2T tokens",
      detail: "82% NL · 12% code · 4% math · 6% synthetic cap",
      jump: CHAPTER_JUMP.mix,
    },
    {
      id: "tco",
      label: "Year-2 TCO",
      value: `$${inference.annual_tco_usd_millions["40b_int4_baseline"]}M → $${(
        inference.annual_tco_usd_millions["40b_int4_baseline"] *
        (1 - 0.22)
      ).toFixed(1)}M`,
      detail: `India tokenizer saves $${inference.india_tokenizer_savings_vs_generic_usd_m}M/yr`,
      jump: CHAPTER_JUMP.tco,
    },
    {
      id: "eval",
      label: "Release gates",
      value: `${scorecards?.scorecards.length ?? 5} scorecards`,
      detail: scorecards?.ship_gate ?? "L1–L3 pyramid gating",
      jump: CHAPTER_JUMP.eval,
    },
  ];

  return (
    <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((c) => (
        <button
          key={c.id}
          type="button"
          onClick={() => onJump(c.jump)}
          className="card p-4 text-left transition hover:-translate-y-0.5 hover:border-[var(--color-saffron)] hover:shadow-md"
        >
          <p className="text-[10px] font-medium uppercase tracking-widest text-[var(--muted)]">
            {c.label}
          </p>
          <p className="mt-1 font-mono text-lg font-semibold tabular-nums">{c.value}</p>
          <p className="mt-1 text-xs text-[var(--muted)]">{c.detail}</p>
        </button>
      ))}
    </section>
  );
}
