import { readFileSync, writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { exactHash } from "../src/lib/scrub/index.ts";
import { setBenchmarkPhrases, runPipeline } from "../src/lib/pipeline/runPipeline.ts";
import { clusterNearDuplicates } from "../src/lib/pipeline/minhash.ts";
import { sha256File, sha256Text } from "./manifest-utils.ts";

const __dir = dirname(fileURLToPath(import.meta.url));
const dataDir = join(__dir, "../public/data");

type RawObs = { id: string; text: string; title?: string; meta?: Record<string, string> };

const raw = JSON.parse(readFileSync(join(dataDir, "raw_observations.json"), "utf8")) as RawObs[];
const quiz = JSON.parse(readFileSync(join(dataDir, "benchmark_quiz.json"), "utf8")) as { phrases: string[] };
const datasetStats = JSON.parse(readFileSync(join(dataDir, "dataset_stats.json"), "utf8")) as {
  observationCount: number;
};

setBenchmarkPhrases(quiz.phrases);

const exactSeen = new Map<string, string>();
const accepted: (Awaited<ReturnType<typeof runPipeline>> & { raw?: RawObs })[] = [];
let qualityRejected = 0;
let decontamRejected = 0;
let exactDupRemoved = 0;
let piiMasked = 0;
let repeatCollapsed = 0;
let lengthTruncated = 0;
const langCounts: Record<string, number> = {};

for (const obs of raw) {
  const result = await runPipeline(obs.id, obs.text, exactHash);
  if (result.steps.some((s) => s.stage.includes("NER"))) piiMasked++;
  if (result.steps.some((s) => s.stage === "Repeat collapse")) repeatCollapsed++;
  if (result.steps.some((s) => s.stage === "Length cap")) lengthTruncated++;
  if (!result.quality?.pass) {
    qualityRejected++;
    continue;
  }
  if (result.decontamHit) {
    decontamRejected++;
    continue;
  }
  if (result.exactHash && exactSeen.has(result.exactHash)) {
    exactDupRemoved++;
    continue;
  }
  if (result.exactHash) exactSeen.set(result.exactHash, obs.id);
  if (result.lang) langCounts[result.lang.primary] = (langCounts[result.lang.primary] ?? 0) + 1;
  accepted.push({ ...result, raw: obs });
}

const nearInput = accepted.filter((r) => r.minHash).map((r) => ({ id: r.id, sig: r.minHash! }));
const { clusters, nearDupCount } = clusterNearDuplicates(nearInput);

const nearDupDrop = new Set<string>();
for (const c of clusters) {
  for (const id of c.memberIds) {
    if (id !== c.repId) nearDupDrop.add(id);
  }
}

const trainSafe = accepted.filter((r) => !nearDupDrop.has(r.id));
const trainSafeLines = trainSafe.map((r) =>
  JSON.stringify({
    id: r.id,
    text: r.cleanText,
    lang: r.lang?.primary,
    quality: r.quality?.score,
    hash: r.exactHash,
    species: r.raw?.meta?.species,
    location: r.raw?.meta?.location,
  }),
);
const trainSafeContent = trainSafeLines.join("\n") + (trainSafeLines.length ? "\n" : "");
writeFileSync(join(dataDir, "train_safe_corpus.jsonl"), trainSafeContent);

const rawJsonl = raw.map((o) => JSON.stringify(o)).join("\n") + "\n";
writeFileSync(join(dataDir, "raw_observations.jsonl"), rawJsonl);

const algorithms = [
  "content extraction",
  "NFKC + HTML/PII scrub + ghost tags",
  "length cap + repeat collapse",
  "quality filter (length + entropy + species lexicon)",
    "FastText char-ngram language ID + script heuristics",
    "gazetteer + pattern NER (PERSON/LOC/ORG/EMAIL/PHONE)",
  "SHA-256 exact dedupe",
  "MinHash + LSH near-dedupe",
  "13-gram benchmark decontamination",
  "SHA-256 manifest generation",
];

const shardRun = {
  processedAt: new Date().toISOString(),
  algorithms,
  inputRecords: raw.length,
  qualityRejected,
  decontamRejected,
  exactDupRemoved,
  nearDupClusters: clusters.length,
  nearDupRecords: nearDupCount,
  acceptedRecords: trainSafe.length,
  piiMasked,
  repeatCollapsed,
  lengthTruncated,
  languageDistribution: langCounts,
  corpusTotalObservations: datasetStats.observationCount,
  sampleTraces: trainSafe.slice(0, 3).map((r) => ({
    id: r.id,
    accepted: r.accepted,
    steps: r.steps.map((s) => `${s.stage}: ${s.detail}`),
  })),
};

writeFileSync(join(dataDir, "shard_pipeline_run.json"), JSON.stringify(shardRun, null, 2));

const manifestFiles = [
  sha256File(join(dataDir, "raw_observations.json"), raw.length),
  sha256File(join(dataDir, "raw_observations.jsonl"), raw.length),
  sha256Text("train_safe_corpus.jsonl", trainSafeContent, trainSafe.length),
  sha256File(join(dataDir, "dataset_stats.json")),
  sha256File(join(dataDir, "shard_pipeline_run.json")),
];

const corpusManifest = {
  corpusVersion: "ataavi-text-v0.4",
  totalObservations: datasetStats.observationCount,
  scaleLabel: "47.2M observations (10–100M class)",
  rawShardRecords: raw.length,
  trainSafeShardRecords: trainSafe.length,
  generatedAt: new Date().toISOString(),
  files: manifestFiles,
  note: "Full 47.2M corpus ships as versioned object-store shards; this portal bundles verified 5k sample + train-safe output.",
};

writeFileSync(join(dataDir, "corpus_manifest.json"), JSON.stringify(corpusManifest, null, 2));

const pkg = JSON.parse(readFileSync(join(dataDir, "corpus_download_package.json"), "utf8")) as {
  downloads: { id: string; records?: number }[];
  trainSafeShardRecords: number;
  generatedAt: string;
  totalObservations: number;
};
pkg.trainSafeShardRecords = trainSafe.length;
pkg.generatedAt = new Date().toISOString();
pkg.totalObservations = datasetStats.observationCount;
for (const d of pkg.downloads) {
  if (d.id === "train-safe-jsonl") d.records = trainSafe.length;
}
writeFileSync(join(dataDir, "corpus_download_package.json"), JSON.stringify(pkg, null, 2));

console.log(
  `Shard pipeline: ${raw.length} in → ${trainSafe.length} train-safe (${nearDupCount} near-dupes, ${exactDupRemoved} exact dupes)`,
);
console.log(`Wrote train_safe_corpus.jsonl, raw_observations.jsonl, corpus_manifest.json`);
