import { AppProvider, useApp } from "./context/AppContext";
import { Header, ModeBanner } from "./components/shell/Header";
import { ChapterNav } from "./components/shell/ChapterNav";
import { OpeningSequence, QKVExperiment } from "./components/experiments/AttentionCore";
import { CausalMaskExperiment } from "./components/experiments/CausalMask";
import { QuadraticCost } from "./components/experiments/QuadraticCost";
import { KVCacheSimulator, MHAComparison } from "./components/experiments/KVCache";
import { PositionStory, RoPEVisualization, ContextWars } from "./components/experiments/Position";
import {
  LinearAttentionStory,
  DeltaNetMemory,
  MLACompression,
  FlashAttentionIO,
  AttentionSinks,
  ContextExtension,
} from "./components/experiments/Advanced";
import { MasterTimeline } from "./components/timeline/MasterTimeline";
import { FamilyTree } from "./components/timeline/FamilyTree";
import { ArchitectureLab } from "./components/lab/ArchitectureLab";
import { TryItOut } from "./components/game/TryItOut";
import { SixtySecondMode } from "./components/modes/SixtySecond";
import { SourceAudit } from "./components/audit/SourceAudit";
import { ChapterSection } from "./components/shell/ChapterSection";

function AppShell() {
  const { mode } = useApp();

  return (
    <div className="grid-bg min-h-screen" data-mode={mode}>
      <Header />
      <ModeBanner />
      <ChapterNav />
      <SixtySecondMode />

      <main className="mx-auto max-w-5xl px-4 pb-24 sm:px-6">
        <OpeningSequence />

        <ChapterSection id={1} />
        <ChapterSection id={2}>
          <QKVExperiment />
          <CausalMaskExperiment />
        </ChapterSection>

        <ChapterSection id={3}>
          <QuadraticCost />
          <FlashAttentionIO />
        </ChapterSection>

        <ChapterSection id={4}>
          <PositionStory />
          <RoPEVisualization />
          <ContextExtension />
        </ChapterSection>

        <ChapterSection id={5}>
          <KVCacheSimulator />
          <MHAComparison />
          <AttentionSinks />
        </ChapterSection>

        <ChapterSection id={6}>
          <ContextWars />
        </ChapterSection>

        <ChapterSection id={7}>
          <LinearAttentionStory />
          <DeltaNetMemory />
        </ChapterSection>

        <ChapterSection id={8}>
          <MLACompression />
        </ChapterSection>

        <ChapterSection id={9} />

        <ChapterSection id={10} title="Where Attention Is Going" subtitle="Hybrid systems, no single winner">
          <div className="panel p-6 text-sm text-muted">
            <p>
              The field is converging on <strong className="text-text">hybrid stacks</strong>: dense local attention + sparse global paths,
              RoPE with YaRN extension, GQA or MLA for KV, FlashAttention for IO, learned sparsity (DSA/CSA) for million-token paths,
              and recurrent layers (Mamba/DeltaNet) for infinite context segments.
            </p>
            <p className="mt-4">
              No single mechanism wins. The question is always: <em>which bottleneck are you paying for right now?</em>
            </p>
          </div>
        </ChapterSection>

        <div className="py-16">
          <MasterTimeline />
        </div>

        <ArchitectureLab />
        <TryItOut />

        <ChapterSection id={12} title="The Final Mental Model" subtitle="Negotiated compromises">
          <div className="panel p-6 text-sm leading-relaxed text-muted">
            <p>
              Attention did not evolve because researchers kept inventing &quot;better attention.&quot;
              It evolved because every useful solution exposed another bottleneck.
            </p>
            <ul className="mt-4 list-inside list-disc space-y-2">
              <li><strong className="text-text">Dense attention</strong> solved contextual retrieval → created quadratic cost</li>
              <li><strong className="text-text">Sparse attention</strong> reduced work → created connectivity problems</li>
              <li><strong className="text-text">Positional methods</strong> encoded order → created extrapolation problems</li>
              <li><strong className="text-text">MQA/GQA</strong> reduced KV memory → traded K/V diversity</li>
              <li><strong className="text-text">FlashAttention</strong> attacked hardware IO → without changing mathematical attention</li>
              <li><strong className="text-text">MLA</strong> compressed KV state → increased architectural complexity</li>
              <li><strong className="text-text">Linear/DeltaNet</strong> made memory recurrent → sacrificed unrestricted exact retrieval</li>
            </ul>
            <p className="mt-6 text-lg font-semibold text-[var(--color-accent)]">
              Modern attention is not one mechanism — it is an accumulation of engineering compromises.
            </p>
          </div>
        </ChapterSection>

        <FamilyTree />
        <SourceAudit />
      </main>

      <footer className="border-t border-theme py-8 text-center text-xs text-muted">
        ERA V5 Session 8 · Attention Evolution · Built for understanding, not decoration
      </footer>
    </div>
  );
}

function App() {
  return (
    <AppProvider>
      <AppShell />
    </AppProvider>
  );
}

export default App;
