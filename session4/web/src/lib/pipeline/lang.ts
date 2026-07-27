import { fastTextPredict, charNgramFeatures } from "./fasttext";
import { scriptDetect } from "./script";

export type LangResult = {
  primary: string;
  secondary?: string;
  confidence: number;
  fastTextLabel: string;
  fastTextConfidence: number;
  fastTextProbabilities: Record<string, number>;
  script: Record<string, number>;
  method: string;
};

/** FastText char-ngram model + script heuristics for code-switch tags. */
export function detectLanguage(text: string): LangResult {
  const ft = fastTextPredict(text);
  const script = scriptDetect(text);

  const sorted = Object.entries(script.counts).sort((a, b) => b[1] - a[1]);
  const scriptPrimary = sorted[0]?.[0];
  const scriptSecondary = sorted[1]?.[0];
  const scriptShare = sorted[1] ? sorted[1][1] / Math.max(script.total, 1) : 0;

  let primary = ft.label;
  let secondary: string | undefined;
  if (scriptShare > 0.15 && scriptSecondary && scriptSecondary !== ft.label) {
    primary = `${ft.label}-${scriptSecondary}`;
    secondary = scriptSecondary;
  } else if (ft.confidence < 0.45 && scriptPrimary) {
    primary = scriptPrimary;
  }

  return {
    primary,
    secondary,
    confidence: Math.round(ft.confidence * 100) / 100,
    fastTextLabel: ft.label,
    fastTextConfidence: ft.confidence,
    fastTextProbabilities: ft.probabilities,
    script: script.counts,
    method: "fasttext-char-ngram+script-heuristic",
  };
}

export { charNgramFeatures };
