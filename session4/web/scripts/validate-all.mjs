import { readFileSync, writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { execSync } from "node:child_process";

const __dir = dirname(fileURLToPath(import.meta.url));
const root = join(__dir, "..");
const dataDir = join(root, "public/data");
const reportPath = join(root, "VALIDATION_REPORT.json");

console.log("=== Corpus Forge validation ===\n");

execSync("npm run selfcheck", { cwd: root, stdio: "inherit" });
execSync("npm run pipeline:shard", { cwd: root, stdio: "inherit" });

const shardRun = JSON.parse(readFileSync(join(dataDir, "shard_pipeline_run.json"), "utf8"));
const manifest = JSON.parse(readFileSync(join(dataDir, "corpus_manifest.json"), "utf8"));
const pkg = JSON.parse(readFileSync(join(dataDir, "corpus_download_package.json"), "utf8"));
const model = JSON.parse(readFileSync(join(root, "src/lib/pipeline/data/fasttext_lang_model.json"), "utf8"));

const report = {
  validatedAt: new Date().toISOString(),
  selfcheck: "pass",
  corpusTotalObservations: manifest.totalObservations,
  rawShardRecords: manifest.rawShardRecords,
  trainSafeRecords: manifest.trainSafeShardRecords,
  fastText: {
    method: model.method,
    trainAccuracy: model.trainAccuracy,
    labels: model.labels,
  },
  pipeline: {
    algorithms: shardRun.algorithms,
    inputRecords: shardRun.inputRecords,
    acceptedRecords: shardRun.acceptedRecords,
    exactDupRemoved: shardRun.exactDupRemoved,
    nearDupRecords: shardRun.nearDupRecords,
  },
  implementations: {
    fastText: { file: "src/lib/pipeline/fasttext.ts", status: "implemented" },
    ner: { file: "src/lib/pipeline/ner.ts", status: "implemented" },
    minHashLsh: { file: "src/lib/pipeline/minhash.ts", status: "implemented" },
    decontamination: { file: "src/lib/pipeline/decontam.ts", status: "implemented" },
    qualityFilter: { file: "src/lib/pipeline/quality.ts", status: "implemented" },
  },
  downloads: pkg.downloads.map((d) => ({
    id: d.id,
    path: d.path,
    records: d.records,
  })),
};

writeFileSync(reportPath, JSON.stringify(report, null, 2));
console.log(`\nWrote ${reportPath}`);
console.log(JSON.stringify(report, null, 2));
