/** Unicode script counts — secondary signal paired with FastText (strategy s2). */

const RANGES: { id: string; re: RegExp }[] = [
  { id: "hi", re: /[\u0900-\u097F]/ },
  { id: "ta", re: /[\u0B80-\u0BFF]/ },
  { id: "ml", re: /[\u0D00-\u0D7F]/ },
  { id: "bn", re: /[\u0980-\u09FF]/ },
  { id: "en", re: /[A-Za-z]/ },
];

export function scriptDetect(text: string): { counts: Record<string, number>; total: number } {
  const counts: Record<string, number> = {};
  let total = 0;
  for (const { id, re } of RANGES) {
    const n = text.match(new RegExp(re.source, "g"))?.length ?? 0;
    if (n > 0) counts[id] = n;
    total += n;
  }
  return { counts, total };
}
