import { computeCorpusHealth } from "./corpusHealth";

const metrics = computeCorpusHealth({
  surgery: {
    observations: 1000,
    duplicateClusters: 100,
    piiRemoved: 10,
    averageQualityScore: 0.87,
  },
  stats: {
    languages: [{ name: "English", value: 62 }, { name: "Hindi", value: 14 }],
    species: [],
    qualityTimeline: [{ stage: "Raw", score: 0.42 }],
    dedupeSavings: [],
    readinessScore: 0.91,
    tokenReductionPct: 18,
  },
  dataset: {
    name: "test",
    inspiredBy: "test",
    observationCount: 1000,
    countries: 31,
    languages: 14,
    species: 100,
    observationYears: "2020",
    averageNoteLength: 80,
    observerCount: 500,
    samples: [],
  },
  shardMetaTaggedPct: 0.94,
});

if (metrics.length !== 7) throw new Error("expected 7 metrics");
if (metrics.find((m) => m.key === "trainingReadiness")?.value !== 91) throw new Error("readiness");
console.log("corpusHealth selfcheck OK");
