import type { CorpusStats, DatasetStats, SurgeryMetrics } from "../types";

export type HealthMetric = {
  key: string;
  label: string;
  value: number;
  invert?: boolean;
};

export type CorpusHealthInput = {
  surgery: SurgeryMetrics;
  stats: CorpusStats;
  dataset: DatasetStats;
  shardMetaTaggedPct?: number;
};

/** Derive monitor metrics from corpus manifests — no random jitter. */
export function computeCorpusHealth({
  surgery,
  stats,
  dataset,
  shardMetaTaggedPct = 0.9,
}: CorpusHealthInput): HealthMetric[] {
  const observations = Number(surgery.observations) || dataset.observationCount;
  const duplicateRatio = observations > 0 ? (Number(surgery.duplicateClusters) / observations) * 100 : 0;
  const piiPerObs = observations > 0 ? Number(surgery.piiRemoved) / observations : 0;

  const rawQuality = stats.qualityTimeline[0]?.score ?? 0.42;
  const noiseScore = Math.round(rawQuality * 100);

  const corpusQuality = Math.round(Number(surgery.averageQualityScore) * 100);

  const shares = stats.languages.map((l) => l.value / 100);
  const entropy = -shares.reduce((sum, p) => sum + (p > 0 ? p * Math.log2(p) : 0), 0);
  const maxEntropy = Math.log2(Math.max(shares.length, 2));
  const languageBalance = Math.round((entropy / maxEntropy) * 100);

  const metaTagged = shardMetaTaggedPct;
  const metadataCompleteness = Math.round(
    Math.min(100, metaTagged * 35 + (dataset.countries / 40) * 30 + (dataset.languages / 20) * 35),
  );

  const piiRisk = Math.round(Math.min(100, piiPerObs * 500 + 4));

  const trainingReadiness = Math.round(stats.readinessScore * 100);

  return [
    { key: "noiseScore", label: "Noise Score", value: noiseScore, invert: true },
    { key: "corpusQuality", label: "Corpus Quality", value: corpusQuality },
    { key: "duplicateRatio", label: "Duplicate Ratio", value: Math.round(duplicateRatio), invert: true },
    { key: "languageBalance", label: "Language Balance", value: languageBalance },
    { key: "metadataCompleteness", label: "Metadata Completeness", value: metadataCompleteness },
    { key: "piiRisk", label: "PII Risk", value: piiRisk, invert: true },
    { key: "trainingReadiness", label: "Training Readiness", value: trainingReadiness },
  ];
}
