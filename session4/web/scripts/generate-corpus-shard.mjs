/**
 * Generate a realistic raw observation shard for the static portal.
 * Run: node scripts/generate-corpus-shard.mjs
 */
import { writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dir = dirname(fileURLToPath(import.meta.url));
const dataDir = join(__dir, "../public/data");

const TOTAL_CORPUS = 47_200_000;
const SHARD_SIZE = 5000;

const species = [
  { common: "Indian Robin", sci: "Copsychus fulicatus", region: "India" },
  { common: "Indian Pitta", sci: "Pitta brachyura", region: "India" },
  { common: "Himalayan Monal", sci: "Lophophorus impejanus", region: "India" },
  { common: "Black Drongo", sci: "Dicrurus macrocercus", region: "India" },
  { common: "Purple Sunbird", sci: "Cinnyris asiaticus", region: "India" },
  { common: "Asian Koel", sci: "Eudynamys scolopaceus", region: "India" },
  { common: "Sarus Crane", sci: "Antigone antigone", region: "India" },
  { common: "Great Hornbill", sci: "Buceros bicornis", region: "India" },
  { common: "Rose-ringed Parakeet", sci: "Psittacula krameri", region: "India" },
  { common: "White-throated Kingfisher", sci: "Halcyon smyrnensis", region: "India" },
  { common: "Common Tailorbird", sci: "Orthotomus sutorius", region: "India" },
  { common: "Blyth's Reed Warbler", sci: "Acrocephalus dumetorum", region: "India" },
  { common: "Painted Stork", sci: "Mycteria leucocephala", region: "India" },
  { common: "Indian Peafowl", sci: "Pavo cristatus", region: "India" },
  { common: "Malabar Trogon", sci: "Harpactes fasciatus", region: "India" },
  { common: "American Robin", sci: "Turdus migratorius", region: "Global" },
  { common: "European Robin", sci: "Erithacus rubecula", region: "Global" },
];

const locations = [
  "Pune, Maharashtra", "Thattekad, Kerala", "Bharatpur, Rajasthan", "Valparai, Tamil Nadu",
  "Chilika, Odisha", "Eaglenest, Arunachal Pradesh", "Rann of Kutch, Gujarat", "Hemis, Ladakh",
  "Sundarbans, West Bengal", "Nainital, Uttarakhand", "Central Park, NYC", "London Wetland Centre, UK",
];

const issueSets = [
  ["GPS", "PII"],
  ["HTML", "Boilerplate"],
  ["Duplicate", "Whitespace"],
  ["Synonym", "Scientific"],
  ["Unicode", "OCR"],
  ["Multilingual", "Formatting"],
  ["Media", "Broken links"],
  ["Near-dupe", "Benchmark risk"],
  ["GPS", "HTML"],
  ["PII", "Name"],
];

const templates = [
  (s, loc) => `${s.common} at ${loc} — male on wire, tail cocked, chee-chee call.`,
  (s, loc) => `Heard only ${s.common} near ${loc}; possible rain-affected recording.`,
  (s, loc) => `<b>${s.common}</b> (${s.sci}) observed at ${loc}. Contact birder@example.com`,
  (s, loc) => `${s.common} / ${s.sci} / indian ${s.common.toLowerCase()} — scrub edge habitat.`,
  (s, loc) => `एशियन कोयल style note for ${s.common} at ${loc} — हल्की धुंध.`,
  (s, loc) => `OCR: ${s.common.replace(/i/g, "1")} at ${loc}. GPS 28.${Math.floor(Math.random() * 9000)}`,
  (s, loc) => `${s.common} at nectar bush. `.repeat(3),
  (s, loc) => `café trailhead · ${s.common} · ${s.sci} — fancy ﬁde ligatures`,
];

function pick(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

const observations = [];
for (let i = 0; i < SHARD_SIZE; i++) {
  const sp = pick(species);
  const loc = pick(locations);
  const issues = pick(issueSets);
  const tpl = pick(templates);
  const id = `raw-${String(i + 1).padStart(6, "0")}`;
  const text = tpl(sp, loc);
  observations.push({
    id,
    title: `${sp.common} · ${issues[0]} issue`,
    issues,
    text,
    meta: {
      species: sp.common,
      scientific: sp.sci,
      location: loc,
      region: sp.region,
      ingestedAt: `2024-${String((i % 12) + 1).padStart(2, "0")}-${String((i % 28) + 1).padStart(2, "0")}`,
      corpusIndex: Math.floor((TOTAL_CORPUS / SHARD_SIZE) * i),
    },
  });
}

writeFileSync(join(dataDir, "raw_observations.json"), JSON.stringify(observations));

const datasetStats = {
  name: "Bird Observation Corpus",
  inspiredBy: "Community bird observations (eBird-style) · India-primary with global decontamination slice",
  observationCount: TOTAL_CORPUS,
  rawShardRecords: SHARD_SIZE,
  countries: 142,
  languages: 38,
  species: 9842,
  observationYears: "1998–2025",
  averageNoteLength: 94,
  observerCount: 2_840_000,
  samples: observations.slice(0, 8).map((o) => ({
    id: o.id,
    species: o.meta.species,
    location: o.meta.location,
    excerpt: o.text.slice(0, 120) + (o.text.length > 120 ? "…" : ""),
  })),
};

writeFileSync(join(dataDir, "dataset_stats.json"), JSON.stringify(datasetStats, null, 2));

const surgery = {
  observations: TOTAL_CORPUS,
  languages: 38,
  species: 9842,
  duplicateClusters: 4_820_000,
  piiRemoved: 1_240_000,
  unicodeFixes: 8_400_000,
  gpsMasked: 620_000,
  scientificNamesNormalized: 12_400_000,
  averageQualityScore: 0.89,
};
writeFileSync(join(dataDir, "surgery_metrics.json"), JSON.stringify(surgery, null, 2));

const corpusStats = {
  languages: [
    { name: "English", value: 54 },
    { name: "Hindi", value: 18 },
    { name: "Tamil", value: 7 },
    { name: "Malayalam", value: 5 },
    { name: "Bengali", value: 5 },
    { name: "Other", value: 11 },
  ],
  species: [
    { name: "Black Drongo", value: 3_240_000 },
    { name: "Asian Koel", value: 2_680_000 },
    { name: "House Crow", value: 2_410_000 },
    { name: "Purple Sunbird", value: 2_180_000 },
    { name: "Indian Robin", value: 1_920_000 },
    { name: "Rose-ringed Parakeet", value: 1_640_000 },
    { name: "Sarus Crane", value: 890_000 },
    { name: "Great Hornbill", value: 420_000 },
  ],
  qualityTimeline: [
    { stage: "Raw", score: 0.38 },
    { stage: "Extract", score: 0.52 },
    { stage: "Filter", score: 0.67 },
    { stage: "Dedupe", score: 0.78 },
    { stage: "PII", score: 0.86 },
    { stage: "Final", score: 0.92 },
  ],
  dedupeSavings: [
    { label: "Exact", before: TOTAL_CORPUS, after: 38_400_000 },
    { label: "Near", before: 38_400_000, after: 31_200_000 },
  ],
  readinessScore: 0.92,
  tokenReductionPct: 21.6,
};
writeFileSync(join(dataDir, "corpus_stats.json"), JSON.stringify(corpusStats, null, 2));

writeFileSync(
  join(dataDir, "dataset_manifest.json"),
  JSON.stringify({
    corpusVersion: "ataavi-text-v0.4",
    totalObservations: TOTAL_CORPUS,
    rawShardRecords: SHARD_SIZE,
    format: "json",
    note: "Portal displays and downloads a representative noisy shard; full corpus ships as versioned manifests.",
  }, null, 2),
);

console.log(`Wrote ${SHARD_SIZE} raw observations, corpus total ${TOTAL_CORPUS.toLocaleString()}`);
