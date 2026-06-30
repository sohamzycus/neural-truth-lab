import * as tf from "@tensorflow/tfjs";

const GRID_SIZE = 100;
const BOUNDS = 1.2;

export function getGridConfig(): { gridSize: number; bounds: number } {
  return { gridSize: GRID_SIZE, bounds: BOUNDS };
}

export function computeDecisionGrid(model: tf.LayersModel): Float32Array {
  return tf.tidy(() => {
    const step = (2 * BOUNDS) / (GRID_SIZE - 1);
    const coords: number[] = [];
    for (let row = 0; row < GRID_SIZE; row++) {
      for (let col = 0; col < GRID_SIZE; col++) {
        coords.push(-BOUNDS + col * step, -BOUNDS + row * step);
      }
    }
    const input = tf.tensor2d(coords, [GRID_SIZE * GRID_SIZE, 2]);
    const pred = model.predict(input) as tf.Tensor;
    return new Float32Array(pred.dataSync());
  });
}

export function predictLabels(
  model: tf.LayersModel,
  features: Float32Array,
  sampleCount: number
): Float32Array {
  return tf.tidy(() => {
    const input = tf.tensor2d(features, [sampleCount, 2]);
    const pred = model.predict(input) as tf.Tensor;
    return new Float32Array(pred.dataSync());
  });
}

export function confusionMatrix(
  labels: Float32Array,
  predictions: Float32Array,
  threshold = 0.5
): number[][] {
  let tn = 0;
  let fp = 0;
  let fn = 0;
  let tp = 0;
  for (let i = 0; i < labels.length; i++) {
    const actual = labels[i] >= 0.5 ? 1 : 0;
    const pred = predictions[i] >= threshold ? 1 : 0;
    if (actual === 0 && pred === 0) tn++;
    else if (actual === 0 && pred === 1) fp++;
    else if (actual === 1 && pred === 0) fn++;
    else tp++;
  }
  return [
    [tn, fp],
    [fn, tp],
  ];
}

export function readMetric(
  history: tf.History,
  key: "loss" | "accuracy"
): number {
  const values =
    key === "loss"
      ? history.history.loss
      : history.history.accuracy ?? history.history.acc;
  const last = values?.[values.length - 1];
  return typeof last === "number" ? last : 0;
}
