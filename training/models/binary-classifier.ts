import * as tf from "@tensorflow/tfjs";

export type ActivationType = "linear" | "relu";

export function createBinaryClassifier(
  activation: ActivationType,
  learningRate = 0.03
): tf.LayersModel {
  const model = tf.sequential();
  model.add(
    tf.layers.dense({
      inputShape: [2],
      units: 16,
      activation: activation === "linear" ? "linear" : "relu",
    })
  );
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
