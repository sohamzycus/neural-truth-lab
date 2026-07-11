"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import * as tf from "@tensorflow/tfjs";
import { generateConcentricRings, type RingDataset } from "@/datasets/concentric-rings";
import {
  createBinaryClassifier,
  disposeModel,
} from "@/training/models/binary-classifier";
import {
  computeDecisionGrid,
  confusionMatrix,
  predictLabels,
  readMetric,
} from "@/training/metrics";
import { markLabComplete } from "@/lib/progress-storage";
import type { EpochSnapshot } from "@/types/training";

const DEFAULT_EPOCHS = 100;
const DEFAULT_BATCH = 32;
const DEFAULT_LR = 0.03;

export type TrainingStatus = "idle" | "training" | "complete";

interface ActivationsLabState {
  dataset: RingDataset;
  historyA: EpochSnapshot[];
  historyB: EpochSnapshot[];
  currentEpoch: number;
  status: TrainingStatus;
  seed: number;
  learningRate: number;
  tfReady: boolean;
}

export function useActivationsLab(): {
  dataset: RingDataset;
  historyA: EpochSnapshot[];
  historyB: EpochSnapshot[];
  snapshotA: EpochSnapshot | null;
  snapshotB: EpochSnapshot | null;
  currentEpoch: number;
  status: TrainingStatus;
  seed: number;
  learningRate: number;
  tfReady: boolean;
  maxEpoch: number;
  setCurrentEpoch: (epoch: number) => void;
  setSeed: (seed: number) => void;
  setLearningRate: (lr: number) => void;
  trainBoth: () => Promise<void>;
  reset: () => void;
  replay: () => void;
  stopReplay: () => void;
  isReplaying: boolean;
} {
  const [state, setState] = useState<ActivationsLabState>(() => ({
    dataset: generateConcentricRings(42),
    historyA: [],
    historyB: [],
    currentEpoch: 0,
    status: "idle",
    seed: 42,
    learningRate: DEFAULT_LR,
    tfReady: false,
  }));

  const modelARef = useRef<tf.LayersModel | null>(null);
  const modelBRef = useRef<tf.LayersModel | null>(null);
  const trainingRef = useRef(false);
  const replayRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [isReplaying, setIsReplaying] = useState(false);

  const initModels = useCallback((lr: number) => {
    disposeModel(modelARef.current);
    disposeModel(modelBRef.current);
    modelARef.current = createBinaryClassifier("linear", lr);
    modelBRef.current = createBinaryClassifier("relu", lr);
  }, []);

  useEffect(() => {
    let mounted = true;
    void tf.setBackend("webgl").then(() => {
      if (mounted) {
        initModels(DEFAULT_LR);
        setState((s) => ({ ...s, tfReady: true }));
      }
    });
    return () => {
      mounted = false;
      disposeModel(modelARef.current);
      disposeModel(modelBRef.current);
      modelARef.current = null;
      modelBRef.current = null;
      if (replayRef.current) clearInterval(replayRef.current);
    };
  }, [initModels]);

  const captureSnapshot = useCallback(
    (
      model: tf.LayersModel,
      epoch: number,
      dataset: RingDataset,
      history: tf.History
    ): EpochSnapshot => {
      const preds = predictLabels(
        model,
        dataset.features,
        dataset.metadata.count
      );
      return {
        epoch,
        loss: readMetric(history, "loss"),
        accuracy: readMetric(history, "accuracy"),
        decisionGrid: computeDecisionGrid(model),
        confusionMatrix: confusionMatrix(dataset.labels, preds),
      };
    },
    []
  );

  const reset = useCallback(() => {
    trainingRef.current = false;
    if (replayRef.current) clearInterval(replayRef.current);
    setIsReplaying(false);
    setState((s) => {
      initModels(s.learningRate);
      const dataset = generateConcentricRings(s.seed);
      return {
        ...s,
        dataset,
        historyA: [],
        historyB: [],
        currentEpoch: 0,
        status: "idle",
      };
    });
  }, [initModels]);

  const setSeed = useCallback(
    (seed: number) => {
      initModels(state.learningRate);
      setState((s) => ({
        ...s,
        seed,
        dataset: generateConcentricRings(seed),
        historyA: [],
        historyB: [],
        currentEpoch: 0,
        status: "idle",
      }));
    },
    [initModels, state.learningRate]
  );

  const trainBoth = useCallback(async () => {
    if (trainingRef.current || !state.tfReady) return;
    trainingRef.current = true;

    const dataset = generateConcentricRings(state.seed);
    initModels(state.learningRate);
    const modelA = modelARef.current!;
    const modelB = modelBRef.current!;

    const xs = tf.tensor2d(dataset.features, [dataset.metadata.count, 2]);
    const ys = tf.tensor2d(dataset.labels, [dataset.metadata.count, 1]);

    const historyA: EpochSnapshot[] = [];
    const historyB: EpochSnapshot[] = [];

    setState((s) => ({
      ...s,
      dataset,
      historyA: [],
      historyB: [],
      currentEpoch: 0,
      status: "training",
    }));

    try {
      for (let epoch = 1; epoch <= DEFAULT_EPOCHS; epoch++) {
        if (!trainingRef.current) break;

        const histA = await modelA.fit(xs, ys, {
          epochs: 1,
          batchSize: DEFAULT_BATCH,
          shuffle: true,
          verbose: 0,
        });
        const snapA = captureSnapshot(modelA, epoch, dataset, histA);
        historyA.push(snapA);

        const histB = await modelB.fit(xs, ys, {
          epochs: 1,
          batchSize: DEFAULT_BATCH,
          shuffle: true,
          verbose: 0,
        });
        const snapB = captureSnapshot(modelB, epoch, dataset, histB);
        historyB.push(snapB);

        setState((s) => ({
          ...s,
          historyA: [...historyA],
          historyB: [...historyB],
          currentEpoch: epoch,
        }));

        await tf.nextFrame();
      }

      if (trainingRef.current) {
        markLabComplete("activations");
        setState((s) => ({ ...s, status: "complete" }));
      }
    } finally {
      xs.dispose();
      ys.dispose();
      trainingRef.current = false;
    }
  }, [captureSnapshot, initModels, state.seed, state.learningRate, state.tfReady]);

  const setCurrentEpoch = useCallback((epoch: number) => {
    setState((s) => ({ ...s, currentEpoch: epoch }));
  }, []);

  const replay = useCallback(() => {
    if (replayRef.current) clearInterval(replayRef.current);
    setIsReplaying(true);
    let epoch = 0;
    const max = Math.min(state.historyA.length, state.historyB.length);
    if (max === 0) {
      setIsReplaying(false);
      return;
    }
    setCurrentEpoch(0);
    replayRef.current = setInterval(() => {
      epoch += 1;
      setCurrentEpoch(epoch);
      if (epoch >= max) {
        if (replayRef.current) clearInterval(replayRef.current);
        setIsReplaying(false);
      }
    }, 50);
  }, [setCurrentEpoch, state.historyA.length, state.historyB.length]);

  const stopReplay = useCallback(() => {
    if (replayRef.current) clearInterval(replayRef.current);
    setIsReplaying(false);
  }, []);

  const maxEpoch = Math.max(state.historyA.length, state.historyB.length);
  const idx = Math.max(0, state.currentEpoch - 1);

  return {
    dataset: state.dataset,
    historyA: state.historyA,
    historyB: state.historyB,
    snapshotA: state.historyA[idx] ?? null,
    snapshotB: state.historyB[idx] ?? null,
    currentEpoch: state.currentEpoch,
    status: state.status,
    seed: state.seed,
    learningRate: state.learningRate,
    tfReady: state.tfReady,
    maxEpoch,
    setCurrentEpoch,
    setSeed,
    setLearningRate: (lr: number) => setState((s) => ({ ...s, learningRate: lr })),
    trainBoth,
    reset,
    replay,
    stopReplay,
    isReplaying,
  };
}
