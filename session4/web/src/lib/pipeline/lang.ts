/** Script-heuristic language ID (ponytail: not FastText — Unicode ranges + ratio voting). */

const RANGES: { id: string; re: RegExp }[] = [
  { id: "hi", re: /[\u0900-\u097F]/ },
  { id: "ta", re: /[\u0B80-\u0BFF]/ },
  { id: "ml", re: /[\u0D00-\u0D7F]/ },
  { id: "bn", re: /[\u0980-\u09FF]/ },
  { id: "en", re: /[A-Za-z]/ },
];

export type LangResult = {
  primary: string;
  secondary?: string;
  confidence: number;
  scripts: Record<string, number>;
};

export function detectLanguage(text: string): LangResult {
  const counts: Record<string, number> = {};
  let letters = 0;
  for (const { id, re } of RANGES) {
    const m = text.match(new RegExp(re.source, "g"));
    const n = m?.length ?? 0;
    if (n > 0) counts[id] = n;
    letters += n;
  }
  if (letters === 0) return { primary: "unknown", confidence: 0, scripts: counts };

  const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const [primary, pCount] = sorted[0]!;
  const [secondary, sCount] = sorted[1] ?? [undefined, 0];
  const confidence = pCount / letters;
  const codeSwitch = secondary && sCount / letters > 0.15;
  return {
    primary: codeSwitch ? `${primary}-${secondary}` : primary,
    secondary: codeSwitch ? secondary : undefined,
    confidence: Math.round(confidence * 100) / 100,
    scripts: counts,
  };
}
