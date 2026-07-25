export type DatasetStats = {
  name: string;
  inspiredBy: string;
  observationCount: number;
  rawShardRecords?: number;
  countries: number;
  languages: number;
  species: number;
  observationYears: string;
  averageNoteLength: number;
  observerCount: number;
  samples: { id: string; species: string; location: string; excerpt: string }[];
};

export type RawObservation = {
  id: string;
  title: string;
  issues: string[];
  text: string;
  meta?: Record<string, string>;
};

export type PipelineStage = {
  id: string;
  name: string;
  purpose: string;
  technique: string;
  input: string;
  output: string;
  challenges: string;
};

export type Strategy = {
  id: string;
  title: string;
  why: string;
  algorithms: string[];
  before: string;
  after: string;
};

export type DomainEnhancement = {
  id: string;
  title: string;
  description: string;
  inputs: string[];
  output: string;
  note?: string;
};

export type SurgeryMetrics = Record<string, number | string>;

export type Comparison = {
  id: string;
  title: string;
  raw: string;
  clean: string;
  transforms: string[];
};

export type Discovery = {
  id: string;
  label: string;
  value: string;
  detail: string;
  why: string;
};

export type CorpusStats = {
  languages: { name: string; value: number }[];
  species: { name: string; value: number }[];
  qualityTimeline: { stage: string; score: number }[];
  dedupeSavings: { label: string; before: number; after: number }[];
  readinessScore: number;
  tokenReductionPct: number;
};

export type RoadmapItem = {
  id: string;
  label: string;
  description: string;
};

export type Lesson = {
  id: string;
  title: string;
  body: string;
};

export type HealthSyncConfig = {
  intervalMs: number;
};

export type ScrubSample = {
  id: string;
  label: string;
  text: string;
};
