"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import * as tf from "@tensorflow/tfjs";
import { generateConcentricRings, type RingDataset } from "@/datasets/concentric-rings";
import {
  createDepthModel,
  disposeModel,
  type DepthModelKind,
} from "@/training/models/depth-models";
import {
  collapseLinearWeights,
  extractKernels,
} from "@/training/weight-collapse";
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

export function useDepthLab(): {
  dataset: RingDataset;
  history1: EpochSnapshot[];
  history2: EpochSnapshot[];
  history3: EpochSnapshot[];
  snapshot1: EpochSnapshot | null;
  snapshot2: EpochSnapshot | null;
  snapshot3: EpochSnapshot | null;
  currentEpoch: number;
  status: TrainingStatus;
  seed: number;
  tfReady: boolean;
  maxEpoch: number;
  trainingLabel: string;
  setCurrentEpoch: (epoch: number) => void;
  setSeed: (seed: number) => void;
  compareAll: () => Promise<void>;
  reset: () => void;
  replay: () => void;
  stopReplay: () => void;
  isReplaying: boolean;
} {
  const [dataset, setDataset] = useState<RingDataset>(() =>
    generateConcentricRings(42)
  );
  const [history1, setHistory1] = useState<EpochSnapshot[]>([]);
  const [history2, setHistory2] = useState<EpochSnapshot[]>([]);
  const [history3, setHistory3] = useState<EpochSnapshot[]>([]);
  const [currentEpoch, setCurrentEpoch] = useState(0);
  const [status, setStatus] = useState<TrainingStatus>("idle");
  const [seed, setSeedState] = useState(42);
  const [tfReady, setTfReady] = useState(false);
  const [trainingLabel, setTrainingLabel] = useState("");
  const [isReplaying, setIsReplaying] = useState(false);

  const model1Ref = useRef<tf.LayersModel | null>(null);
  const model2Ref = useRef<tf.LayersModel | null>(null);
  const model3Ref = useRef<tf.LayersModel | null>(null);
  const trainingRef = useRef(false);
  const replayRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const initModels = useCallback((lr: number) => {
    disposeModel(model1Ref.current);
    disposeModel(model2Ref.current);
    disposeModel(model3Ref.current);
    model1Ref.current = createDepthModel("one-linear", lr);
    model2Ref.current = createDepthModel("five-linear", lr);
    model3Ref.current = createDepthModel("five-relu", lr);
  }, []);

  useEffect(() => {
    let mounted = true;
    void tf.setBackend("webgl").then(() => {
      if (mounted) {
        initModels(DEFAULT_LR);
        setTfReady(true);
      }
    });
    return () => {
      mounted = false;
      disposeModel(model1Ref.current);
      disposeModel(model2Ref.current);
      disposeModel(model3Ref.current);
      if (replayRef.current) clearInterval(replayRef.current);
    };
  }, [initModels]);

  const captureSnapshot = useCallback(
    (
      model: tf.LayersModel,
      epoch: number,
      data: RingDataset,
      history: tf.History,
      includeWeights: boolean
    ): EpochSnapshot => {
      const preds = predictLabels(model, data.features, data.metadata.count);
      const snap: EpochSnapshot = {
        epoch,
        loss: readMetric(history, "loss"),
        accuracy: readMetric(history, "accuracy"),
        decisionGrid: computeDecisionGrid(model),
        confusionMatrix: confusionMatrix(data.labels, preds),
      };
      if (includeWeights) {
        const kernels = extractKernels(model);
        snap.weightMatrices = kernels;
        snap.combinedWeights = collapseLinearWeights(kernels);
      }
      return snap;
    },
    []
  );

  const trainModel = useCallback(
    async (
      kind: DepthModelKind,
      model: tf.LayersModel,
      data: RingDataset,
      label: string,
      onHistoryUpdate: (history: EpochSnapshot[]) => void
    ): Promise<EpochSnapshot[]> => {
      setTrainingLabel(label);
      const xs = tf.tensor2d(data.features, [data.metadata.count, 2]);
      const ys = tf.tensor2d(data.labels, [data.metadata.count, 1]);
      const history: EpochSnapshot[] = [];
      const includeWeights = kind === "five-linear";

      try {
        for (let epoch = 1; epoch <= DEFAULT_EPOCHS; epoch++) {
          if (!trainingRef.current) break;
          const hist = await model.fit(xs, ys, {
            epochs: 1,
            batchSize: DEFAULT_BATCH,
            shuffle: true,
            verbose: 0,
          });
          const snap = captureSnapshot(model, epoch, data, hist, includeWeights);
          history.push(snap);
          onHistoryUpdate([...history]);
          setCurrentEpoch(epoch);
          await tf.nextFrame();
        }
      } finally {
        xs.dispose();
        ys.dispose();
      }
      return history;
    },
    [captureSnapshot]
  );

  const compareAll = useCallback(async () => {
    if (trainingRef.current || !tfReady) return;
    trainingRef.current = true;
    const data = generateConcentricRings(seed);
    setDataset(data);
    setHistory1([]);
    setHistory2([]);
    setHistory3([]);
    setCurrentEpoch(0);
    setStatus("training");
    initModels(DEFAULT_LR);

    try {
      await trainModel(
        "one-linear",
        model1Ref.current!,
        data,
        "Training model 1 of 3 — 1 Linear Layer",
        setHistory1
      );

      await trainModel(
        "five-linear",
        model2Ref.current!,
        data,
        "Training model 2 of 3 — 5 Linear Layers",
        setHistory2
      );

      await trainModel(
        "five-relu",
        model3Ref.current!,
        data,
        "Training model 3 of 3 — 5 Layers + ReLU",
        setHistory3
      );

      if (trainingRef.current) {
        markLabComplete("depth");
        setStatus("complete");
        setTrainingLabel("");
      }
    } finally {
      trainingRef.current = false;
    }
  }, [initModels, seed, tfReady, trainModel]);

  const reset = useCallback(() => {
    trainingRef.current = false;
    if (replayRef.current) clearInterval(replayRef.current);
    setIsReplaying(false);
    initModels(DEFAULT_LR);
    setDataset(generateConcentricRings(seed));
    setHistory1([]);
    setHistory2([]);
    setHistory3([]);
    setCurrentEpoch(0);
    setStatus("idle");
    setTrainingLabel("");
  }, [initModels, seed]);

  const setSeed = useCallback(
    (next: number) => {
      setSeedState(next);
      setDataset(generateConcentricRings(next));
      setHistory1([]);
      setHistory2([]);
      setHistory3([]);
      setCurrentEpoch(0);
      setStatus("idle");
      initModels(DEFAULT_LR);
    },
    [initModels]
  );

  const replay = useCallback(() => {
    if (replayRef.current) clearInterval(replayRef.current);
    const max = Math.min(history1.length, history2.length, history3.length);
    if (max === 0) return;
    setIsReplaying(true);
    let epoch = 0;
    setCurrentEpoch(0);
    replayRef.current = setInterval(() => {
      epoch += 1;
      setCurrentEpoch(epoch);
      if (epoch >= max) {
        if (replayRef.current) clearInterval(replayRef.current);
        setIsReplaying(false);
      }
    }, 50);
  }, [history1.length, history2.length, history3.length]);

  const stopReplay = useCallback(() => {
    if (replayRef.current) clearInterval(replayRef.current);
    setIsReplaying(false);
  }, []);

  const maxEpoch = Math.max(history1.length, history2.length, history3.length);
  const idx = Math.max(0, currentEpoch - 1);

  return {
    dataset,
    history1,
    history2,
    history3,
    snapshot1: history1[idx] ?? null,
    snapshot2: history2[idx] ?? null,
    snapshot3: history3[idx] ?? null,
    currentEpoch,
    status,
    seed,
    tfReady,
    maxEpoch,
    trainingLabel,
    setCurrentEpoch,
    setSeed,
    compareAll,
    reset,
    replay,
    stopReplay,
    isReplaying,
  };
}
