export interface VerifiedSubmission {
  generated_at: string;
  tokenizer: {
    model: string;
    vocab_size: number;
    normalizer: Record<string, unknown>;
    pretokenizer: Record<string, unknown>;
    decoder: Record<string, unknown>;
    sha256: string;
    verified: boolean;
  };
  languages: string[];
  corpora: Record<
    string,
    {
      language: string;
      language_name: string;
      article: string;
      source_url: string;
      frozen_path: string;
      sha256: string;
      faithful_units: number;
      characters: number;
      bytes: number;
    }
  >;
  metrics: {
    faithful_unit_counts: Record<string, number>;
    token_counts: Record<string, number>;
    fertilities: Record<string, number>;
    spread: number;
    raw_score: number;
    hindi_penalty: number;
    adjusted_score: number;
  };
  thresholds: { en_under_1_2: boolean; hi_under_1_2: boolean };
  roundtrip: {
    reviewer_sample: boolean;
    full_corpus: Record<string, boolean>;
    samples: Record<string, boolean>;
  };
  vocabularyComposition: {
    vocab_size: number;
    categories: Record<string, number>;
    sum: number;
  };
  vocabularyUtilization: {
    per_corpus_unique_ids: Record<string, number>;
    used_by_at_least_one: number;
    unused_by_all_four: number;
    used_by_exactly_one: number;
    used_by_all_four: number;
  };
  fertilityExamples: {
    reviewer_sample: {
      original_text: string;
      faithful_units: string[];
      faithful_unit_count: number;
      bpe_tokens: string[];
      token_ids?: number[];
      bpe_token_count: number;
      fertility: number | null;
      decoded_text: string;
    };
    per_language: Record<string, {
      original_text: string;
      faithful_unit_count: number;
      bpe_token_count: number;
      fertility: number | null;
    }>;
  };
  optimizer: {
    total_measured?: number;
    baseline_weights?: Record<string, number>;
    candidates_passing_both_thresholds?: number;
  };
  provenance: { weights: Record<string, number> };
  tokenizer_sha256: string;
  baseline?: {
    weights: Record<string, number>;
    fertilities: Record<string, number>;
    spread: number;
    adjusted_score: number;
  };
  baselineVsWinner?: Record<string, unknown>;
  vocabularyMap?: Array<{ id: number; token: string; category: string }>;
}

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
    { faithful_units: number; tokens: number; fertility: number; wordish_units?: number }
  >;
  roundtrip?: {
    reviewer_sample: boolean;
    full_corpus: Record<string, boolean>;
    valid: boolean;
  };
  thresholds?: {
    en_under_1_2: boolean;
    hi_under_1_2: boolean;
  };
  scoring: {
    x_min: number;
    x_max: number;
    spread: number;
    raw_score: number;
    hindi_penalty: number;
    final_grade: number;
    adjusted_score?: number;
  };
  provenance?: {
    weights?: Record<string, number>;
    strategy?: string;
    constraint_class?: string;
    english_threshold_pass?: boolean;
    hindi_threshold_pass?: boolean;
    selection_reason?: string;
  };
}

export interface ResubmissionComparisonRow {
  label: string;
  weights?: Record<string, number>;
  fertilities: Record<string, number>;
  spread: number;
  adjusted_score: number;
  status: string;
  constraint_class?: string;
  english_threshold_pass?: boolean;
  hindi_threshold_pass?: boolean;
}

export interface ResubmissionComparison {
  generated_at?: string;
  rows: (ResubmissionComparisonRow | null)[];
  selection?: Record<string, unknown>;
}

export interface ResubmissionExperiment {
  experiment_id: string;
  strategy: string;
  weights: Record<string, number>;
  final_grade: number;
  adjusted_score?: number;
  raw_score: number;
  hindi_penalty: number;
  spread: number;
  fertilities: Record<string, number>;
  status: string;
  english_threshold_pass?: boolean;
  hindi_threshold_pass?: boolean;
  constraint_class?: string;
}

export interface ResubmissionExperiments {
  generated_at?: string;
  objective?: string;
  experiments: ResubmissionExperiment[];
  winner_experiment_id?: string;
  total_measured?: number;
  winner_selection?: Record<string, unknown>;
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
