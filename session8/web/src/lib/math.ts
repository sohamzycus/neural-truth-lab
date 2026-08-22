export function softmax(arr: number[]): number[] {
  const max = Math.max(...arr);
  const exps = arr.map((x) => Math.exp(x - max));
  const sum = exps.reduce((a, b) => a + b, 0);
  return exps.map((e) => e / sum);
}

export function dot(a: number[], b: number[]): number {
  return a.reduce((s, v, i) => s + v * b[i], 0);
}

export function formatPairs(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

export function pairCount(n: number): number {
  return n * n;
}

export function kvCacheBytes(
  seqLen: number,
  layers: number,
  kvHeads: number,
  headDim: number,
  bytesPerElem = 2,
): number {
  return seqLen * layers * kvHeads * headDim * 2 * bytesPerElem;
}

export const SEQ_PRESETS = [32, 128, 512, 2048, 8192, 32768, 131072, 1000000] as const;

export function seqLabel(n: number): string {
  if (n >= 1_000_000) return "1M";
  if (n >= 1000) return `${n / 1000}K`;
  return String(n);
}

export function rotate2D(x: number, y: number, angle: number): [number, number] {
  const c = Math.cos(angle);
  const s = Math.sin(angle);
  return [x * c - y * s, x * s + y * c];
}
