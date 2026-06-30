"use client";

import { useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, RotateCcw, Download, Loader2 } from "lucide-react";
import { useGeneralizationLab } from "@/hooks/useGeneralizationLab";
import { GeneralizationGraph } from "@/components/visualization/generalization-graph";
import { DecisionBoundary } from "@/components/visualization/decision-boundary";
import { EpochSlider } from "@/components/visualization/epoch-slider";
import {
  DATASET_SIZES,
  sizeLabel,
} from "@/datasets/noisy-classification";
import { Section } from "@/components/layout/section";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const THEORY_CHIPS = [
  "Train loss = fit on seen data",
  "Val loss = fit on unseen data",
  "Gap = val loss − train loss",
  "More data → gap shrinks",
] as const;

const SIZE_LABELS = DATASET_SIZES.map((s) => `${sizeLabel(s)} (${s})`);

export function GeneralizationLab(): React.ReactElement {
  const lab = useGeneralizationLab();
  const graphRef = useRef<HTMLDivElement>(null);

  const trainLoss = lab.run?.history.map((s) => ({
    epoch: s.epoch,
    value: s.trainLoss,
  })) ?? [];
  const valLoss = lab.run?.history.map((s) => ({
    epoch: s.epoch,
    value: s.valLoss,
  })) ?? [];

  const downloadPng = (): void => {
    const svg = graphRef.current?.querySelector("svg");
    if (!svg) return;
    const svgData = new XMLSerializer().serializeToString(svg);
    const canvas = document.createElement("canvas");
    canvas.width = 960;
    canvas.height = 400;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const img = new Image();
    img.onload = () => {
      ctx.fillStyle = "#0a0a0f";
      ctx.fillRect(0, 0, 960, 400);
      ctx.drawImage(img, 0, 0, 960, 400);
      const link = document.createElement("a");
      link.download = `generalization-${lab.selectedSize}.png`;
      link.href = canvas.toDataURL("image/png");
      link.click();
    };
    img.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svgData)}`;
  };

  const combinedFeatures = lab.run
    ? (() => {
        const d = lab.run.dataset;
        const f = new Float32Array(
          (d.trainCount + d.valCount) * 2
        );
        const l = new Float32Array(d.trainCount + d.valCount);
        f.set(d.trainFeatures, 0);
        f.set(d.valFeatures, d.trainCount * 2);
        l.set(d.trainLabels, 0);
        l.set(d.valLabels, d.trainCount);
        return { features: f, labels: l, count: d.trainCount + d.valCount };
      })()
    : null;

  return (
    <>
      <Section id="claim" eyebrow="Claim" title="The experiment">
        <div className="glass-panel border-l-4 border-l-[var(--lab-generalization)] p-8">
          <p className="text-xl font-medium leading-relaxed text-[var(--text-primary)] md:text-2xl">
            More data closes the gap between what a model memorizes and what it
            truly learns.
          </p>
        </div>
      </Section>

      <Section id="theory" eyebrow="Theory" title="Generalization gap">
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

      <Section id="experiment" eyebrow="Experiment" title="Dataset size arena">
        <div className="mb-6 flex flex-wrap items-center gap-3">
          <Button
            onClick={() => void lab.trainAllSizes()}
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
                Train All Sizes
              </>
            )}
          </Button>
          <Button variant="secondary" onClick={lab.reset} disabled={lab.status === "training"}>
            <RotateCcw className="h-4 w-4" />
            Reset
          </Button>
          <Button
            variant="secondary"
            onClick={lab.isReplaying ? lab.stopReplay : lab.replaySizes}
            disabled={Object.keys(lab.runs).length < 2}
          >
            {lab.isReplaying ? "Stop" : "Animate sizes"}
          </Button>
          <Button variant="ghost" onClick={downloadPng} disabled={!lab.run}>
            <Download className="h-4 w-4" />
            PNG
          </Button>
        </div>

        {lab.trainingLabel && (
          <p className="mb-4 text-sm text-[var(--lab-generalization)]">{lab.trainingLabel}</p>
        )}

        <div className="mb-8 glass-panel p-4">
          <label className="text-xs text-[var(--text-muted)]">Training set size</label>
          <input
            type="range"
            min={0}
            max={DATASET_SIZES.length - 1}
            step={1}
            value={lab.selectedIndex}
            disabled={lab.status === "training" || !lab.run}
            onChange={(e) => lab.setSelectedIndex(Number(e.target.value))}
            className="mt-2 w-full accent-[var(--lab-generalization)]"
          />
          <div className="mt-2 flex justify-between text-xs text-[var(--text-muted)]">
            {SIZE_LABELS.map((l) => (
              <span key={l}>{l}</span>
            ))}
          </div>
          <div className="mt-4">
            <label className="text-xs text-[var(--text-muted)]">Seed</label>
            <input
              type="number"
              value={lab.seed}
              disabled={lab.status === "training"}
              onChange={(e) => lab.setSeed(Number(e.target.value) || 42)}
              className="mt-1 w-full max-w-xs rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 font-mono text-sm"
            />
          </div>
        </div>

        <div className="mb-6 grid gap-4 sm:grid-cols-3">
          <motion.div
            key={lab.selectedSize}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-panel p-6 sm:col-span-1"
          >
            <p className="text-xs uppercase tracking-wider text-[var(--text-muted)]">
              Generalization gap
            </p>
            <p className="mt-2 font-mono text-4xl font-semibold text-[var(--lab-generalization)]">
              {lab.gap.toFixed(3)}
            </p>
            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              val loss − train loss
            </p>
          </motion.div>
          {lab.snapshot && (
            <>
              <div className="glass-panel p-4 font-mono text-sm">
                <span className="text-[var(--text-muted)]">Train acc · </span>
                {(lab.snapshot.trainAccuracy * 100).toFixed(1)}%
              </div>
              <div className="glass-panel p-4 font-mono text-sm">
                <span className="text-[var(--text-muted)]">Val acc · </span>
                {(lab.snapshot.valAccuracy * 100).toFixed(1)}%
              </div>
            </>
          )}
        </div>

        <div ref={graphRef} className="mb-6">
          {lab.run ? (
            <GeneralizationGraph
              trainHistory={trainLoss}
              valHistory={valLoss}
              currentEpoch={lab.currentEpoch}
            />
          ) : (
            <div className="glass-panel flex h-48 items-center justify-center text-[var(--text-muted)]">
              {lab.tfReady
                ? "Train all sizes to compare generalization gaps"
                : "Loading TensorFlow.js…"}
            </div>
          )}
        </div>

        {combinedFeatures && lab.snapshot?.decisionGrid && (
          <DecisionBoundary
            grid={lab.snapshot.decisionGrid}
            features={combinedFeatures.features}
            labels={combinedFeatures.labels}
            sampleCount={combinedFeatures.count}
            label={`Decision boundary — ${sizeLabel(lab.selectedSize)} (${lab.selectedSize} samples)`}
          />
        )}
      </Section>

      <Section id="results" eyebrow="Results" title="Epoch timeline">
        <EpochSlider
          epoch={lab.currentEpoch}
          maxEpoch={lab.run?.history.length ? 150 : 0}
          onChange={lab.setCurrentEpoch}
          disabled={!lab.run || lab.status === "training"}
        />
      </Section>

      <Section id="insight" eyebrow="Insight" title="Key takeaway">
        <AnimatePresence>
          {lab.status === "complete" && (
            <motion.div
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              className={cn(
                "glass-panel border-l-4 border-l-[var(--lab-generalization)] p-8",
                "shadow-[0_0_40px_rgba(16,185,129,0.15)]"
              )}
            >
              <p className="text-xl font-medium text-[var(--text-primary)] md:text-2xl">
                As data grows, the gap closes.
              </p>
              <p className="mt-3 text-[var(--text-secondary)]">
                Small data invites memorization. Large data forces generalization.
                The gap between train and validation loss tells you which regime
                you&apos;re in.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
        {lab.status !== "complete" && (
          <p className="text-sm text-[var(--text-muted)]">
            Train all four sizes to reveal the key insight.
          </p>
        )}
      </Section>
    </>
  );
}
