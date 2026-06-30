"use client";

import { useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, RotateCcw, Download, Loader2 } from "lucide-react";
import { useDepthLab } from "@/hooks/useDepthLab";
import { DecisionBoundary } from "@/components/visualization/decision-boundary";
import { TripleMetricChart } from "@/components/visualization/triple-metric-chart";
import { EpochSlider } from "@/components/visualization/epoch-slider";
import { WeightCollapsePanel } from "@/components/visualization/weight-collapse-panel";
import { NeuralNetworkView } from "@/components/visualization/neural-network-view";
import { Section } from "@/components/layout/section";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const THEORY_CHIPS = [
  "Matrix multiply chains into one matrix",
  "Depth alone adds no nonlinearity",
  "Activations make depth meaningful",
  "W = W₅ × W₄ × W₃ × W₂ × W₁",
] as const;

export function DepthLab(): React.ReactElement {
  const lab = useDepthLab();
  const boundaryRef = useRef<HTMLDivElement>(null);
  const [networkCollapsed, setNetworkCollapsed] = useState(false);

  const toSeries = (history: { epoch: number; loss: number; accuracy: number }[], key: "loss" | "accuracy") =>
    history.map((s) => ({ epoch: s.epoch, value: s[key] }));

  const downloadPng = (): void => {
    const canvases = boundaryRef.current?.querySelectorAll("canvas");
    if (!canvases || canvases.length < 3) return;
    const w = canvases[0].width;
    const h = canvases[0].height;
    const combined = document.createElement("canvas");
    combined.width = w * 3;
    combined.height = h;
    const ctx = combined.getContext("2d");
    if (!ctx) return;
    canvases.forEach((c, i) => ctx.drawImage(c, i * w, 0));
    const link = document.createElement("a");
    link.download = "depth-boundaries.png";
    link.href = combined.toDataURL("image/png");
    link.click();
  };

  return (
    <>
      <Section id="claim" eyebrow="Claim" title="The experiment">
        <div className="glass-panel border-l-4 border-l-[var(--lab-depth)] p-8">
          <p className="text-xl font-medium leading-relaxed text-[var(--text-primary)] md:text-2xl">
            Stacking linear layers does not add expressive power. Five linear
            layers collapse into one.
          </p>
        </div>
      </Section>

      <Section id="theory" eyebrow="Theory" title="Why depth needs activation">
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

      <Section id="experiment" eyebrow="Experiment" title="Compare all three models">
        <div className="mb-6 flex flex-wrap items-center gap-3">
          <Button
            onClick={() => void lab.compareAll()}
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
                Compare All
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
          <Button variant="ghost" onClick={downloadPng} disabled={!lab.snapshot3}>
            <Download className="h-4 w-4" />
            PNG
          </Button>
        </div>

        {lab.trainingLabel && (
          <p className="mb-4 text-sm text-[var(--lab-depth)]">{lab.trainingLabel}</p>
        )}

        <div className="mb-6 glass-panel p-4">
          <label className="text-xs text-[var(--text-muted)]">Dataset seed</label>
          <input
            type="number"
            value={lab.seed}
            disabled={lab.status === "training"}
            onChange={(e) => lab.setSeed(Number(e.target.value) || 42)}
            className="mt-1 w-full max-w-xs rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 font-mono text-sm"
          />
        </div>

        <div ref={boundaryRef} className="grid gap-6 lg:grid-cols-3">
          <DecisionBoundary
            grid={lab.snapshot1?.decisionGrid ?? null}
            features={lab.dataset.features}
            labels={lab.dataset.labels}
            sampleCount={lab.dataset.metadata.count}
            label="1 Linear Layer"
          />
          <DecisionBoundary
            grid={lab.snapshot2?.decisionGrid ?? null}
            features={lab.dataset.features}
            labels={lab.dataset.labels}
            sampleCount={lab.dataset.metadata.count}
            label="5 Linear Layers"
          />
          <DecisionBoundary
            grid={lab.snapshot3?.decisionGrid ?? null}
            features={lab.dataset.features}
            labels={lab.dataset.labels}
            sampleCount={lab.dataset.metadata.count}
            label="5 Layers + ReLU"
          />
        </div>
      </Section>

      <Section id="weights" eyebrow="Weights" title="Matrix collapse">
        <div className="mb-6">
          <NeuralNetworkView collapsed={networkCollapsed} />
          <Button
            variant="ghost"
            size="sm"
            className="mt-3"
            onClick={() => setNetworkCollapsed((c) => !c)}
          >
            {networkCollapsed ? "Expand 5 layers" : "Collapse to 1 layer"}
          </Button>
        </div>
        <WeightCollapsePanel
          matrices={lab.snapshot2?.weightMatrices}
          combined={lab.snapshot2?.combinedWeights}
        />
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

        <div className="grid gap-4 lg:grid-cols-2">
          <TripleMetricChart
            title="Loss"
            currentEpoch={lab.currentEpoch}
            series={[
              {
                id: "m1",
                label: "1 Linear",
                color: "var(--text-muted)",
                history: toSeries(lab.history1, "loss"),
              },
              {
                id: "m2",
                label: "5 Linear",
                color: "var(--lab-depth)",
                history: toSeries(lab.history2, "loss"),
              },
              {
                id: "m3",
                label: "5 ReLU",
                color: "#10b981",
                history: toSeries(lab.history3, "loss"),
              },
            ]}
          />
          <TripleMetricChart
            title="Accuracy"
            currentEpoch={lab.currentEpoch}
            maxY={1}
            formatValue={(v) => `${(v * 100).toFixed(0)}%`}
            series={[
              {
                id: "m1",
                label: "1 Linear",
                color: "var(--text-muted)",
                history: toSeries(lab.history1, "accuracy"),
              },
              {
                id: "m2",
                label: "5 Linear",
                color: "var(--lab-depth)",
                history: toSeries(lab.history2, "accuracy"),
              },
              {
                id: "m3",
                label: "5 ReLU",
                color: "#10b981",
                history: toSeries(lab.history3, "accuracy"),
              },
            ]}
          />
        </div>
      </Section>

      <Section id="insight" eyebrow="Insight" title="Key takeaway">
        <AnimatePresence>
          {lab.status === "complete" && (
            <motion.div
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              className={cn(
                "glass-panel border-l-4 border-l-[var(--lab-depth)] p-8",
                "shadow-[0_0_40px_rgba(6,182,212,0.15)]"
              )}
            >
              <p className="text-xl font-medium text-[var(--text-primary)] md:text-2xl">
                Depth without activation is mathematically equivalent to one layer.
              </p>
              <p className="mt-3 text-[var(--text-secondary)]">
                ReLU is what makes depth matter. Compare the boundaries — 1-Layer
                and 5-Linear look the same; 5-ReLU curves around the rings.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
        {lab.status !== "complete" && (
          <p className="text-sm text-[var(--text-muted)]">
            Run Compare All to reveal the key insight.
          </p>
        )}
      </Section>
    </>
  );
}
