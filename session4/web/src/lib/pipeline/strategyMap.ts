/** Maps each of the 10 strategies to its implementation module. */
export const STRATEGY_IMPLEMENTATION: Record<string, { module: string; fn: string }> = {
  s1: { module: "src/lib/scrub/index.ts", fn: "normalizeUnicode" },
  s2: { module: "src/lib/pipeline/fasttext.ts + lang.ts", fn: "fastTextPredict + detectLanguage" },
  s3: { module: "src/lib/pipeline/quality.ts", fn: "scoreQuality + lexicon.ts" },
  s4: { module: "src/lib/scrub/index.ts", fn: "exactHash" },
  s5: { module: "src/lib/pipeline/minhash.ts", fn: "clusterNearDuplicates" },
  s6: { module: "src/lib/pipeline/ner.ts", fn: "extractEntities, maskNer" },
  s7: { module: "src/lib/scrub/index.ts", fn: "stripHtml" },
  s8: { module: "src/lib/pipeline/filters.ts", fn: "collapseRepeats, capLength" },
  s9: { module: "src/lib/pipeline/decontam.ts", fn: "overlapsBenchmark" },
  s10: { module: "scripts/manifest-utils.ts", fn: "sha256File" },
};

export function isStrategyImplemented(id: string): boolean {
  return id in STRATEGY_IMPLEMENTATION;
}
