export interface EpochSnapshot {
  epoch: number;
  loss: number;
  accuracy: number;
  validationLoss?: number;
  validationAccuracy?: number;
  decisionGrid?: Float32Array;
  embeddings?: Float32Array;
  confusionMatrix?: number[][];
  weightMatrices?: number[][][];
  combinedWeights?: number[][];
}

export interface EmbeddingSnapshot {
  epoch: number;
  loss: number;
  accuracy: number;
  points: { token: string; tokenId: number; x: number; y: number }[];
  embeddings: Float32Array;
}

export interface GeneralizationSnapshot {
  epoch: number;
  trainLoss: number;
  valLoss: number;
  trainAccuracy: number;
  valAccuracy: number;
  decisionGrid?: Float32Array;
}

export interface GeneralizationRun {
  size: number;
  history: GeneralizationSnapshot[];
  dataset: {
    trainFeatures: Float32Array;
    trainLabels: Float32Array;
    valFeatures: Float32Array;
    valLabels: Float32Array;
    trainCount: number;
    valCount: number;
    totalSize: number;
  };
}

export interface TrainingConfig {
  epochs: number;
  learningRate: number;
  batchSize: number;
}

export interface ModelConfig extends TrainingConfig {
  name: string;
}
