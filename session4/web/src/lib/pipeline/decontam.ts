export function buildNgrams(text: string, n = 13): Set<string> {
  const norm = text.toLowerCase().replace(/\s+/g, " ").trim();
  const grams = new Set<string>();
  if (norm.length < n) {
    if (norm) grams.add(norm);
    return grams;
  }
  for (let i = 0; i <= norm.length - n; i++) grams.add(norm.slice(i, i + n));
  return grams;
}

export function buildQuizIndex(phrases: string[], n = 13): Set<string> {
  const index = new Set<string>();
  for (const p of phrases) {
    for (const g of buildNgrams(p, n)) index.add(g);
  }
  return index;
}

export function overlapsBenchmark(text: string, quizIndex: Set<string>, n = 13): boolean {
  for (const g of buildNgrams(text, n)) {
    if (quizIndex.has(g)) return true;
  }
  return false;
}
