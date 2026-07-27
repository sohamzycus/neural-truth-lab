/**
 * Train FastText-style char-ngram language classifier.
 * npm run train:fasttext-lang
 */
import { writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dir = dirname(fileURLToPath(import.meta.url));
const outPath = join(__dir, "../src/lib/pipeline/data/fasttext_lang_model.json");

const DIM = 512;
const NMIN = 2;
const NMAX = 5;
const LABELS = ["en", "hi", "ta", "ml", "bn"];
const EPOCHS = 80;
const LR = 0.35;

const TRAIN = {
  en: [
    "Indian Robin on fence with chee-chee call",
    "Black Drongo mobbing raptor at agricultural edge",
    "Great Hornbill flying over forest canopy morning",
    "Sarus Crane pair in wetland Bharatpur",
    "heard only warbler near scrub edge",
    "Purple Sunbird at nectar bush garden Pune",
    "Rose-ringed Parakeet flock on wire urban",
    "White-throated Kingfisher dive fishing pond",
  ],
  hi: [
    "एशियन कोयल की आवाज सुबह सुनाई दी",
    "काला ड्रोंगो खेत के किनारे बैठा था",
    "भारतीय रॉबिन झाड़ी के पास",
    "मोर नृत्य कर रहा था मानसून में",
    "सारस जोड़ा दिखा कच्छ में",
  ],
  ta: [
    "அரசாங்கப் பறவை காட்டில் காணப்பட்டது",
    "தமிழ்நாடு வால்பாறையில் குருவி",
    "காலை நேரத்தில் கோகை அழைப்பு",
  ],
  ml: [
    "മലയാളം കുറിപ്പ് തേക്കട വനത്തിൽ",
    "കാക്ക കാണാൻ ലഭിച്ചു",
    "പ്രഭാതത്തിൽ കിളി ശബ്ദം",
  ],
  bn: [
    "সুন্দরবনে পাখির ডাক শোনা গেল",
    "কাক ধানক্ষেতে বসে আছে",
    "বাংলা নোট চিলিকা হ্রদে",
  ],
};

function hashNgram(s) {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return ((h % DIM) + DIM) % DIM;
}

function features(text) {
  const t = ` ${text.toLowerCase().normalize("NFKC")} `;
  const v = new Float32Array(DIM);
  for (let n = NMIN; n <= NMAX; n++) {
    for (let i = 0; i <= t.length - n; i++) v[hashNgram(t.slice(i, i + n))] += 1;
  }
  let norm = 0;
  for (let i = 0; i < DIM; i++) norm += v[i] * v[i];
  norm = Math.sqrt(norm) || 1;
  for (let i = 0; i < DIM; i++) v[i] /= norm;
  return v;
}

const weights = LABELS.map(() => new Float32Array(DIM));
const bias = new Float32Array(LABELS.length);

for (let epoch = 0; epoch < EPOCHS; epoch++) {
  for (const [label, samples] of Object.entries(TRAIN)) {
    const li = LABELS.indexOf(label);
    for (const sample of samples) {
      const x = features(sample);
      const scores = LABELS.map((_, i) => {
        let s = bias[i];
        for (let d = 0; d < DIM; d++) s += weights[i][d] * x[d];
        return s;
      });
      const max = Math.max(...scores);
      const ex = scores.map((s) => Math.exp(s - max));
      const sum = ex.reduce((a, b) => a + b, 0);
      const probs = ex.map((e) => e / sum);
      for (let i = 0; i < LABELS.length; i++) {
        const err = probs[i] - (i === li ? 1 : 0);
        bias[i] -= LR * err;
        for (let d = 0; d < DIM; d++) weights[i][d] -= LR * err * x[d];
      }
    }
  }
}

function predict(text) {
  const x = features(text);
  let best = 0;
  let bestScore = -Infinity;
  for (let i = 0; i < LABELS.length; i++) {
    let s = bias[i];
    for (let d = 0; d < DIM; d++) s += weights[i][d] * x[d];
    if (s > bestScore) {
      bestScore = s;
      best = i;
    }
  }
  return LABELS[best];
}

let correct = 0;
let total = 0;
for (const [label, samples] of Object.entries(TRAIN)) {
  for (const s of samples) {
    total++;
    if (predict(s) === label) correct++;
  }
}

const model = {
  method: "fasttext-char-ngram-linear",
  dim: DIM,
  nmin: NMIN,
  nmax: NMAX,
  labels: LABELS,
  weights: weights.map((w) => [...w]),
  bias: [...bias],
  trainAccuracy: Math.round((correct / total) * 1000) / 1000,
  trainSamples: total,
};

writeFileSync(outPath, JSON.stringify(model));
console.log(`Wrote ${outPath} — train accuracy ${(model.trainAccuracy * 100).toFixed(1)}% (${correct}/${total})`);
