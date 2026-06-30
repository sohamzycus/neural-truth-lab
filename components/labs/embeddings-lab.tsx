"use client";

import { useRef, useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, Pause, RotateCcw, Download, Loader2 } from "lucide-react";
import { useEmbeddingsLab } from "@/hooks/useEmbeddingsLab";
import { EmbeddingGalaxy } from "@/components/visualization/embedding-galaxy";
import { SimilarityCard } from "@/components/visualization/similarity-card";
import { MetricChart } from "@/components/visualization/metric-chart";
import { EpochSlider } from "@/components/visualization/epoch-slider";
import { topNeighbors } from "@/visualization/embedding-projection";
import { EMBED_DIM } from "@/training/models/embedding-lm";
import { Section } from "@/components/layout/section";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const THEORY_CHIPS = [
  "Embeddings map tokens to vectors",
  "Similar contexts pull words together",
  "PCA reveals cluster structure",
  "Neighbors reflect semantic similarity",
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
    () =>
      neighbors.map(
        (n) => lab.corpus.tokenToId[n.token]
      ),
    [neighbors, lab.corpus.tokenToId]
  );

  const selectedToken =
    selectedTokenId !== null ? lab.corpus.idToToken[selectedTokenId] : null;

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
      ctx.fillStyle = "#0a0a0f";
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

  return (
    <>
      <Section id="claim" eyebrow="Claim" title="The experiment">
        <div className="glass-panel border-l-4 border-l-[var(--lab-embeddings)] p-8">
          <p className="text-xl font-medium leading-relaxed text-[var(--text-primary)] md:text-2xl">
            Words that appear in similar contexts end up close together in
            embedding space.
          </p>
        </div>
      </Section>

      <Section id="theory" eyebrow="Theory" title="How embeddings learn">
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

      <Section id="experiment" eyebrow="Experiment" title="Train embeddings">
        <div className="mb-6 flex flex-wrap items-center gap-3">
          <Button
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
                Train Embeddings
              </>
            )}
          </Button>
          {lab.status === "training" && (
            <Button variant="secondary" onClick={lab.pause}>
              <Pause className="h-4 w-4" />
              Pause
            </Button>
          )}
          {lab.status === "paused" && (
            <Button variant="secondary" onClick={lab.resume}>
              <Play className="h-4 w-4" />
              Resume
            </Button>
          )}
          <Button variant="secondary" onClick={lab.reset} disabled={lab.status === "training"}>
            <RotateCcw className="h-4 w-4" />
            Reset
          </Button>
          <Button
            variant="secondary"
            onClick={lab.isReplaying ? lab.stopReplay : lab.replay}
            disabled={lab.history.length === 0}
          >
            {lab.isReplaying ? "Stop Replay" : "Replay"}
          </Button>
          <Button variant="ghost" onClick={downloadPng} disabled={!lab.snapshot}>
            <Download className="h-4 w-4" />
            PNG
          </Button>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div ref={galaxyRef} className="lg:col-span-2">
            {lab.snapshot ? (
              <EmbeddingGalaxy
                points={lab.snapshot.points}
                categories={lab.corpus.categories}
                frequencies={lab.corpus.frequencies}
                selectedTokenId={selectedTokenId}
                neighborIds={neighborIds}
                onSelect={setSelectedTokenId}
              />
            ) : (
              <div className="glass-panel flex aspect-square items-center justify-center rounded-xl border border-[var(--border)] text-[var(--text-muted)]">
                {lab.tfReady
                  ? "Press Train Embeddings to launch the galaxy"
                  : "Loading TensorFlow.js…"}
              </div>
            )}
          </div>
          <div>
            {selectedToken && lab.snapshot ? (
              <SimilarityCard
                token={selectedToken}
                category={lab.corpus.categories[selectedToken] ?? "other"}
                neighbors={neighbors}
              />
            ) : (
              <div className="glass-panel flex h-full min-h-[200px] items-center justify-center p-6 text-center text-sm text-[var(--text-muted)]">
                Click a star to see cosine similarity neighbors
              </div>
            )}
          </div>
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
        <div className="grid gap-4 lg:grid-cols-2">
          <MetricChart
            title="Loss"
            historyA={lab.lossHistory}
            historyB={[]}
            currentEpoch={lab.currentEpoch}
            labelA="Embedding LM"
            labelB=""
          />
          <MetricChart
            title="Accuracy (snapshot epochs)"
            historyA={accHistory}
            historyB={[]}
            currentEpoch={lab.currentEpoch}
            maxY={1}
            formatValue={(v) => `${(v * 100).toFixed(0)}%`}
            labelA="Top-1 next token"
            labelB=""
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
                "glass-panel border-l-4 border-l-[var(--lab-embeddings)] p-8",
                "shadow-[0_0_40px_rgba(168,85,247,0.15)]"
              )}
            >
              <p className="text-xl font-medium text-[var(--text-primary)] md:text-2xl">
                Words used in similar contexts end up close together.
              </p>
              <p className="mt-3 text-[var(--text-secondary)]">
                Embeddings encode meaning through context. Similar words attract;
                unrelated words repel — without ever being told the categories.
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
