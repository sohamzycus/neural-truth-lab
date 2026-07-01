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
import { unlockAchievement } from "@/lib/achievements";
import {
  GENERALIZATION_EPOCHS,
  GENERALIZATION_SNAPSHOT_EVERY,
} from "@/lib/lab-demos";
import type { GeneralizationRun, GeneralizationSnapshot } from "@/types/training";

export type TrainingStatus = "idle" | "training" | "complete";

function readLogs(logs: tf.Logs | undefined, key: string): number {
  const v = logs?.[key];
  return typeof v === "number" ? v : 0;
}

function epochsForSize(size: DatasetSize): number {
  return GENERALIZATION_EPOCHS[size] ?? 40;
}

function batchSizeFor(trainCount: number): number {
  return Math.min(128, Math.max(4, Math.floor(trainCount / 4)));
}

export function useGeneralizationLab(): {
  selectedSize: DatasetSize;
  selectedIndex: number;
  setSelectedIndex: (index: number) => void;
  run: GeneralizationRun | null;
  runs: Partial<Record<DatasetSize, GeneralizationRun>>;
  snapshot: GeneralizationSnapshot | null;
  currentEpoch: number;
  maxEpochForRun: number;
  status: TrainingStatus;
  tfReady: boolean;
  trainingLabel: string;
  seed: number;
  setSeed: (seed: number) => void;
  setCurrentEpoch: (epoch: number) => void;
  trainCurrentSize: () => Promise<void>;
  trainAllSizes: () => Promise<void>;
  stopTraining: () => void;
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
  const [maxEpochForRun, setMaxEpochForRun] = useState(0);
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

      const maxEpochs = epochsForSize(size);
      const batchSize = batchSizeFor(dataset.trainCount);
      const history: GeneralizationSnapshot[] = [];

      setMaxEpochForRun(maxEpochs);

      try {
        await model.fit(trainX, trainY, {
          epochs: maxEpochs,
          batchSize,
          shuffle: true,
          validationData: [valX, valY],
          verbose: 0,
          callbacks: {
            onEpochEnd: (epoch, logs) => {
              if (!trainingRef.current) return;

              const epochNum = epoch + 1;
              const snap: GeneralizationSnapshot = {
                epoch: epochNum,
                trainLoss: readLogs(logs, "loss"),
                valLoss: readLogs(logs, "val_loss"),
                trainAccuracy:
                  readLogs(logs, "accuracy") || readLogs(logs, "acc"),
                valAccuracy:
                  readLogs(logs, "val_accuracy") || readLogs(logs, "val_acc"),
              };

              if (
                epochNum % GENERALIZATION_SNAPSHOT_EVERY === 0 ||
                epochNum === maxEpochs
              ) {
                if (epochNum === maxEpochs) {
                  snap.decisionGrid = computeDecisionGrid(model);
                }
                history.push(snap);
              }

              void tf.nextFrame().then(() => {
                setCurrentEpoch(epochNum);
                setTrainingLabel(
                  `${sizeLabel(size)} · epoch ${epochNum}/${maxEpochs}`
                );
              });
            },
          },
        });

        if (history.length === 0 || history[history.length - 1].epoch !== maxEpochs) {
          const snap: GeneralizationSnapshot = {
            epoch: maxEpochs,
            trainLoss: history.at(-1)?.trainLoss ?? 0,
            valLoss: history.at(-1)?.valLoss ?? 0,
            trainAccuracy: history.at(-1)?.trainAccuracy ?? 0,
            valAccuracy: history.at(-1)?.valAccuracy ?? 0,
            decisionGrid: computeDecisionGrid(model),
          };
          history.push(snap);
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

  const finishRun = useCallback(
    (
      size: DatasetSize,
      run: GeneralizationRun,
      nextRuns: Partial<Record<DatasetSize, GeneralizationRun>>
    ): void => {
      nextRuns[size] = run;
      setRuns({ ...nextRuns });
      setSelectedIndex(DATASET_SIZES.indexOf(size));
      setCurrentEpoch(run.history[run.history.length - 1]?.epoch ?? 0);

      if (size === 20) {
        const last = run.history[run.history.length - 1];
        if (last && last.valLoss - last.trainLoss > 0.3) {
          unlockAchievement("memorizer");
        }
      }
    },
    []
  );

  const trainSizes = useCallback(
    async (sizes: DatasetSize[], replaceRuns = false): Promise<void> => {
      if (!tfReady || trainingRef.current) return;
      trainingRef.current = true;
      setStatus("training");

      const nextRuns: Partial<Record<DatasetSize, GeneralizationRun>> = replaceRuns
        ? {}
        : { ...runs };

      try {
        for (const size of sizes) {
          if (!trainingRef.current) break;
          setTrainingLabel(
            `Starting ${sizeLabel(size)} (${size.toLocaleString()} samples)…`
          );
          const run = await trainSize(size, seed);
          finishRun(size, run, nextRuns);
        }

        if (trainingRef.current) {
          const trained = sizes.every((s) => nextRuns[s]);
          if (trained && sizes.length === DATASET_SIZES.length) {
            unlockAchievement("scientist");
            markLabComplete("generalization");
            setStatus("complete");
          }
          setTrainingLabel("");
        }
      } finally {
        trainingRef.current = false;
        setTrainingLabel("");
        setStatus((prev) => (prev === "training" ? "idle" : prev));
      }
    },
    [tfReady, runs, seed, trainSize, finishRun]
  );

  const trainCurrentSize = useCallback(async () => {
    await trainSizes([selectedSize], false);
  }, [trainSizes, selectedSize]);

  const trainAllSizes = useCallback(async () => {
    setCurrentEpoch(0);
    await trainSizes([...DATASET_SIZES], true);
  }, [trainSizes]);

  const stopTraining = useCallback(() => {
    trainingRef.current = false;
    setTrainingLabel("Stopping…");
  }, []);

  const reset = useCallback(() => {
    trainingRef.current = false;
    if (replayRef.current) clearInterval(replayRef.current);
    setIsReplaying(false);
    setRuns({});
    setCurrentEpoch(0);
    setMaxEpochForRun(0);
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
    const last = runs[DATASET_SIZES[0]]?.history.at(-1)?.epoch ?? 0;
    setCurrentEpoch(last);
    replayRef.current = setInterval(() => {
      i += 1;
      if (i >= DATASET_SIZES.length) {
        if (replayRef.current) clearInterval(replayRef.current);
        setIsReplaying(false);
        return;
      }
      setSelectedIndex(i);
      const ep = runs[DATASET_SIZES[i]]?.history.at(-1)?.epoch ?? 0;
      setCurrentEpoch(ep);
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
      const ep = runs[DATASET_SIZES[index]]?.history.at(-1)?.epoch ?? 0;
      setCurrentEpoch(ep);
    },
    run,
    runs,
    snapshot,
    currentEpoch,
    maxEpochForRun,
    status,
    tfReady,
    trainingLabel,
    seed,
    setSeed,
    setCurrentEpoch,
    trainCurrentSize,
    trainAllSizes,
    stopTraining,
    reset,
    replaySizes,
    stopReplay,
    isReplaying,
    gap,
  };
}
