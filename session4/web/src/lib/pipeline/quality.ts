const MIN_LEN = 12;
const MIN_ENTROPY = 2.0;

function charEntropy(text: string): number {
  const freq = new Map<string, number>();
  let total = 0;
  for (const c of text.toLowerCase()) {
    if (!/\S/.test(c)) continue;
    freq.set(c, (freq.get(c) ?? 0) + 1);
    total++;
  }
  if (total === 0) return 0;
  let h = 0;
  for (const n of freq.values()) {
    const p = n / total;
    h -= p * Math.log2(p);
  }
  return h;
}

export type QualityResult = {
  pass: boolean;
  score: number;
  entropy: number;
  reason?: string;
};

/** Length + Shannon entropy gate; short heard-only notes need len ≥ MIN_LEN. */
export function scoreQuality(text: string): QualityResult {
  const t = text.trim();
  if (t.length < MIN_LEN) {
    return { pass: false, score: 0, entropy: 0, reason: "too short" };
  }
  const entropy = charEntropy(t);
  if (entropy < MIN_ENTROPY) {
    return { pass: false, score: entropy / MIN_ENTROPY, entropy, reason: "low entropy" };
  }
  return { pass: true, score: Math.min(1, entropy / 4.5), entropy };
}
