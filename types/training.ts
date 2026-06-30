export interface EpochSnapshot {
  epoch: number;
  loss: number;
  accuracy: number;
  validationLoss?: number;
  validationAccuracy?: number;
  decisionGrid?: Float32Array;
  embeddings?: Float32Array;
  confusionMatrix?: number[][];
}

export interface TrainingConfig {
  epochs: number;
  learningRate: number;
  batchSize: number;
}

export interface ModelConfig extends TrainingConfig {
  name: string;
}
