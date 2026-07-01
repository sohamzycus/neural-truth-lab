"use client";

import { useRef, useState, useMemo } from "react";
import { Play, Pause, RotateCcw, Download, Loader2 } from "lucide-react";
import { useEmbeddingsLab } from "@/hooks/useEmbeddingsLab";
import { EmbeddingGalaxy } from "@/components/visualization/embedding-galaxy";
import { SimilarityCard } from "@/components/visualization/similarity-card";
import { MetricChart } from "@/components/visualization/metric-chart";
import { ExpandableViz } from "@/components/visualization/expandable-viz";
import { EpochSlider } from "@/components/visualization/epoch-slider";
import { topNeighbors } from "@/visualization/embedding-projection";
import { EMBED_DIM } from "@/training/models/embedding-lm";
import { LAB_DEMOS } from "@/lib/lab-demos";
import { embeddingsSchematic, LAB_SCHEMATIC_ACCENT } from "@/lib/lab-schematics";
import { LabWorkspace } from "@/components/layout/lab-workspace";
import { LabStat } from "@/components/labs/lab-stat";
import { LabSidebarPanel } from "@/components/labs/lab-sidebar-panel";
import { LabSchematicPanel } from "@/components/labs/lab-schematic-panel";
import { Button } from "@/components/ui/button";

const THEORY = [
  "Train only on next-token prediction — no similarity labels.",
  "Tokens in the same template slot cluster together.",
  "PCA reveals category structure the model was never told.",
] as const;

