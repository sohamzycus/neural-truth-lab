import { extractNoteBody } from "./extract";
import { cleanGhostTags } from "./ghostTags";
import { collapseRepeats, capLength } from "./filters";
import { lexiconBoost } from "./lexicon";
import { scrubObservation } from "../scrub";
import { detectLanguage } from "./lang";
import { scoreQuality } from "./quality";
import { overlapsBenchmark, buildQuizIndex } from "./decontam";
import { wordShingles, minHashSignature } from "./minhash";
import { applyDomainEnrichment } from "./domain";

export type PipelineStep = { stage: string; detail: string; ok: boolean };

export type PipelineResult = {
  id: string;
  accepted: boolean;
  cleanText: string;
  steps: PipelineStep[];
  lang?: ReturnType<typeof detectLanguage>;
  quality?: ReturnType<typeof scoreQuality>;
  exactHash?: string;
  minHash?: number[];
  decontamHit?: boolean;
};

let quizIndex: Set<string> | null = null;

export function setBenchmarkPhrases(phrases: string[]): void {
  quizIndex = buildQuizIndex(phrases);
}

export async function runPipeline(
  id: string,
  raw: string,
  exactHashFn: (t: string) => Promise<string>,
): Promise<PipelineResult> {
  const steps: PipelineStep[] = [];

  const extracted = extractNoteBody(raw);
  if (extracted.extracted) {
    steps.push({ stage: "Content extraction", detail: "Pulled note body from field wrapper", ok: true });
  }

  let text = extracted.text;
  const scrubbed = scrubObservation(text);
  text = scrubbed.text;
  for (const s of scrubbed.steps) {
    steps.push({ stage: s.name, detail: s.detail, ok: true });
  }

  const domain = applyDomainEnrichment(text);
  text = domain.text;
  for (const d of domain.steps) {
    steps.push({ stage: "Domain enrichment", detail: d, ok: true });
  }

  const ghosted = cleanGhostTags(text);
  if (ghosted !== text) {
    steps.push({ stage: "Ghost tag cleanup", detail: "Removed orphan markup tokens", ok: true });
    text = ghosted;
  }

  const { text: capped, truncated } = capLength(text);
  text = capped;
  if (truncated) {
    steps.push({ stage: "Length cap", detail: `Truncated to 4096 chars`, ok: true });
  }

  const { text: deduped, collapsed } = collapseRepeats(text);
  text = deduped;
  if (collapsed) {
    steps.push({ stage: "Repeat collapse", detail: "Collapsed runaway token repetition", ok: true });
  }

  let quality = scoreQuality(text);
  const boosted = lexiconBoost(text, quality.score);
  if (boosted !== quality.score) {
    quality = { ...quality, score: boosted, pass: quality.pass || boosted >= 0.5 };
    steps.push({ stage: "Species lexicon", detail: `boost score→${boosted.toFixed(2)}`, ok: true });
  }

  steps.push({
    stage: "Quality filter",
    detail: quality.pass
      ? `score=${quality.score.toFixed(2)} entropy=${quality.entropy.toFixed(2)}`
      : quality.reason ?? "rejected",
    ok: quality.pass,
  });
  if (!quality.pass) {
    return { id, accepted: false, cleanText: text, steps, quality };
  }

  const lang = detectLanguage(text);
  steps.push({
    stage: "FastText lang ID",
    detail: `${lang.fastTextLabel} p=${lang.fastTextConfidence.toFixed(2)} → tag=${lang.primary}`,
    ok: lang.fastTextLabel !== "unknown",
  });

  const shingles = wordShingles(text);
  const minHash = minHashSignature(shingles);
  steps.push({ stage: "MinHash", detail: `${shingles.size} shingles → ${minHash.length}-dim sig`, ok: true });

  const exactHash = await exactHashFn(text);
  steps.push({ stage: "Exact hash", detail: exactHash.slice(0, 16) + "…", ok: true });

  let decontamHit = false;
  if (quizIndex) {
    decontamHit = overlapsBenchmark(text, quizIndex);
    steps.push({
      stage: "Benchmark decontam",
      detail: decontamHit ? "13-gram overlap with held-out quiz" : "no overlap",
      ok: !decontamHit,
    });
    if (decontamHit) {
      return { id, accepted: false, cleanText: text, steps, lang, quality, exactHash, minHash, decontamHit };
    }
  }

  return { id, accepted: true, cleanText: text, steps, lang, quality, exactHash, minHash, decontamHit };
}
