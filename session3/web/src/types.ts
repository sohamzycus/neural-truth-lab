export type LanguageWeights = {
  weights_percent: Record<string, number>;
  population_baseline_percent: Record<string, number>;
  hindi_mcda_vs_population: { mcda_percent: number; population_percent: number; delta_pp: number };
  dravidian_collective_mcda: number;
  dravidian_collective_population: number;
};

export type DataMix = {
  slice_tokens_billions: Record<string, number>;
  language_allocation_billions: Record<string, number>;
  code_breakdown_billions: Record<string, number>;
  synthetic_cap_percent: number;
};

export type FertilityProjections = {
  projections: Record<
    string,
    { avg_indic_fertility: number; relative_inference_cost: number }
  >;
};

export type InferenceCosts = {
  annual_tco_usd_millions: Record<string, number>;
  india_tokenizer_savings_vs_generic_usd_m: number;
  year2_scale: { queries_per_day: number; avg_tokens: number };
};

export type TrainingBudget = {
  total_budget_usd_m: number;
  timeline_months: number;
  billable_gpu_hours_one_run: number;
};

export type Scorecards = {
  scorecards: { id: string; name: string; gate: number }[];
  ship_gate: string;
};

export type Matrix = {
  id: string;
  title: string;
  criteria: string[];
  options: string[];
  scores: Record<string, number[]>;
  weights: number[];
  decision: string;
};

export async function loadJson<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load ${path}`);
  return res.json();
}