export function EmbeddingsLab(): React.ReactElement {
  const lab = useEmbeddingsLab();
  const galaxyRef = useRef<HTMLDivElement>(null);
  const [selectedTokenId, setSelectedTokenId] = useState<number | null>(null);

  const neighbors = useMemo(() => {
    if (selectedTokenId === null || !lab.snapshot) return [];
    return topNeighbors(
      lab.snapshot.embeddings,
      EMBED_DIM,
      selectedTokenId,
      lab.corpus.idToToken,
      3
    );
  }, [lab.snapshot, selectedTokenId, lab.corpus.idToToken]);

  const neighborIds = useMemo(
    () => neighbors.map((n) => lab.corpus.tokenToId[n.token]),
    [neighbors, lab.corpus.tokenToId]
  );

  const selectedToken =
    selectedTokenId !== null ? lab.corpus.idToToken[selectedTokenId] : null;

  const acc = lab.snapshot?.accuracy;

  const downloadPng = (): void => {
    const svg = galaxyRef.current?.querySelector("svg");
    if (!svg) return;
    const svgData = new XMLSerializer().serializeToString(svg);
    const canvas = document.createElement("canvas");
    canvas.width = 800;
    canvas.height = 800;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const img = new Image();
    img.onload = () => {
      ctx.fillStyle = "#fafaf9";
      ctx.fillRect(0, 0, 800, 800);
      ctx.drawImage(img, 0, 0, 800, 800);
      const link = document.createElement("a");
      link.download = "embedding-galaxy.png";
      link.href = canvas.toDataURL("image/png");
      link.click();
    };
    img.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svgData)}`;
  };

  const accHistory = lab.history.map((s) => ({
    epoch: s.epoch,
    value: s.accuracy,
  }));

  const galaxy = lab.snapshot ? (
    <EmbeddingGalaxy
      points={lab.snapshot.points}
      categories={lab.corpus.categories}
      frequencies={lab.corpus.frequencies}
      selectedTokenId={selectedTokenId}
      neighborIds={neighborIds}
      onSelect={setSelectedTokenId}
    />
  ) : (
    <div className="lab-viz-canvas-compact flex aspect-square items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--viz-canvas-bg)] text-xs text-[var(--text-muted)]">
      {lab.tfReady ? "Press Run to project embeddings" : "Loading TensorFlow.js…"}
    </div>
  );

  const neighborsPanel =
    selectedToken && lab.snapshot ? (
      <SimilarityCard
        token={selectedToken}
        category={lab.corpus.categories[selectedToken] ?? "other"}
        neighbors={neighbors}
      />
    ) : (
      <div className="flex h-full min-h-[120px] items-center justify-center rounded-lg border border-dashed border-[var(--border)] p-3 text-center text-xs text-[var(--text-muted)]">
        Click a point to see cosine neighbors
      </div>
    );

  return (
    <LabWorkspace
      labId="embeddings"
      experiment="Token embeddings"
      accentClass="text-[var(--lab-embeddings)]"
      demo={LAB_DEMOS.embeddings}
      problem="The model is never told which words are similar."
      solution="Next-token prediction alone pulls co-occurring tokens together — animals, fruits, and verbs form separate clusters in PCA space."
      stats={
        <>
          <LabStat
            size="sm"
            label="Next-token"
            value={acc === undefined ? "—" : `${(acc * 100).toFixed(0)}%`}
            accent
          />
          <LabStat size="sm" label="Vocab" value={String(lab.corpus.vocab.length)} />
          <LabStat size="sm" label="Selected" value={selectedToken ?? "—"} hint="click point" />
        </>
      }
      sidebar={
        <>
          <LabSidebarPanel title="Run experiment">
            <div className="flex flex-wrap gap-2">
              <Button
                className="flex-1"
                onClick={() => void lab.train()}
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
              {lab.status === "training" && (
                <Button variant="secondary" size="sm" onClick={lab.pause}>
                  <Pause className="h-4 w-4" />
                </Button>
              )}
              {lab.status === "paused" && (
                <Button variant="secondary" size="sm" onClick={lab.resume}>
                  <Play className="h-4 w-4" />
                </Button>
              )}
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
                variant="ghost"
                size="icon"
                onClick={downloadPng}
                disabled={!lab.snapshot}
                aria-label="Download PNG"
              >
                <Download className="h-4 w-4" />
              </Button>
            </div>
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
              {...embeddingsSchematic()}
              accentColor={LAB_SCHEMATIC_ACCENT.embeddings}
            />
          </LabSidebarPanel>

          <LabSidebarPanel title="Why this matters">
            <ul className="space-y-2 text-xs leading-relaxed text-[var(--text-secondary)]">
              {THEORY.map((t) => (
                <li key={t} className="flex gap-2">
                  <span className="text-[var(--lab-embeddings)]">→</span>
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
            historyA={lab.lossHistory}
            historyB={[]}
            currentEpoch={lab.currentEpoch}
            labelA="Embedding LM"
            labelB=""
            strokeB="var(--lab-embeddings)"
          />
          <MetricChart
            compact
            expandable
            title="Accuracy"
            historyA={accHistory}
            historyB={[]}
            currentEpoch={lab.currentEpoch}
            maxY={1}
            formatValue={(v) => `${(v * 100).toFixed(0)}%`}
            labelA="Top-1 next token"
            labelB=""
            strokeB="var(--lab-embeddings)"
          />
        </>
      }
      insight={
        lab.status === "complete" ? (
          <p className="rounded-lg border border-[var(--lab-embeddings)]/25 bg-[var(--lab-embeddings)]/5 px-3 py-2 text-xs leading-relaxed text-[var(--text-secondary)]">
            <span className="font-semibold text-[var(--text-primary)]">Proof: </span>
            Animals, fruits, and verbs cluster — the model only saw next-token prediction.
          </p>
        ) : (
          <p className="text-xs text-[var(--text-muted)]">
            Train embeddings · click galaxy or neighbors to expand
          </p>
        )
      }
    >
      <div className="grid gap-2 sm:grid-cols-2">
        <ExpandableViz
          label="Embedding galaxy (PCA)"
          disabled={!lab.snapshot}
          contentClassName="rounded-lg border border-[var(--border)] bg-[var(--viz-canvas-bg)]"
          expandedClassName="[&_.lab-viz-canvas-compact]:max-h-[min(72vh,560px)]"
        >
          <div ref={galaxyRef}>{galaxy}</div>
        </ExpandableViz>
        <ExpandableViz
          label="Nearest neighbors"
          disabled={!selectedToken}
          expandedClassName="max-w-md mx-auto"
        >
          {neighborsPanel}
        </ExpandableViz>
      </div>
    </LabWorkspace>
  );
}
