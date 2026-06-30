"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import * as tf from "@tensorflow/tfjs";
import {
  DATASET_SIZES,
  generateNoisyClassification,
  sizeLabel,
  type DatasetSize,
} from "@/datasets/noisy-classification";
import {
  createLargeMlp,
  datasetToTensors,
  disposeModel,
} from "@/training/models/large-mlp";
import { computeDecisionGrid } from "@/training/metrics";
import { markLabComplete } from "@/lib/progress-storage";
import type { GeneralizationRun, GeneralizationSnapshot } from "@/types/training";

const EPOCHS = 150;

export type TrainingStatus = "idle" | "training" | "complete";

function readHist(history: tf.History, key: string): number {
  const values = history.history[key];
  const v = values?.[0];
  return typeof v === "number" ? v : 0;
}

export function useGeneralizationLab(): {
  selectedSize: DatasetSize;
  selectedIndex: number;
  setSelectedIndex: (index: number) => void;
  run: GeneralizationRun | null;
  runs: Partial<Record<DatasetSize, GeneralizationRun>>;
  snapshot: GeneralizationSnapshot | null;
  currentEpoch: number;
  status: TrainingStatus;
  tfReady: boolean;
  trainingLabel: string;
  seed: number;
  setSeed: (seed: number) => void;
  setCurrentEpoch: (epoch: number) => void;
  trainAllSizes: () => Promise<void>;
  reset: () => void;
  replaySizes: () => void;
  stopReplay: () => void;
  isReplaying: boolean;
  gap: number;
} {
  const [runs, setRuns] = useState<Partial<Record<DatasetSize, GeneralizationRun>>>(
    {}
  );
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [currentEpoch, setCurrentEpoch] = useState(0);
  const [status, setStatus] = useState<TrainingStatus>("idle");
  const [tfReady, setTfReady] = useState(false);
  const [trainingLabel, setTrainingLabel] = useState("");
  const [seed, setSeedState] = useState(42);
  const [isReplaying, setIsReplaying] = useState(false);

  const trainingRef = useRef(false);
  const replayRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const selectedSize = DATASET_SIZES[selectedIndex];

  useEffect(() => {
    let mounted = true;
    void tf.setBackend("webgl").then(() => {
      if (mounted) setTfReady(true);
    });
    return () => {
      mounted = false;
      if (replayRef.current) clearInterval(replayRef.current);
    };
  }, []);

  const trainSize = useCallback(
    async (size: DatasetSize, datasetSeed: number): Promise<GeneralizationRun> => {
      const dataset = generateNoisyClassification(size, datasetSeed);
      const model = createLargeMlp();
      const { xs: trainX, ys: trainY } = datasetToTensors(
        dataset.trainFeatures,
        dataset.trainLabels,
        dataset.trainCount
      );
      const { xs: valX, ys: valY } = datasetToTensors(
        dataset.valFeatures,
        dataset.valLabels,
        dataset.valCount
      );

      const batchSize = Math.max(1, Math.min(32, Math.floor(dataset.trainCount / 2)));
      const history: GeneralizationSnapshot[] = [];

      try {
        for (let epoch = 1; epoch <= EPOCHS; epoch++) {
          if (!trainingRef.current) break;

          const hist = await model.fit(trainX, trainY, {
            epochs: 1,
            batchSize,
            shuffle: true,
            validationData: [valX, valY],
            verbose: 0,
          });

          const snap: GeneralizationSnapshot = {
            epoch,
            trainLoss: readHist(hist, "loss"),
            valLoss: readHist(hist, "val_loss"),
            trainAccuracy:
              readHist(hist, "accuracy") || readHist(hist, "acc"),
            valAccuracy:
              readHist(hist, "val_accuracy") || readHist(hist, "val_acc"),
          };

          if (epoch === EPOCHS) {
            snap.decisionGrid = computeDecisionGrid(model);
          }

          history.push(snap);
          await tf.nextFrame();
        }
      } finally {
        trainX.dispose();
        trainY.dispose();
        valX.dispose();
        valY.dispose();
        disposeModel(model);
      }

      return { size, history, dataset };
    },
    []
  );

  const trainAllSizes = useCallback(async () => {
    if (!tfReady || trainingRef.current) return;
    trainingRef.current = true;
    setRuns({});
    setStatus("training");
    setCurrentEpoch(0);

    const nextRuns: Partial<Record<DatasetSize, GeneralizationRun>> = {};

    try {
      for (const size of DATASET_SIZES) {
        if (!trainingRef.current) break;
        setTrainingLabel(
          `Training ${sizeLabel(size)} dataset (${size.toLocaleString()} samples)…`
        );
        const run = await trainSize(size, seed);
        nextRuns[size] = run;
        setRuns({ ...nextRuns });
        setSelectedIndex(DATASET_SIZES.indexOf(size));
        setCurrentEpoch(EPOCHS);
      }

      if (trainingRef.current) {
        markLabComplete("generalization");
        setStatus("complete");
        setTrainingLabel("");
      }
    } finally {
      trainingRef.current = false;
    }
  }, [seed, tfReady, trainSize]);

  const reset = useCallback(() => {
    trainingRef.current = false;
    if (replayRef.current) clearInterval(replayRef.current);
    setIsReplaying(false);
    setRuns({});
    setCurrentEpoch(0);
    setSelectedIndex(0);
    setStatus("idle");
    setTrainingLabel("");
  }, []);

  const setSeed = useCallback((next: number) => {
    setSeedState(next);
    setRuns({});
    setCurrentEpoch(0);
    setStatus("idle");
  }, []);

  const run = runs[selectedSize] ?? null;

  const snapshot = useMemo(() => {
    if (!run) return null;
    return (
      [...run.history].reverse().find((s) => s.epoch <= currentEpoch) ??
      run.history[run.history.length - 1] ??
      null
    );
  }, [run, currentEpoch]);

  const gap = snapshot ? Math.max(0, snapshot.valLoss - snapshot.trainLoss) : 0;

  const replaySizes = useCallback(() => {
    if (Object.keys(runs).length < 2) return;
    if (replayRef.current) clearInterval(replayRef.current);
    setIsReplaying(true);
    let i = 0;
    setSelectedIndex(0);
    setCurrentEpoch(EPOCHS);
    replayRef.current = setInterval(() => {
      i += 1;
      if (i >= DATASET_SIZES.length) {
        if (replayRef.current) clearInterval(replayRef.current);
        setIsReplaying(false);
        return;
      }
      setSelectedIndex(i);
      setCurrentEpoch(EPOCHS);
    }, 2000);
  }, [runs]);

  const stopReplay = useCallback(() => {
    if (replayRef.current) clearInterval(replayRef.current);
    setIsReplaying(false);
  }, []);

  return {
    selectedSize,
    selectedIndex,
    setSelectedIndex: (index: number) => {
      setSelectedIndex(index);
      setCurrentEpoch(EPOCHS);
    },
    run,
    runs,
    snapshot,
    currentEpoch,
    status,
    tfReady,
    trainingLabel,
    seed,
    setSeed,
    setCurrentEpoch,
    trainAllSizes,
    reset,
    replaySizes,
    stopReplay,
    isReplaying,
    gap,
  };
}
