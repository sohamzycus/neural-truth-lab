import { useEffect, useState } from "react";
import { AppShell } from "./components/shell/AppShell";
import { HealthMonitor } from "./components/monitor/HealthMonitor";
import { HeroSection } from "./components/sections/HeroSection";
import { WhyNotesSection } from "./components/sections/WhyNotesSection";
import { DatasetSection } from "./components/sections/DatasetSection";
import { RawSection } from "./components/sections/RawSection";
import { StrategiesSection } from "./components/sections/StrategiesSection";
import { DomainSection } from "./components/sections/DomainSection";
import { SurgerySection } from "./components/sections/SurgerySection";
import { CompareSection } from "./components/sections/CompareSection";
import { DiscoveriesSection } from "./components/sections/DiscoveriesSection";
import { StatsSection } from "./components/sections/StatsSection";
import { RoadmapSection } from "./components/sections/RoadmapSection";
import { LessonsSection } from "./components/sections/LessonsSection";
import type {
  Comparison,
  CorpusStats,
  DatasetStats,
  Discovery,
  DomainEnhancement,
  HealthBaseline,
  Lesson,
  RawObservation,
  RoadmapItem,
  ScrubSample,
  Strategy,
  SurgeryMetrics,
} from "./types";

async function loadJson<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load ${path}`);
  return res.json() as Promise<T>;
}

type Bundle = {
  dataset: DatasetStats;
  raw: RawObservation[];
  strategies: Strategy[];
  domain: DomainEnhancement[];
  surgery: SurgeryMetrics;
  comparisons: Comparison[];
  discoveries: Discovery[];
  stats: CorpusStats;
  roadmap: RoadmapItem[];
  lessons: Lesson[];
  health: HealthBaseline;
  scrub: ScrubSample[];
};

export default function App() {
  const [data, setData] = useState<Bundle | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      loadJson<DatasetStats>("/data/dataset_stats.json"),
      loadJson<RawObservation[]>("/data/raw_observations.json"),
      loadJson<Strategy[]>("/data/strategies.json"),
      loadJson<DomainEnhancement[]>("/data/domain_enhancements.json"),
      loadJson<SurgeryMetrics>("/data/surgery_metrics.json"),
      loadJson<Comparison[]>("/data/comparisons.json"),
      loadJson<Discovery[]>("/data/discoveries.json"),
      loadJson<CorpusStats>("/data/corpus_stats.json"),
      loadJson<RoadmapItem[]>("/data/roadmap.json"),
      loadJson<Lesson[]>("/data/lessons.json"),
      loadJson<HealthBaseline>("/data/health_baseline.json"),
      loadJson<ScrubSample[]>("/data/scrub_samples.json"),
    ])
      .then(
        ([
          dataset,
          raw,
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
        ]) =>
          setData({
            dataset,
            raw,
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
      <HeroSection />
      <WhyNotesSection />
      <DatasetSection data={data.dataset} />
      <RawSection data={data.raw} />
      <StrategiesSection strategies={data.strategies} />
      <DomainSection items={data.domain} />
      <SurgerySection metrics={data.surgery} />
      <CompareSection comparisons={data.comparisons} samples={data.scrub} />
      <DiscoveriesSection items={data.discoveries} />
      <StatsSection stats={data.stats} />
      <RoadmapSection items={data.roadmap} />
      <LessonsSection lessons={data.lessons} />
      <HealthMonitor baseline={data.health} />
    </AppShell>
  );
}
