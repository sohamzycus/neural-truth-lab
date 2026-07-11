import * as tf from "@tensorflow/tfjs";

export function createLargeMlp(learningRate = 0.001): tf.LayersModel {
  const model = tf.sequential();
  model.add(tf.layers.dense({ inputShape: [2], units: 64, activation: "relu" }));
  model.add(tf.layers.dense({ units: 64, activation: "relu" }));
  model.add(tf.layers.dense({ units: 32, activation: "relu" }));
  model.add(tf.layers.dense({ units: 1, activation: "sigmoid" }));
  model.compile({
    optimizer: tf.train.adam(learningRate),
    loss: "binaryCrossentropy",
    metrics: ["accuracy"],
  });
  return model;
}

export function disposeModel(model: tf.LayersModel | null): void {
  if (model) model.dispose();
}

export function datasetToTensors(
  features: Float32Array,
  labels: Float32Array,
  count: number
): { xs: tf.Tensor2D; ys: tf.Tensor2D } {
  const xs = tf.tensor2d(features, [count, 2]);
  const ys = tf.tensor2d(labels, [count, 1]);
  return { xs, ys };
}
