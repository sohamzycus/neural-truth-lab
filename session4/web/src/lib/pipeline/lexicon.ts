const SPECIES = [
  "robin", "drongo", "koel", "sunbird", "hornbill", "crane", "pitta", "warbler",
  "kingfisher", "parakeet", "peafowl", "stork", "monal", "trogon", "crow", "sparrow",
];

export function mentionsSpecies(text: string): boolean {
  const lower = text.toLowerCase();
  return SPECIES.some((s) => lower.includes(s));
}

/** Lexicon hit boosts quality score for short heard-only notes. */
export function lexiconBoost(text: string, baseScore: number): number {
  if (mentionsSpecies(text)) return Math.min(1, baseScore + 0.12);
  return baseScore;
}
