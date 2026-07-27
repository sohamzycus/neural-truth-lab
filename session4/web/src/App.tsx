import { useEffect, useState } from "react";
import { AppShell } from "./components/shell/AppShell";
import { HealthMonitor } from "./components/monitor/HealthMonitor";
import { HeroSection } from "./components/sections/HeroSection";
import { WhyNotesSection } from "./components/sections/WhyNotesSection";
import { CorpusDownloadSection } from "./components/sections/CorpusDownloadSection";
import { DatasetSection } from "./components/sections/DatasetSection";
import { RawSection } from "./components/sections/RawSection";
import { PipelineSection } from "./components/sections/PipelineSection";
import { StrategiesSection } from "./components/sections/StrategiesSection";
import { DomainSection } from "./components/sections/DomainSection";
import { SurgerySection } from "./components/sections/SurgerySection";
import { CompareSection } from "./components/sections/CompareSection";
import { DiscoveriesSection } from "./components/sections/DiscoveriesSection";
import { StatsSection } from "./components/sections/StatsSection";
import { RoadmapSection } from "./components/sections/RoadmapSection";
import { ShardEvidenceSection } from "./components/sections/ShardEvidenceSection";
import { LessonsSection } from "./components/sections/LessonsSection";
import type {
  Comparison,
  CorpusStats,
  DatasetStats,
  Discovery,
  DomainEnhancement,
  HealthSyncConfig,
  Lesson,
  PipelineStage,
  RawObservation,
  RoadmapItem,
  ScrubSample,
  Strategy,
  SurgeryMetrics,
  ShardPipelineRun,
  BenchmarkQuiz,
  CorpusDownloadPackage,
} from "./types";

async function loadJson<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load ${path}`);
  return res.json() as Promise<T>;
}

type Bundle = {
  dataset: DatasetStats;
  raw: RawObservation[];
  pipeline: PipelineStage[];
  strategies: Strategy[];
  domain: DomainEnhancement[];
  surgery: SurgeryMetrics;
  comparisons: Comparison[];
  discoveries: Discovery[];
  stats: CorpusStats;
  roadmap: RoadmapItem[];
  lessons: Lesson[];
  health: HealthSyncConfig;
  scrub: ScrubSample[];
  shardRun: ShardPipelineRun;
  quiz: BenchmarkQuiz;
  downloadPkg: CorpusDownloadPackage;
};

export default function App() {
  const [data, setData] = useState<Bundle | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      loadJson<DatasetStats>("/data/dataset_stats.json"),
      loadJson<RawObservation[]>("/data/raw_observations.json"),
      loadJson<PipelineStage[]>("/data/pipeline_stages.json"),
      loadJson<Strategy[]>("/data/strategies.json"),
      loadJson<DomainEnhancement[]>("/data/domain_enhancements.json"),
      loadJson<SurgeryMetrics>("/data/surgery_metrics.json"),
      loadJson<Comparison[]>("/data/comparisons.json"),
      loadJson<Discovery[]>("/data/discoveries.json"),
      loadJson<CorpusStats>("/data/corpus_stats.json"),
      loadJson<RoadmapItem[]>("/data/roadmap.json"),
      loadJson<Lesson[]>("/data/lessons.json"),
      loadJson<HealthSyncConfig>("/data/health_sync.json"),
      loadJson<ScrubSample[]>("/data/scrub_samples.json"),
      loadJson<ShardPipelineRun>("/data/shard_pipeline_run.json"),
      loadJson<BenchmarkQuiz>("/data/benchmark_quiz.json"),
      loadJson<CorpusDownloadPackage>("/data/corpus_download_package.json"),
    ])
      .then(
        ([
          dataset,
          raw,
          pipeline,
          strategies,
          domain,
          surgery,
          comparisons,
          discoveries,
          stats,
          roadmap,
          lessons,
          health,
          scrub,
          shardRun,
          quiz,
          downloadPkg,
        ]) =>
          setData({
            dataset,
            raw,
            pipeline,
            strategies,
            domain,
            surgery,
            comparisons,
            discoveries,
            stats,
            roadmap,
            lessons,
            health,
            scrub,
            shardRun,
            quiz,
            downloadPkg,
          }),
      )
      .catch((e: Error) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center px-6 text-center text-[var(--color-muted)]">
        Unable to load corpus data: {error}
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex min-h-screen items-center justify-center font-mono text-sm text-[var(--color-muted)]">
        Loading Corpus Forge…
      </div>
    );
  }

  return (
    <AppShell>
      <HeroSection
        observationCount={data.dataset.observationCount}
        observerCount={data.dataset.observerCount}
        rawSample={data.raw}
      />
      <WhyNotesSection />
      <DatasetSection data={data.dataset} />
      <CorpusDownloadSection pkg={data.downloadPkg} observationCount={data.dataset.observationCount} />
      <RawSection data={data.raw} totalCorpus={data.dataset.observationCount} />
      <PipelineSection stages={data.pipeline} />
      <StrategiesSection strategies={data.strategies} />
      <DomainSection items={data.domain} />
      <SurgerySection metrics={data.surgery} />
      <ShardEvidenceSection run={data.shardRun} />
      <CompareSection comparisons={data.comparisons} samples={data.scrub} quizPhrases={data.quiz.phrases} />
      <DiscoveriesSection items={data.discoveries} observationCount={data.dataset.observationCount} />
      <StatsSection stats={data.stats} />
      <RoadmapSection items={data.roadmap} />
      <LessonsSection lessons={data.lessons} />
      <HealthMonitor config={data.health} />
    </AppShell>
  );
}
