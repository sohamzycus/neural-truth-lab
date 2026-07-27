import { fastTextPredict, getFastTextModelMeta } from "./fasttext";
import { detectLanguage } from "./lang";
import { extractEntities, maskNer } from "./ner";
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

// FastText
const meta = getFastTextModelMeta();
assert(meta.method.includes("fasttext"), "fasttext model loaded");
const en = fastTextPredict("Indian Robin on agricultural edge fence");
assert(en.label === "en" && en.confidence > 0.3, `fasttext en got ${en.label} ${en.confidence}`);
const hi = fastTextPredict("एशियन कोयल की आवाज सुबह");
assert(hi.label === "hi", `fasttext hi got ${hi.label}`);
const lang = detectLanguage("एशियन कोयल loud call");
assert(lang.fastTextLabel === "hi" || lang.primary.includes("hi"), "fasttext+script hi");

// NER
const ner = maskNer("Rajesh Kumar saw Drongo in Pune — birder@example.com +91 98765 43210");
assert(ner.text.includes("[PERSON]"), "ner person");
assert(ner.text.includes("[LOC]"), "ner loc");
assert(ner.text.includes("[EMAIL]"), "ner email");
assert(ner.text.includes("[PHONE]"), "ner phone");
assert(extractEntities("BNHS trip to Bharatpur").some((e) => e.type === "ORG"), "ner org");

// quality
assert(!scoreQuality("ok").pass, "short rejected");
assert(scoreQuality("Indian Robin on fence with chee-chee call").pass, "valid note passes");

// minhash
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

// decontam
const quiz = buildQuizIndex(["which bird has a red breast in spring migration"]);
assert(overlapsBenchmark("field quiz: which bird has a red breast in spring migration notes", quiz), "overlap");

assert(collapseRepeats("koel koel koel koel koel").collapsed, "repeat collapse");
assert(capLength("x".repeat(5000), 4096).truncated, "length cap");
assert(cleanGhostTags("text </b> more").includes("text"), "ghost tags");
assert(mentionsSpecies("saw Indian Robin"), "lexicon");
assert(extractNoteBody("note: Hornbill at dawn").extracted, "extract");

setBenchmarkPhrases(["which bird has a red breast in spring migration"]);
const run = await runPipeline("t1", "Saw <b>Robin</b> in Pune — contact birder@example.com", exactHash);
assert(run.steps.some((s) => s.stage === "NER / PII removal" || s.stage.includes("NER")), "ner in pipeline");
assert(run.steps.some((s) => s.stage === "FastText lang ID"), "fasttext in pipeline");
assert(run.accepted, "clean note accepted");

console.log("pipeline selfcheck OK");
