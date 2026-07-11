"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import * as tf from "@tensorflow/tfjs";
import {
  buildSyntheticCorpus,
  type SyntheticCorpus,
} from "@/datasets/synthetic-language";
import {
  corpusToTensors,
  createEmbeddingModel,
  disposeModel,
  extractEmbeddingMatrix,
  EMBED_DIM,
} from "@/training/models/embedding-lm";
import { pca2D } from "@/visualization/embedding-projection";
import { readMetric } from "@/training/metrics";
import { markLabComplete } from "@/lib/progress-storage";
import type { EmbeddingSnapshot } from "@/types/training";

const EPOCHS = 200;
const SNAPSHOT_EVERY = 5;

export type TrainingStatus = "idle" | "training" | "paused" | "complete";

export function useEmbeddingsLab(): {
  corpus: SyntheticCorpus;
  history: EmbeddingSnapshot[];
  lossHistory: { epoch: number; value: number }[];
  snapshot: EmbeddingSnapshot | null;
  currentEpoch: number;
  status: TrainingStatus;
  tfReady: boolean;
  maxEpoch: number;
  setCurrentEpoch: (epoch: number) => void;
  train: () => Promise<void>;
  pause: () => void;
  resume: () => void;
  reset: () => void;
  replay: () => void;
  stopReplay: () => void;
  isReplaying: boolean;
} {
  const [corpus] = useState<SyntheticCorpus>(() => buildSyntheticCorpus());
  const [history, setHistory] = useState<EmbeddingSnapshot[]>([]);
  const [lossHistory, setLossHistory] = useState<{ epoch: number; value: number }[]>(
    []
  );
  const [currentEpoch, setCurrentEpoch] = useState(0);
  const [status, setStatus] = useState<TrainingStatus>("idle");
  const [tfReady, setTfReady] = useState(false);
  const [isReplaying, setIsReplaying] = useState(false);

  const modelRef = useRef<tf.LayersModel | null>(null);
  const trainingRef = useRef(false);
  const pausedRef = useRef(false);
  const epochRef = useRef(1);
  const replayRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const xsRef = useRef<tf.Tensor2D | null>(null);
  const ysRef = useRef<tf.Tensor2D | null>(null);

  useEffect(() => {
    let mounted = true;
    void tf.setBackend("webgl").then(() => {
      if (mounted) {
        modelRef.current = createEmbeddingModel(corpus.vocab.length);
        const { xs, ys } = corpusToTensors(corpus);
        xsRef.current = xs;
        ysRef.current = ys;
        setTfReady(true);
      }
    });
    return () => {
      mounted = false;
      disposeModel(modelRef.current);
      xsRef.current?.dispose();
      ysRef.current?.dispose();
      if (replayRef.current) clearInterval(replayRef.current);
    };
  }, [corpus]);

  const makeSnapshot = useCallback(
    (epoch: number, loss: number, accuracy: number): EmbeddingSnapshot => {
      const embeddings = extractEmbeddingMatrix(modelRef.current!);
      return {
        epoch,
        loss,
        accuracy,
        embeddings,
        points: pca2D(
          embeddings,
          corpus.vocab.length,
          EMBED_DIM,
          corpus.idToToken
        ),
      };
    },
    [corpus]
  );

  const trainingLoop = useCallback(async () => {
    const model = modelRef.current;
    const xs = xsRef.current;
    const ys = ysRef.current;
    if (!model || !xs || !ys) return;

    const snapshots: EmbeddingSnapshot[] = [];
    const losses: { epoch: number; value: number }[] = [];

    for (let epoch = epochRef.current; epoch <= EPOCHS; epoch++) {
      while (pausedRef.current) {
        await new Promise((r) => setTimeout(r, 100));
        if (!trainingRef.current) return;
      }
      if (!trainingRef.current) return;

      const hist = await model.fit(xs, ys, {
        epochs: 1,
        batchSize: Math.min(32, xs.shape[0]),
        shuffle: true,
        verbose: 0,
      });

      const loss = readMetric(hist, "loss");
      const accuracy = readMetric(hist, "accuracy");
      losses.push({ epoch, value: loss });
      setLossHistory([...losses]);

      if (epoch % SNAPSHOT_EVERY === 0 || epoch === EPOCHS) {
        snapshots.push(makeSnapshot(epoch, loss, accuracy));
        setHistory([...snapshots]);
      }

      setCurrentEpoch(epoch);
      epochRef.current = epoch + 1;
      await tf.nextFrame();
    }

    trainingRef.current = false;
    pausedRef.current = false;
    markLabComplete("embeddings");
    setStatus("complete");
  }, [makeSnapshot]);

  const train = useCallback(async () => {
    if (!tfReady || trainingRef.current) return;
    disposeModel(modelRef.current);
    modelRef.current = createEmbeddingModel(corpus.vocab.length);
    setHistory([]);
    setLossHistory([]);
    setCurrentEpoch(0);
    epochRef.current = 1;
    trainingRef.current = true;
    pausedRef.current = false;
    setStatus("training");
    await trainingLoop();
  }, [corpus.vocab.length, tfReady, trainingLoop]);

  const pause = useCallback(() => {
    if (status === "training") {
      pausedRef.current = true;
      setStatus("paused");
    }
  }, [status]);

  const resume = useCallback(() => {
    if (status === "paused" && trainingRef.current) {
      pausedRef.current = false;
      setStatus("training");
      void trainingLoop();
    }
  }, [status, trainingLoop]);

  const reset = useCallback(() => {
    trainingRef.current = false;
    pausedRef.current = false;
    if (replayRef.current) clearInterval(replayRef.current);
    setIsReplaying(false);
    disposeModel(modelRef.current);
    modelRef.current = createEmbeddingModel(corpus.vocab.length);
    epochRef.current = 1;
    setHistory([]);
    setLossHistory([]);
    setCurrentEpoch(0);
    setStatus("idle");
  }, [corpus.vocab.length]);

  const replay = useCallback(() => {
    if (history.length === 0) return;
    if (replayRef.current) clearInterval(replayRef.current);
    setIsReplaying(true);
    let i = 0;
    setCurrentEpoch(history[0].epoch);
    replayRef.current = setInterval(() => {
      i += 1;
      if (i >= history.length) {
        if (replayRef.current) clearInterval(replayRef.current);
        setIsReplaying(false);
        return;
      }
      setCurrentEpoch(history[i].epoch);
    }, 120);
  }, [history]);

  const stopReplay = useCallback(() => {
    if (replayRef.current) clearInterval(replayRef.current);
    setIsReplaying(false);
  }, []);

  const snapshot = useMemo(() => {
    if (history.length === 0) return null;
    return (
      [...history].reverse().find((s) => s.epoch <= currentEpoch) ?? history[0]
    );
  }, [history, currentEpoch]);

  return {
    corpus,
    history,
    lossHistory,
    snapshot,
    currentEpoch,
    status,
    tfReady,
    maxEpoch: EPOCHS,
    setCurrentEpoch,
    train,
    pause,
    resume,
    reset,
    replay,
    stopReplay,
    isReplaying,
  };
}
