import * as tf from "@tensorflow/tfjs";
import type { SyntheticCorpus } from "@/datasets/synthetic-language";

const EMBED_DIM = 16;
const SEQ_LEN = 3;

export function createEmbeddingModel(
  vocabSize: number,
  learningRate = 0.05
): tf.LayersModel {
  const model = tf.sequential();
  model.add(
    tf.layers.embedding({
      inputDim: vocabSize,
      outputDim: EMBED_DIM,
      inputLength: SEQ_LEN,
    })
  );
  model.add(tf.layers.flatten());
  model.add(tf.layers.dense({ units: vocabSize, activation: "softmax" }));
  model.compile({
    optimizer: tf.train.adam(learningRate),
    loss: "categoricalCrossentropy",
    metrics: ["accuracy"],
  });
  return model;
}

export function corpusToTensors(
  corpus: SyntheticCorpus
): { xs: tf.Tensor2D; ys: tf.Tensor2D } {
  const n = corpus.sequences.length;
  const xs = tf.tensor2d(corpus.sequences, [n, SEQ_LEN]);
  const ys = tf.oneHot(
    tf.tensor1d(corpus.targets, "int32"),
    corpus.vocab.length
  ) as tf.Tensor2D;
  return { xs, ys };
}

export function extractEmbeddingMatrix(model: tf.LayersModel): Float32Array {
  const embeddingLayer = model.layers[0];
  const weights = embeddingLayer.getWeights()[0];
  return new Float32Array(weights.dataSync());
}

export function disposeModel(model: tf.LayersModel | null): void {
  if (model) model.dispose();
}

export { EMBED_DIM, SEQ_LEN };
