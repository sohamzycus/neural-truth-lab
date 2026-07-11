"use client";

import { useRef, useState } from "react";
import { Play, RotateCcw, Download, Loader2 } from "lucide-react";
import { useActivationsLab } from "@/hooks/useActivationsLab";
import { DecisionBoundary } from "@/components/visualization/decision-boundary";
import { MetricChart } from "@/components/visualization/metric-chart";
import { ConfusionMatrix } from "@/components/visualization/confusion-matrix";
import { EpochSlider } from "@/components/visualization/epoch-slider";
import { LAB_DEMOS } from "@/lib/lab-demos";
import { activationsSchematic, LAB_SCHEMATIC_ACCENT } from "@/lib/lab-schematics";
import { LabWorkspace } from "@/components/layout/lab-workspace";
import { LabStat } from "@/components/labs/lab-stat";
import { LabSidebarPanel } from "@/components/labs/lab-sidebar-panel";
import { LabSchematicPanel } from "@/components/labs/lab-schematic-panel";
import { Button } from "@/components/ui/button";

const THEORY = [
  "A linear model can only draw one straight boundary.",
  "ReLU bends the surface — same data, same depth.",
  "Only the activation function changes between A and B.",
] as const;

function fmtAcc(v: number | undefined): string {
  return v === undefined ? "—" : `${(v * 100).toFixed(0)}%`;
}

