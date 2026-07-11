import * as tf from "@tensorflow/tfjs";

export type DepthModelKind = "one-linear" | "five-linear" | "five-relu";

export function createDepthModel(
  kind: DepthModelKind,
  learningRate = 0.03
): tf.LayersModel {
  const model = tf.sequential();

  if (kind === "one-linear") {
    model.add(tf.layers.dense({ inputShape: [2], units: 1, activation: "sigmoid" }));
  } else {
    const hiddenActivation = kind === "five-linear" ? "linear" : "relu";
    model.add(
      tf.layers.dense({
        inputShape: [2],
        units: 8,
        activation: hiddenActivation,
      })
    );
    for (let i = 0; i < 3; i++) {
      model.add(tf.layers.dense({ units: 8, activation: hiddenActivation }));
    }
    model.add(tf.layers.dense({ units: 1, activation: "sigmoid" }));
  }

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
