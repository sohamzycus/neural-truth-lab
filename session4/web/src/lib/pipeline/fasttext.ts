/**
 * FastText-style character n-gram language ID (Bojanowski et al. subword features + linear classifier).
 * Weights trained offline: npm run train:fasttext-lang → public/data/fasttext_lang_model.json
 */
import modelData from "./data/fasttext_lang_model.json";

export type FastTextLangModel = {
  method: string;
  dim: number;
  nmin: number;
  nmax: number;
  labels: string[];
  weights: number[][];
  bias: number[];
};

const model = modelData as FastTextLangModel;

function hashNgram(s: string, dim: number): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return ((h % dim) + dim) % dim;
}

export function charNgramFeatures(text: string): Float32Array {
  const t = ` ${text.toLowerCase().normalize("NFKC")} `;
  const v = new Float32Array(model.dim);
  for (let n = model.nmin; n <= model.nmax; n++) {
    for (let i = 0; i <= t.length - n; i++) {
      v[hashNgram(t.slice(i, i + n), model.dim)]! += 1;
    }
  }
  let norm = 0;
  for (let i = 0; i < v.length; i++) norm += v[i]! * v[i]!;
  norm = Math.sqrt(norm) || 1;
  for (let i = 0; i < v.length; i++) v[i]! /= norm;
  return v;
}

function softmax(scores: number[]): number[] {
  const max = Math.max(...scores);
  const ex = scores.map((s) => Math.exp(s - max));
  const sum = ex.reduce((a, b) => a + b, 0);
  return ex.map((e) => e / sum);
}

export type FastTextLangResult = {
  label: string;
  confidence: number;
  probabilities: Record<string, number>;
  method: string;
};

export function fastTextPredict(text: string): FastTextLangResult {
  const feats = charNgramFeatures(text);
  const scores = model.labels.map((_, li) => {
    let s = model.bias[li] ?? 0;
    const w = model.weights[li]!;
    for (let i = 0; i < model.dim; i++) s += w[i]! * feats[i]!;
    return s;
  });
  const probs = softmax(scores);
  let best = 0;
  for (let i = 1; i < probs.length; i++) if (probs[i]! > probs[best]!) best = i;
  const probabilities: Record<string, number> = {};
  model.labels.forEach((l, i) => {
    probabilities[l] = Math.round(probs[i]! * 1000) / 1000;
  });
  return {
    label: model.labels[best]!,
    confidence: probs[best]!,
    probabilities,
    method: model.method,
  };
}

export function getFastTextModelMeta() {
  return { labels: model.labels, dim: model.dim, method: model.method };
}
