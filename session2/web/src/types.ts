export interface TokenizerData {
  version: string;
  pretokenization: "whitespace" | "character" | "grapheme";
  special_tokens: Record<string, number>;
  vocab: Record<string, number>;
  merges: string[][];
}

export interface LanguageStat {
  lang: string;
  label: string;
  characters: number;
  word_units: number;
  tokens: number;
  fertility: number;
  rank: number;
  distance_from_best?: number;
  distance_from_worst?: number;
}

export interface ResubmissionMetrics {
  generated_at?: string;
  tokenizer: {
    format: string;
    vocab_size: number;
    sha256: string;
    vocab_constraint_pass?: boolean;
  };
  corpus_dir?: string;
  corpus_sha256?: Record<string, string>;
  languages: Record<
    string,
    { wordish_units: number; tokens: number; fertility: number }
  >;
  scoring: {
    x_min: number;
    x_max: number;
    spread: number;
    raw_score: number;
    hindi_penalty: number;
    final_grade: number;
  };
  provenance?: {
    weights?: Record<string, number>;
    strategy?: string;
  };
}

export interface ResubmissionExperiment {
  experiment_id: string;
  strategy: string;
  weights: Record<string, number>;
  final_grade: number;
  raw_score: number;
  hindi_penalty: number;
  spread: number;
  fertilities: Record<string, number>;
  status: string;
}

export interface ResubmissionExperiments {
  generated_at?: string;
  objective?: string;
  experiments: ResubmissionExperiment[];
  winner_experiment_id?: string;
}

export interface Stats {
  generated_at: string;
  source?: string;
  verified: boolean;
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
  english_constraint: { max_allowed: number; actual: number; pass: boolean };
  vocab_constraint?: { max_allowed: number; actual: number; pass: boolean };
  tokenizer_sha256: string;
  corpus_hashes?: Record<string, string>;
  vocab_allocation?: Record<string, number>;
  vocab_attribution?: Record<string, number>;
  trust?: {
    english_lte_1_2: boolean;
    vocabulary_lte_10000: boolean;
    one_deterministic_tokenizer: boolean;
    scores_independently_reproducible: boolean;
  };
  optimization_audit?: {
    hero_claim_recommended?: string;
    highest_implemented_level?: number;
    deliberate_degradation_used?: boolean;
  };
}

export interface StrategyRow {
  id: string;
  name: string;
  implemented: boolean;
  verified: boolean;
  winner: boolean;
  vocabularySize: number;
  fertility: Record<string, number>;
  gap: number;
  score: number;
  englishConstraintPassed: boolean;
}

export interface StrategyComparison {
  strategies: StrategyRow[];
  legacy?: unknown[];
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

export const LANG_DISPLAY: Record<string, { label: string; native: string; fontClass: string }> = {
  en: { label: "English", native: "ENGLISH", fontClass: "" },
  hi: { label: "Hindi", native: "हिन्दी", fontClass: "font-devanagari" },
  te: { label: "Telugu", native: "తెలుగు", fontClass: "font-telugu" },
  bn: { label: "Bengali", native: "বাংলা", fontClass: "font-bengali" },
};
