"use client";

import { useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, RotateCcw, Download, Loader2 } from "lucide-react";
import { useActivationsLab } from "@/hooks/useActivationsLab";
import { DecisionBoundary } from "@/components/visualization/decision-boundary";
import { MetricChart } from "@/components/visualization/metric-chart";
import { ConfusionMatrix } from "@/components/visualization/confusion-matrix";
import { EpochSlider } from "@/components/visualization/epoch-slider";
import { Button } from "@/components/ui/button";
import { Section } from "@/components/layout/section";
import { cn } from "@/lib/utils";

const THEORY_CHIPS = [
  "Linear layers compose into one linear transform",
  "Activations introduce nonlinearity",
  "Nonlinearity bends decision boundaries",
  "Same depth — only activation changes",
] as const;

export function ActivationsLab(): React.ReactElement {
  const lab = useActivationsLab();
  const boundaryRef = useRef<HTMLDivElement>(null);

  const lossA = lab.historyA.map((s) => ({ epoch: s.epoch, value: s.loss }));
  const lossB = lab.historyB.map((s) => ({ epoch: s.epoch, value: s.loss }));
  const accA = lab.historyA.map((s) => ({ epoch: s.epoch, value: s.accuracy }));
  const accB = lab.historyB.map((s) => ({ epoch: s.epoch, value: s.accuracy }));

  const downloadPng = (): void => {
    const canvases = boundaryRef.current?.querySelectorAll("canvas");
    if (!canvases || canvases.length < 2) return;
    const w = canvases[0].width;
    const h = canvases[0].height;
    const combined = document.createElement("canvas");
    combined.width = w * 2;
    combined.height = h;
    const ctx = combined.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(canvases[0], 0, 0);
    ctx.drawImage(canvases[1], w, 0);
    const link = document.createElement("a");
    link.download = "activations-boundaries.png";
    link.href = combined.toDataURL("image/png");
    link.click();
  };

  return (
    <>
      <Section id="claim" eyebrow="Claim" title="The experiment">
        <div className="glass-panel border-l-4 border-l-[var(--lab-activations)] p-8">
          <p className="text-xl font-medium leading-relaxed text-[var(--text-primary)] md:text-2xl">
            Without nonlinearity, a neural network cannot separate concentric rings
            — no matter how you train it.
          </p>
        </div>
      </Section>

      <Section id="theory" eyebrow="Theory" title="Why activations matter">
        <div className="flex flex-wrap gap-3">
          {THEORY_CHIPS.map((chip) => (
            <span
              key={chip}
              className="rounded-full border border-[var(--border)] bg-[var(--surface)] px-4 py-2 text-sm text-[var(--text-secondary)]"
            >
              {chip}
            </span>
          ))}
        </div>
      </Section>

      <Section id="experiment" eyebrow="Experiment" title="Train both models">
        <div className="mb-6 flex flex-wrap items-center gap-3">
          <Button
            onClick={() => void lab.trainBoth()}
            disabled={lab.status === "training" || !lab.tfReady}
          >
            {lab.status === "training" ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Training…
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                Train Both Models
              </>
            )}
          </Button>
          <Button variant="secondary" onClick={lab.reset} disabled={lab.status === "training"}>
            <RotateCcw className="h-4 w-4" />
            Reset
          </Button>
          <Button
            variant="secondary"
            onClick={lab.isReplaying ? lab.stopReplay : lab.replay}
            disabled={lab.maxEpoch === 0}
          >
            {lab.isReplaying ? "Stop Replay" : "Replay"}
          </Button>
          <Button
            variant="ghost"
            onClick={downloadPng}
            disabled={!lab.snapshotA || !lab.snapshotB}
          >
            <Download className="h-4 w-4" />
            PNG
          </Button>
        </div>

        <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="glass-panel p-4">
            <label className="text-xs text-[var(--text-muted)]">Dataset seed</label>
            <input
              type="number"
              value={lab.seed}
              disabled={lab.status === "training"}
              onChange={(e) => lab.setSeed(Number(e.target.value) || 42)}
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 font-mono text-sm"
            />
          </div>
          <details className="glass-panel p-4 sm:col-span-2 lg:col-span-1">
            <summary className="cursor-pointer text-xs text-[var(--text-muted)]">
              Learning rate
            </summary>
            <input
              type="range"
              min={0.001}
              max={0.1}
              step={0.001}
              value={lab.learningRate}
              disabled={lab.status === "training"}
              onChange={(e) => lab.setLearningRate(Number(e.target.value))}
              className="mt-2 w-full accent-[var(--accent-primary)]"
            />
            <p className="mt-1 font-mono text-xs">{lab.learningRate.toFixed(3)}</p>
          </details>
          <div className="glass-panel flex items-center justify-center p-4">
            <p className="text-center text-sm text-[var(--text-muted)]">
              {lab.tfReady ? (
                <>
                  <span className="font-mono text-[var(--text-primary)]">
                    {lab.dataset.metadata.count}
                  </span>{" "}
                  ring samples
                </>
              ) : (
                "Loading TensorFlow.js…"
              )}
            </p>
          </div>
        </div>

        <div
          ref={boundaryRef}
          className="grid gap-6 lg:grid-cols-2"
        >
          <DecisionBoundary
            grid={lab.snapshotA?.decisionGrid ?? null}
            features={lab.dataset.features}
            labels={lab.dataset.labels}
            sampleCount={lab.dataset.metadata.count}
            label="Model A — Linear (no activation)"
          />
          <DecisionBoundary
            grid={lab.snapshotB?.decisionGrid ?? null}
            features={lab.dataset.features}
            labels={lab.dataset.labels}
            sampleCount={lab.dataset.metadata.count}
            label="Model B — ReLU Hidden Layer"
          />
        </div>
      </Section>

      <Section id="results" eyebrow="Results" title="Training progress">
        <div className="mb-6">
          <EpochSlider
            epoch={lab.currentEpoch}
            maxEpoch={lab.maxEpoch}
            onChange={lab.setCurrentEpoch}
            disabled={lab.status === "training"}
          />
        </div>

        <div className="mb-6 grid gap-4 lg:grid-cols-2">
          <MetricChart
            title="Loss"
            historyA={lossA}
            historyB={lossB}
            currentEpoch={lab.currentEpoch}
          />
          <MetricChart
            title="Accuracy"
            historyA={accA}
            historyB={accB}
            currentEpoch={lab.currentEpoch}
            maxY={1}
            formatValue={(v) => `${(v * 100).toFixed(0)}%`}
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <ConfusionMatrix
            matrix={lab.snapshotA?.confusionMatrix}
            label="Linear — confusion matrix"
          />
          <ConfusionMatrix
            matrix={lab.snapshotB?.confusionMatrix}
            label="ReLU — confusion matrix"
          />
        </div>

        {(lab.snapshotA || lab.snapshotB) && (
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {lab.snapshotA && (
              <div className="glass-panel p-4 font-mono text-sm">
                <span className="text-[var(--text-muted)]">Linear · </span>
                loss {lab.snapshotA.loss.toFixed(4)} · acc{" "}
                {(lab.snapshotA.accuracy * 100).toFixed(1)}%
              </div>
            )}
            {lab.snapshotB && (
              <div className="glass-panel p-4 font-mono text-sm">
                <span className="text-[var(--lab-activations)]">ReLU · </span>
                loss {lab.snapshotB.loss.toFixed(4)} · acc{" "}
                {(lab.snapshotB.accuracy * 100).toFixed(1)}%
              </div>
            )}
          </div>
        )}
      </Section>

      <Section id="insight" eyebrow="Insight" title="Key takeaway">
        <AnimatePresence>
          {lab.status === "complete" && (
            <motion.div
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              className={cn(
                "glass-panel border-l-4 border-l-[var(--lab-activations)] p-8",
                "shadow-[0_0_40px_rgba(249,115,22,0.15)]"
              )}
            >
              <p className="text-xl font-medium text-[var(--text-primary)] md:text-2xl">
                Nothing changed except ReLU.
              </p>
              <p className="mt-3 text-[var(--text-secondary)]">
                Same data. Same optimizer. Same epochs. Same hidden size. Nonlinearity
                is the difference between failure and perfect separation.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
        {lab.status !== "complete" && (
          <p className="text-sm text-[var(--text-muted)]">
            Complete training to reveal the key insight.
          </p>
        )}
      </Section>
    </>
  );
}
