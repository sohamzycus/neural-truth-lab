export interface RingDataset {
  features: Float32Array;
  labels: Float32Array;
  metadata: { inner: number; outer: number; noise: number; count: number };
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

export function generateConcentricRings(
  seed = 42,
  count = 300,
  innerRadius = 0.5,
  outerRadius = 1.0,
  noise = 0.15
): RingDataset {
  const rand = mulberry32(seed);
  const half = count / 2;
  const features = new Float32Array(count * 2);
  const labels = new Float32Array(count);
  let maxAbs = 0;

  for (let i = 0; i < count; i++) {
    const isOuter = i >= half;
    const angle = rand() * Math.PI * 2;
    const radius = (isOuter ? outerRadius : innerRadius) + gaussian(rand) * noise;
    const x = radius * Math.cos(angle);
    const y = radius * Math.sin(angle);
    features[i * 2] = x;
    features[i * 2 + 1] = y;
    labels[i] = isOuter ? 1 : 0;
    maxAbs = Math.max(maxAbs, Math.abs(x), Math.abs(y));
  }

  const scale = maxAbs > 0 ? 1 / maxAbs : 1;
  for (let i = 0; i < features.length; i++) {
    features[i] *= scale;
  }

  return {
    features,
    labels,
    metadata: { inner: innerRadius, outer: outerRadius, noise, count },
  };
}
