import * as tf from "@tensorflow/tfjs";

export function matMul(a: number[][], b: number[][]): number[][] {
  const rows = a.length;
  const cols = b[0]?.length ?? 0;
  const inner = b.length;
  const result = Array.from({ length: rows }, () => Array(cols).fill(0));
  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      for (let k = 0; k < inner; k++) {
        result[i][j] += a[i][k] * b[k][j];
      }
    }
  }
  return result;
}

export function collapseLinearWeights(kernels: number[][][]): number[][] {
  return kernels.reduce((acc, kernel) => matMul(acc, kernel));
}

export function extractKernels(model: tf.LayersModel): number[][][] {
  const kernels: number[][][] = [];
  for (const layer of model.layers) {
    const weights = layer.getWeights();
    if (weights.length > 0) {
      kernels.push(weights[0].arraySync() as number[][]);
    }
  }
  return kernels;
}

export function kernelLabels(kernels: number[][][]): string[] {
  return kernels.map((k, i) => {
    const rows = k.length;
    const cols = k[0]?.length ?? 0;
    return `W${i + 1}: ${rows}×${cols}`;
  });
}

// ponytail: self-check — run in dev: npx tsx -e "import './training/weight-collapse'"
if (typeof process !== "undefined" && process.env.NODE_ENV === "test") {
  const p = collapseLinearWeights([
    [
      [1, 2],
      [3, 4],
    ],
    [
      [0.5, 1],
      [1.5, 2],
    ],
  ]);
  console.assert(p[0][0] === 3.5, "weight collapse check");
}