export function ActivationsLab(): React.ReactElement {
  const lab = useActivationsLab();
  const boundaryRef = useRef<HTMLDivElement>(null);
  const [schematic, setSchematic] = useState<"linear" | "relu">("linear");

  const linearAcc = lab.snapshotA?.accuracy;
  const reluAcc = lab.snapshotB?.accuracy;
  const gain =
    linearAcc !== undefined && reluAcc !== undefined
      ? reluAcc - linearAcc
      : undefined;

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
    <LabWorkspace
      labId="activations"
      experiment="Activation functions"
      accentClass="text-[var(--lab-activations)]"
      demo={LAB_DEMOS.activations}
      problem="Concentric rings cannot be separated by a straight line."
      solution="Add one ReLU hidden layer — the boundary curves around the inner ring while everything else stays identical."
      stats={
        <>
          <LabStat size="sm" label="Linear" value={fmtAcc(linearAcc)} />
          <LabStat size="sm" label="ReLU" value={fmtAcc(reluAcc)} accent />
          <LabStat
            size="sm"
            label="Gain"
            value={gain === undefined ? "—" : `+${(gain * 100).toFixed(0)}%`}
            hint="ReLU − linear"
            accent={gain !== undefined && gain > 0.2}
          />
        </>
      }
      sidebar={
        <>
          <LabSidebarPanel title="Run experiment">
            <div className="flex flex-wrap gap-2">
              <Button
                className="flex-1"
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
                    Run
                  </>
                )}
              </Button>
              <Button
                variant="secondary"
                size="icon"
                onClick={lab.reset}
                disabled={lab.status === "training"}
                aria-label="Reset"
              >
                <RotateCcw className="h-4 w-4" />
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={lab.isReplaying ? lab.stopReplay : lab.replay}
                disabled={lab.maxEpoch === 0}
              >
                {lab.isReplaying ? "Stop" : "Replay"}
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={downloadPng}
                disabled={!lab.snapshotA || !lab.snapshotB}
                aria-label="Download PNG"
              >
                <Download className="h-4 w-4" />
              </Button>
            </div>
            <p className="mt-2 text-xs text-[var(--text-muted)]">
              {lab.tfReady
                ? `${lab.dataset.metadata.count} ring samples · seed ${lab.seed}`
                : "Loading TensorFlow.js…"}
            </p>
          </LabSidebarPanel>

          <LabSidebarPanel title="Timeline">
            <EpochSlider
              epoch={lab.currentEpoch}
              maxEpoch={lab.maxEpoch}
              onChange={lab.setCurrentEpoch}
              disabled={lab.status === "training"}
            />
          </LabSidebarPanel>

          <LabSidebarPanel title="Network schematic">
            <LabSchematicPanel
              {...activationsSchematic(schematic)}
              accentColor={LAB_SCHEMATIC_ACCENT.activations}
              toggleLabel={
                schematic === "linear" ? "Switch to ReLU model" : "Switch to linear model"
              }
              onToggle={() =>
                setSchematic((s) => (s === "linear" ? "relu" : "linear"))
              }
            />
          </LabSidebarPanel>

          <LabSidebarPanel title="Parameters">
            <label className="text-xs text-[var(--text-muted)]">Seed</label>
            <input
              type="number"
              value={lab.seed}
              disabled={lab.status === "training"}
              onChange={(e) => lab.setSeed(Number(e.target.value) || 42)}
              className="mt-1 w-full rounded-md border border-[var(--border)] bg-[var(--background)] px-2 py-1.5 font-mono text-sm"
            />
            <label className="mt-3 block text-xs text-[var(--text-muted)]">
              Learning rate · {lab.learningRate.toFixed(3)}
            </label>
            <input
              type="range"
              min={0.001}
              max={0.1}
              step={0.001}
              value={lab.learningRate}
              disabled={lab.status === "training"}
              onChange={(e) => lab.setLearningRate(Number(e.target.value))}
              className="mt-1 w-full accent-[var(--lab-activations)]"
            />
          </LabSidebarPanel>

          <LabSidebarPanel title="Why this matters">
            <ul className="space-y-2 text-xs leading-relaxed text-[var(--text-secondary)]">
              {THEORY.map((t) => (
                <li key={t} className="flex gap-2">
                  <span className="text-[var(--lab-activations)]">→</span>
                  {t}
                </li>
              ))}
            </ul>
          </LabSidebarPanel>
        </>
      }
      charts={
        <>
          <MetricChart
            compact
            expandable
            title="Loss"
            historyA={lossA}
            historyB={lossB}
            currentEpoch={lab.currentEpoch}
          />
          <MetricChart
            compact
            expandable
            title="Accuracy"
            historyA={accA}
            historyB={accB}
            currentEpoch={lab.currentEpoch}
            maxY={1}
            formatValue={(v) => `${(v * 100).toFixed(0)}%`}
          />
          <ConfusionMatrix
            compact
            expandable
            matrix={lab.snapshotA?.confusionMatrix}
            label="Linear — confusion"
          />
          <ConfusionMatrix
            compact
            expandable
            matrix={lab.snapshotB?.confusionMatrix}
            label="ReLU — confusion"
          />
        </>
      }
      insight={
        lab.status === "complete" ? (
          <p className="rounded-lg border border-[var(--lab-activations)]/25 bg-[var(--lab-activations)]/5 px-3 py-2 text-xs leading-relaxed text-[var(--text-secondary)]">
            <span className="font-semibold text-[var(--text-primary)]">Proof: </span>
            Same data and depth — only ReLU changes the boundary from flat to curved.
          </p>
        ) : (
          <p className="text-xs text-[var(--text-muted)]">
            Run the experiment · click any panel to expand
          </p>
        )
      }
    >
      <div ref={boundaryRef} className="grid gap-2 sm:grid-cols-2">
        <DecisionBoundary
          compact
          expandable
          grid={lab.snapshotA?.decisionGrid ?? null}
          features={lab.dataset.features}
          labels={lab.dataset.labels}
          sampleCount={lab.dataset.metadata.count}
          label="A · Linear (no activation)"
        />
        <DecisionBoundary
          compact
          expandable
          grid={lab.snapshotB?.decisionGrid ?? null}
          features={lab.dataset.features}
          labels={lab.dataset.labels}
          sampleCount={lab.dataset.metadata.count}
          label="B · ReLU hidden layer"
        />
      </div>
    </LabWorkspace>
  );
}
