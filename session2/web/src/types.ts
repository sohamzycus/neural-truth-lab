export interface LanguageStat {
  lang: string;
  label: string;
  characters: number;
  word_units: number;
  tokens: number;
  fertility: number;
  rank: number;
}

export interface Stats {
  generated_at: string;
  winning_strategy: string;
  vocabulary_size: number;
  vocab_budget: number;
  languages: LanguageStat[];
  fertilities: Record<string, number>;
  sorted_x: number[];
  x_min: number;
  x_max: number;
  max_min_gap: number;
  score: number;
  english_constraint: {
    max_allowed: number;
    actual: number;
    pass: boolean;
  };
  vocab_allocation: Record<string, number>;
  tokenizer_sha256: string;
}

export interface StrategyRow {
  strategy: string;
  vocabulary_size: number;
  en_fertility: number;
  hi_fertility: number;
  te_fertility: number;
  bn_fertility: number;
  max_min_gap: number;
  score: number;
  english_pass: boolean;
}

export interface OptTraceStep {
  step: number;
  note: string;
  fertilities: Record<string, number>;
  max_min_gap: number;
  score: number;
  vocab_size: number;
  winning_candidate?: string;
}

export interface RejectedMerge {
  candidate: string;
  pair: string[];
  frequency: number;
  language: string;
  old_score: number;
  predicted_score: number;
  reason: string;
}

export interface TokenizerData {
  version: string;
  pretokenization: "whitespace" | "character" | "grapheme";
  special_tokens: Record<string, number>;
  vocab: Record<string, number>;
  merges: string[][];
}

export interface SweepCurves {
  per_language: Record<string, Array<{ vocab_size: number; fertility: number }>>;
  allocation_sweep: Array<{
    allocation: Record<string, number>;
    fertilities: Record<string, number>;
    score: number;
    gap: number;
  }>;
}

export async function loadJson<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load ${path}`);
  return res.json() as Promise<T>;
}
