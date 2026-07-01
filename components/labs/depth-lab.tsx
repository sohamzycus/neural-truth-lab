"use client";

import { useRef, useState } from "react";
import { Play, RotateCcw, Download, Loader2 } from "lucide-react";
import { useDepthLab } from "@/hooks/useDepthLab";
import { DecisionBoundary } from "@/components/visualization/decision-boundary";
import { TripleMetricChart } from "@/components/visualization/triple-metric-chart";
import { EpochSlider } from "@/components/visualization/epoch-slider";
import { WeightCollapsePanel } from "@/components/visualization/weight-collapse-panel";
import { LabSchematicPanel } from "@/components/labs/lab-schematic-panel";
import { depthSchematic, LAB_SCHEMATIC_ACCENT } from "@/lib/lab-schematics";
import { LAB_DEMOS } from "@/lib/lab-demos";
import { LabWorkspace } from "@/components/layout/lab-workspace";
import { LabStat } from "@/components/labs/lab-stat";
import { LabSidebarPanel } from "@/components/labs/lab-sidebar-panel";
import { Button } from "@/components/ui/button";

const THEORY = [
  "W₅W₄W₃W₂W₁ collapses to a single 2×2 matrix.",
  "1-layer and 5-linear produce the same boundary.",
  "ReLU between layers is what makes depth meaningful.",
] as const;

function fmtAcc(v: number | undefined): string {
  return v === undefined ? "—" : `${(v * 100).toFixed(0)}%`;
}

export function DepthLab(): React.ReactElement {
  const lab = useDepthLab();
  const boundaryRef = useRef<HTMLDivElement>(null);
  const [networkCollapsed, setNetworkCollapsed] = useState(false);

  const toSeries = (
    history: { epoch: number; loss: number; accuracy: number }[],
    key: "loss" | "accuracy"
  ) => history.map((s) => ({ epoch: s.epoch, value: s[key] }));

  const acc1 = lab.snapshot1?.accuracy;
  const acc2 = lab.snapshot2?.accuracy;
  const acc3 = lab.snapshot3?.accuracy;
  const collapsed =
    acc1 !== undefined && acc2 !== undefined
      ? Math.abs(acc1 - acc2) < 0.02
      : undefined;

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
    <LabWorkspace
      labId="depth"
      experiment="Network depth"
      accentClass="text-[var(--lab-depth)]"
      demo={LAB_DEMOS.depth}
      problem="Five stacked linear layers add zero expressive power."
      solution="Insert ReLUs — the same depth learns a curved boundary. Without them, depth is just one matrix multiply."
      stats={
        <>
          <LabStat size="sm" label="1 linear" value={fmtAcc(acc1)} />
          <LabStat size="sm" label="5 linear" value={fmtAcc(acc2)} hint="≈ 1 layer" />
          <LabStat size="sm" label="5 + ReLU" value={fmtAcc(acc3)} accent />
          <LabStat
            size="sm"
            label="Collapse"
            value={collapsed === undefined ? "—" : collapsed ? "Yes" : "No"}
            hint="1L vs 5L"
          />
        </>
      }
      sidebar={
        <>
          <LabSidebarPanel title="Run experiment">
            <div className="flex flex-wrap gap-2">
              <Button
                className="flex-1"
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
                disabled={!lab.snapshot3}
                aria-label="Download PNG"
              >
                <Download className="h-4 w-4" />
              </Button>
            </div>
            {lab.trainingLabel ? (
              <p className="mt-2 text-xs text-[var(--lab-depth)]">{lab.trainingLabel}</p>
            ) : null}
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
              {...depthSchematic(networkCollapsed)}
              accentColor={LAB_SCHEMATIC_ACCENT.depth}
              toggleLabel={networkCollapsed ? "Expand 5 layers" : "Collapse to 1"}
              onToggle={() => setNetworkCollapsed((c) => !c)}
            />
            <div className="mt-2">
              <WeightCollapsePanel
                matrices={lab.snapshot2?.weightMatrices}
                combined={lab.snapshot2?.combinedWeights}
              />
            </div>
          </LabSidebarPanel>

          <LabSidebarPanel title="Why this matters">
            <ul className="space-y-2 text-xs leading-relaxed text-[var(--text-secondary)]">
              {THEORY.map((t) => (
                <li key={t} className="flex gap-2">
                  <span className="text-[var(--lab-depth)]">→</span>
                  {t}
                </li>
              ))}
            </ul>
          </LabSidebarPanel>
        </>
      }
      charts={
        <>
          <TripleMetricChart
            compact
            expandable
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
                color: "var(--lab-generalization)",
                history: toSeries(lab.history3, "loss"),
              },
            ]}
          />
          <TripleMetricChart
            compact
            expandable
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
                color: "var(--lab-generalization)",
                history: toSeries(lab.history3, "accuracy"),
              },
            ]}
          />
        </>
      }
      insight={
        lab.status === "complete" ? (
          <p className="rounded-lg border border-[var(--lab-depth)]/25 bg-[var(--lab-depth)]/5 px-3 py-2 text-xs leading-relaxed text-[var(--text-secondary)]">
            <span className="font-semibold text-[var(--text-primary)]">Proof: </span>
            1-linear and 5-linear boundaries match; 5-ReLU curves around the rings.
          </p>
        ) : (
          <p className="text-xs text-[var(--text-muted)]">
            Run all three models · click any boundary to expand
          </p>
        )
      }
    >
      <div ref={boundaryRef} className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        <DecisionBoundary
          compact
          expandable
          grid={lab.snapshot1?.decisionGrid ?? null}
          features={lab.dataset.features}
          labels={lab.dataset.labels}
          sampleCount={lab.dataset.metadata.count}
          label="1 linear layer"
        />
        <DecisionBoundary
          compact
          expandable
          grid={lab.snapshot2?.decisionGrid ?? null}
          features={lab.dataset.features}
          labels={lab.dataset.labels}
          sampleCount={lab.dataset.metadata.count}
          label="5 linear layers"
        />
        <DecisionBoundary
          compact
          expandable
          grid={lab.snapshot3?.decisionGrid ?? null}
          features={lab.dataset.features}
          labels={lab.dataset.labels}
          sampleCount={lab.dataset.metadata.count}
          label="5 layers + ReLU"
        />
      </div>
    </LabWorkspace>
  );
}
