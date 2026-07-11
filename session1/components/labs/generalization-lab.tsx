"use client";

import { useRef } from "react";
import { Play, RotateCcw, Download, Loader2, Square } from "lucide-react";
import { useGeneralizationLab } from "@/hooks/useGeneralizationLab";
import { GeneralizationGraph } from "@/components/visualization/generalization-graph";
import { DecisionBoundary } from "@/components/visualization/decision-boundary";
import { ExpandableViz } from "@/components/visualization/expandable-viz";
import { EpochSlider } from "@/components/visualization/epoch-slider";
import {
  DATASET_SIZES,
  sizeLabel,
} from "@/datasets/noisy-classification";
import { LAB_DEMOS } from "@/lib/lab-demos";
import { generalizationSchematic, LAB_SCHEMATIC_ACCENT } from "@/lib/lab-schematics";
import { LabWorkspace } from "@/components/layout/lab-workspace";
import { LabStat } from "@/components/labs/lab-stat";
import { LabSidebarPanel } from "@/components/labs/lab-sidebar-panel";
import { LabSchematicPanel } from "@/components/labs/lab-schematic-panel";
import { Button } from "@/components/ui/button";

const THEORY = [
  "Tiny data → train loss drops, val loss stays high.",
  "Gap = val loss − train loss measures memorization.",
  "More samples force the true boundary, not the noise.",
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

  const gap20 = lab.runs[20]?.history.at(-1);
  const gap20val =
    gap20 ? Math.max(0, gap20.valLoss - gap20.trainLoss) : undefined;

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
      ctx.fillStyle = "#fafaf9";
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
        const f = new Float32Array((d.trainCount + d.valCount) * 2);
        const l = new Float32Array(d.trainCount + d.valCount);
        f.set(d.trainFeatures, 0);
        f.set(d.valFeatures, d.trainCount * 2);
        l.set(d.trainLabels, 0);
        l.set(d.valLabels, d.trainCount);
        return { features: f, labels: l, count: d.trainCount + d.valCount };
      })()
    : null;

  const lossGraph = lab.run ? (
    <GeneralizationGraph
      trainHistory={trainLoss}
      valHistory={valLoss}
      currentEpoch={lab.currentEpoch}
    />
  ) : (
    <div className="flex h-32 items-center justify-center text-xs text-[var(--text-muted)]">
      {lab.tfReady ? "Train to plot train vs validation loss" : "Loading TensorFlow.js…"}
    </div>
  );

  return (
    <LabWorkspace
      labId="generalization"
      experiment="Generalization"
      accentClass="text-[var(--lab-generalization)]"
      demo={LAB_DEMOS.generalization}
      problem="A large model on tiny data memorizes noise instead of the boundary."
      solution="Scale training data — the generalization gap shrinks as the model is forced to learn structure, not individual points."
      stats={
        <>
          <LabStat
            size="sm"
            label="Gap"
            value={lab.gap.toFixed(3)}
            hint="val − train"
            accent
          />
          <LabStat
            size="sm"
            label="Gap @20"
            value={gap20val === undefined ? "—" : gap20val.toFixed(3)}
          />
          {lab.snapshot ? (
            <>
              <LabStat
                size="sm"
                label="Train"
                value={`${(lab.snapshot.trainAccuracy * 100).toFixed(0)}%`}
              />
              <LabStat
                size="sm"
                label="Val"
                value={`${(lab.snapshot.valAccuracy * 100).toFixed(0)}%`}
              />
            </>
          ) : null}
        </>
      }
      sidebar={
        <>
          <LabSidebarPanel title="Run experiment">
            <div className="flex flex-col gap-2">
              <Button
                className="w-full"
                onClick={() => void lab.trainCurrentSize()}
                disabled={lab.status === "training" || !lab.tfReady}
              >
                {lab.status === "training" ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    {lab.trainingLabel || "Training…"}
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4" />
                    Train {sizeLabel(lab.selectedSize)} (N={lab.selectedSize})
                  </>
                )}
              </Button>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  className="flex-1"
                  onClick={() => void lab.trainAllSizes()}
                  disabled={lab.status === "training" || !lab.tfReady}
                >
                  Train all 4
                </Button>
                {lab.status === "training" ? (
                  <Button variant="secondary" size="sm" onClick={lab.stopTraining} aria-label="Stop">
                    <Square className="h-3 w-3 fill-current" />
                  </Button>
                ) : null}
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
                  onClick={lab.isReplaying ? lab.stopReplay : lab.replaySizes}
                  disabled={Object.keys(lab.runs).length < 2}
                >
                  {lab.isReplaying ? "Stop" : "Replay"}
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={downloadPng}
                  disabled={!lab.run}
                  aria-label="Download PNG"
                >
                  <Download className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </LabSidebarPanel>

          <LabSidebarPanel title="Dataset size">
            <input
              type="range"
              min={0}
              max={DATASET_SIZES.length - 1}
              step={1}
              value={lab.selectedIndex}
              disabled={lab.status === "training" || !lab.run}
              onChange={(e) => lab.setSelectedIndex(Number(e.target.value))}
              className="w-full accent-[var(--lab-generalization)]"
            />
            <div className="mt-1 flex justify-between text-[10px] text-[var(--text-muted)]">
              {SIZE_LABELS.map((l) => (
                <span key={l}>{l.split(" ")[0]}</span>
              ))}
            </div>
          </LabSidebarPanel>

          <LabSidebarPanel title="Timeline">
            <EpochSlider
              epoch={lab.currentEpoch}
              maxEpoch={
                lab.run?.history.at(-1)?.epoch ?? lab.maxEpochForRun ?? 0
              }
              onChange={lab.setCurrentEpoch}
              disabled={!lab.run || lab.status === "training"}
            />
          </LabSidebarPanel>

          <LabSidebarPanel title="Network schematic">
            <LabSchematicPanel
              {...generalizationSchematic()}
              accentColor={LAB_SCHEMATIC_ACCENT.generalization}
            />
          </LabSidebarPanel>

          <LabSidebarPanel title="Why this matters">
            <ul className="space-y-2 text-xs leading-relaxed text-[var(--text-secondary)]">
              {THEORY.map((t) => (
                <li key={t} className="flex gap-2">
                  <span className="text-[var(--lab-generalization)]">→</span>
                  {t}
                </li>
              ))}
            </ul>
          </LabSidebarPanel>
        </>
      }
      insight={
        lab.status === "complete" ? (
          <p className="rounded-lg border border-[var(--lab-generalization)]/25 bg-[var(--lab-generalization)]/5 px-3 py-2 text-xs leading-relaxed text-[var(--text-secondary)]">
            <span className="font-semibold text-[var(--text-primary)]">Proof: </span>
            At N=20 the model memorizes; as N grows, train and val losses converge.
          </p>
        ) : (
          <p className="text-xs text-[var(--text-muted)]">
            Train sizes · click loss curve or boundary to expand
          </p>
        )
      }
    >
      <div className="grid gap-2 sm:grid-cols-2">
        <ExpandableViz
          label="Train vs validation loss"
          disabled={!lab.run}
          contentClassName="rounded-lg border border-[var(--border)] bg-[var(--background-elevated)] p-2"
        >
          <div ref={graphRef}>{lossGraph}</div>
        </ExpandableViz>

        {combinedFeatures ? (
          <DecisionBoundary
            compact
            expandable
            grid={lab.snapshot?.decisionGrid ?? null}
            features={combinedFeatures.features}
            labels={combinedFeatures.labels}
            sampleCount={combinedFeatures.count}
            label={`Boundary · N=${lab.selectedSize}`}
          />
        ) : (
          <ExpandableViz label="Decision boundary" disabled>
            <div className="lab-viz-canvas-compact flex aspect-square items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--viz-canvas-bg)] text-xs text-[var(--text-muted)]">
              Train to see boundary
            </div>
          </ExpandableViz>
        )}
      </div>
    </LabWorkspace>
  );
}
