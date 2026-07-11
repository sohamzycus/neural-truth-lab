export const DATASET_SIZES = [20, 200, 2000, 20000] as const;
export type DatasetSize = (typeof DATASET_SIZES)[number];

export interface NoisyDataset {
  trainFeatures: Float32Array;
  trainLabels: Float32Array;
  valFeatures: Float32Array;
  valLabels: Float32Array;
  trainCount: number;
  valCount: number;
  totalSize: number;
}

function mulberry32(seed: number): () => number {
  let s = seed;
  return () => {
    s |= 0;
    s = (s + 0x6d2b79f5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function gaussian(rand: () => number): number {
  const u1 = rand() || 1e-10;
  const u2 = rand();
  return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
}

function generateMoons(
  n: number,
  rand: () => number,
  featureNoise = 0.1
): { features: Float32Array; labels: Float32Array } {
  const features = new Float32Array(n * 2);
  const labels = new Float32Array(n);
  const half = Math.floor(n / 2);

  for (let i = 0; i < n; i++) {
    const isSecond = i >= half;
    const angle = rand() * Math.PI;
    const r = 1 + gaussian(rand) * featureNoise;
    const x = r * Math.cos(angle) + (isSecond ? 1 : 0);
    const y = r * Math.sin(angle) + (isSecond ? -0.5 : 0.5);
    features[i * 2] = x;
    features[i * 2 + 1] = y;
    labels[i] = isSecond ? 1 : 0;
  }

  return { features, labels };
}

function shuffle<T>(arr: T[], rand: () => number): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export function generateNoisyClassification(
  totalSize: number,
  seed = 42,
  labelNoiseRate = 0.07,
  featureNoise = 0.1
): NoisyDataset {
  const rand = mulberry32(seed);
  const { features, labels } = generateMoons(totalSize, rand, featureNoise);

  for (let i = 0; i < labels.length; i++) {
    if (rand() < labelNoiseRate) {
      labels[i] = 1 - labels[i];
    }
  }

  const indices = shuffle(
    Array.from({ length: totalSize }, (_, i) => i),
    rand
  );
  const trainCount = Math.floor(totalSize * 0.8);
  const valCount = totalSize - trainCount;

  const trainFeatures = new Float32Array(trainCount * 2);
  const trainLabels = new Float32Array(trainCount);
  const valFeatures = new Float32Array(valCount * 2);
  const valLabels = new Float32Array(valCount);

  for (let i = 0; i < trainCount; i++) {
    const idx = indices[i];
    trainFeatures[i * 2] = features[idx * 2];
    trainFeatures[i * 2 + 1] = features[idx * 2 + 1];
    trainLabels[i] = labels[idx];
  }
  for (let i = 0; i < valCount; i++) {
    const idx = indices[trainCount + i];
    valFeatures[i * 2] = features[idx * 2];
    valFeatures[i * 2 + 1] = features[idx * 2 + 1];
    valLabels[i] = labels[idx];
  }

  let maxAbs = 0;
  for (let i = 0; i < features.length; i++) {
    maxAbs = Math.max(maxAbs, Math.abs(features[i]));
  }
  const scale = maxAbs > 0 ? 1.2 / maxAbs : 1;
  for (let i = 0; i < trainFeatures.length; i++) trainFeatures[i] *= scale;
  for (let i = 0; i < valFeatures.length; i++) valFeatures[i] *= scale;

  return {
    trainFeatures,
    trainLabels,
    valFeatures,
    valLabels,
    trainCount,
    valCount,
    totalSize,
  };
}

export function sizeLabel(size: DatasetSize): string {
  const map: Record<DatasetSize, string> = {
    20: "Tiny",
    200: "Small",
    2000: "Medium",
    20000: "Large",
  };
  return map[size];
}
