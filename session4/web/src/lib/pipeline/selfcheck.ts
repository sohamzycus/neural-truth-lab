import { detectLanguage } from "./lang";
import { scoreQuality } from "./quality";
import { wordShingles, minHashSignature, jaccardEstimate, clusterNearDuplicates } from "./minhash";
import { buildQuizIndex, overlapsBenchmark } from "./decontam";
import { collapseRepeats, capLength } from "./filters";
import { cleanGhostTags } from "./ghostTags";
import { mentionsSpecies } from "./lexicon";
import { extractNoteBody } from "./extract";
import { setBenchmarkPhrases, runPipeline } from "./runPipeline";
import { exactHash } from "../scrub";

function assert(cond: unknown, msg: string): void {
  if (!cond) throw new Error(msg);
}

const hi = detectLanguage("एशियन कोयल loud call");
assert(hi.primary.includes("hi"), "devanagari detected");

assert(!scoreQuality("ok").pass, "short rejected");
assert(scoreQuality("Indian Robin on fence with chee-chee call").pass, "valid note passes");

const a = minHashSignature(wordShingles("sunbird at nectar bush in garden"));
const b = minHashSignature(wordShingles("sunbird at nectar bush near garden"));
const c = minHashSignature(wordShingles("completely different hornbill note"));
assert(jaccardEstimate(a, b) > jaccardEstimate(a, c), "similar notes higher jaccard");

const { nearDupCount } = clusterNearDuplicates([
  { id: "1", sig: a },
  { id: "2", sig: a },
  { id: "3", sig: c },
]);
assert(nearDupCount >= 1, "near dup cluster");

const quiz = buildQuizIndex(["which bird has a red breast in spring migration"]);
assert(overlapsBenchmark("field quiz: which bird has a red breast in spring migration notes", quiz), "overlap");

const { collapsed } = collapseRepeats("koel koel koel koel koel");
assert(collapsed, "repeat collapse");

const { truncated } = capLength("x".repeat(5000), 4096);
assert(truncated, "length cap");

assert(cleanGhostTags("text </b> more").includes("text"), "ghost tags");

assert(mentionsSpecies("saw Indian Robin"), "lexicon");

const ext = extractNoteBody("note: Hornbill at dawn");
assert(ext.extracted, "extract");

setBenchmarkPhrases(["which bird has a red breast in spring migration"]);
const run = await runPipeline("t1", "Saw <b>Robin</b> — contact birder@example.com", exactHash);
assert(run.steps.some((s) => s.stage === "PII removal"), "scrub ran");
assert(run.accepted, "clean note accepted");

console.log("pipeline selfcheck OK");
