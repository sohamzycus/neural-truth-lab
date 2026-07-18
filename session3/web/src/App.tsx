import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { BriefingStrip } from "./components/BriefingStrip";
import { ChapterChrome, ChapterTakeaway } from "./components/ChapterChrome";
import { DecisionMatrix } from "./components/DecisionMatrix";
import { DiagramGallery, DiagramTabs } from "./components/PipelineDiagrams";
import { FertilityExplorer } from "./components/FertilityExplorer";
import { InfographicPanels } from "./components/InfographicPanels";
import { LanguageMixCompare } from "./components/LanguageMixCompare";
import { ReadingProgress } from "./components/ReadingProgress";
import { ReportMarkdown } from "./components/ReportMarkdown";
import { UspSection } from "./components/UspSection";
import { downloadReportPdf } from "./lib/downloadPdf";
import { CHAPTER_META } from "./lib/chapterMeta";
import { parseChapters } from "./lib/parseReport";
import {
  loadJson,
  type FertilityProjections,
  type InferenceCosts,
  type LanguageWeights,
  type Matrix,
  type Scorecards,
  type TrainingBudget,
} from "./types";

type Tab = "overview" | "report" | "diagrams" | "explore";

const TABS: { id: Tab; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "report", label: "Report" },
  { id: "diagrams", label: "Architecture" },
  { id: "explore", label: "Explore" },
];

function TabPanel({ active, children }: { active: boolean; children: ReactNode }) {
  return (
    <div className={active ? "tab-panel tab-panel--active" : "tab-panel"} hidden={!active}>
      {children}
    </div>
  );
}

export default function App() {
  const [tab, setTab] = useState<Tab>("overview");
  const [chapterIdx, setChapterIdx] = useState(0);
  const [reportMd, setReportMd] = useState("");
  const [lang, setLang] = useState<LanguageWeights | null>(null);
  const [matrices, setMatrices] = useState<Record<string, Matrix>>({});
  const [fertility, setFertility] = useState<FertilityProjections | null>(null);
  const [inference, setInference] = useState<InferenceCosts | null>(null);
  const [budget, setBudget] = useState<TrainingBudget | null>(null);
  const [scorecards, setScorecards] = useState<Scorecards | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [pdfBusy, setPdfBusy] = useState(false);
  const [readProgress, setReadProgress] = useState(0);
  const articleRef = useRef<HTMLElement>(null);
  const chapterNavRef = useRef<HTMLDivElement>(null);
  const chapterBtnRefs = useRef<(HTMLButtonElement | null)[]>([]);

  const chapters = useMemo(() => parseChapters(reportMd), [reportMd]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const t = params.get("tab") as Tab | null;
    if (t && TABS.some((x) => x.id === t)) setTab(t);
    const ch = Number(params.get("chapter"));
    if (!Number.isNaN(ch) && ch >= 0) setChapterIdx(ch);
  }, []);

  const setUrl = (nextTab: Tab, ch?: number) => {
    const url = new URL(window.location.href);
    url.searchParams.set("tab", nextTab);
    if (ch !== undefined) url.searchParams.set("chapter", String(ch));
    window.history.replaceState({}, "", url);
  };

  const switchTab = (nextTab: Tab) => {
    if (nextTab === tab) return;
    setTab(nextTab);
    setUrl(nextTab, nextTab === "report" ? chapterIdx : undefined);
  };

  const goChapter = (i: number) => {
    setChapterIdx(i);
    if (tab !== "report") setTab("report");
    setUrl("report", i);
  };

  const handleDownloadPdf = async () => {
    if (!reportMd || pdfBusy) return;
    setPdfBusy(true);
    try {
      await downloadReportPdf(reportMd);
    } catch (e) {
      setLoadError(`PDF export failed: ${e}`);
    } finally {
      setPdfBusy(false);
    }
  };

  useEffect(() => {
    Promise.all([
      loadJson<LanguageWeights>("/data/language_weights.json"),
      loadJson<Record<string, Matrix>>("/data/matrices.json"),
      loadJson<FertilityProjections>("/data/fertility_projections.json"),
      loadJson<InferenceCosts>("/data/inference_costs.json"),
      loadJson<TrainingBudget>("/data/training_budget.json"),
      loadJson<Scorecards>("/data/scorecards.json"),
      fetch("/report.md").then((r) => {
        if (!r.ok) throw new Error("report.md missing");
        return r.text();
      }),
    ])
      .then(([lw, mx, fert, inf, bud, sc, md]) => {
        setLang(lw);
        setMatrices(mx);
        setFertility(fert);
        setInference(inf);
        setBudget(bud);
        setScorecards(sc);
        setReportMd(md);
      })
      .catch((e) => setLoadError(String(e)));
  }, []);

  const safeChapter = Math.min(chapterIdx, Math.max(0, chapters.length - 1));
  const currentChapter = chapters[safeChapter];
  const chapterMeta = currentChapter ? CHAPTER_META[currentChapter.num] : undefined;

  useEffect(() => {
    const el = articleRef.current;
    if (!el || tab !== "report") return;
    const onScroll = () => {
      const max = el.scrollHeight - el.clientHeight;
      setReadProgress(max > 0 ? el.scrollTop / max : 0);
    };
    el.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => el.removeEventListener("scroll", onScroll);
  }, [tab, safeChapter]);

  useEffect(() => {
    const el = articleRef.current;
    if (!el) return;
    el.scrollTop = 0;
    setReadProgress(0);
  }, [safeChapter]);

  useEffect(() => {
    chapterBtnRefs.current[safeChapter]?.scrollIntoView({ block: "nearest" });
  }, [safeChapter]);

  return (
    <div className="min-h-screen">
      {tab === "report" && (
        <ReadingProgress progress={(safeChapter + readProgress) / Math.max(chapters.length, 1)} />
      )}
      {loadError && (
        <div className="bg-red-100 px-4 py-2 text-center text-sm text-red-800">
          Run <code>python3 scripts/export_report_data.py</code> — {loadError}
        </div>
      )}

      <header className="hero-mesh relative text-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-end justify-between gap-3 px-4 py-4 md:py-5">
          <div>
            <p className="text-[9px] font-bold uppercase tracking-[0.2em] text-[var(--color-saffron)]">
              IN-40B-2026 · Internal Proposal
            </p>
            <h1 className="text-2xl font-extrabold tracking-tight md:text-3xl">
              India-First <span className="text-[var(--color-saffron)]">40B</span>
            </h1>
          </div>
          {budget && inference && (
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="stat-pill-compact">${budget.total_budget_usd_m}M · {budget.timeline_months}mo</span>
              <span className="stat-pill-compact">128k vocab</span>
              <span className="stat-pill-compact">22% TCO ↓</span>
              <button
                type="button"
                onClick={handleDownloadPdf}
                disabled={!reportMd || pdfBusy}
                className="stat-pill-compact cursor-pointer border-[var(--color-saffron)]/50 bg-[var(--color-saffron)]/20 font-semibold text-white transition hover:bg-[var(--color-saffron)]/35 disabled:cursor-wait disabled:opacity-50"
                title="Download full report as PDF"
              >
                {pdfBusy ? "Generating PDF…" : "↓ PDF"}
              </button>
            </div>
          )}
        </div>

        <nav className="site-tabs sticky top-0 z-20 border-t border-white/10 bg-[var(--color-indigo-deep)]/95 backdrop-blur-md">
          <div className="mx-auto flex max-w-6xl gap-1 overflow-x-auto px-4 py-2">
            {TABS.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => switchTab(t.id)}
                className={`site-tab ${tab === t.id ? "site-tab--active" : ""}`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6">
        <TabPanel active={tab === "overview"}>
          <div className="space-y-6">
            <UspSection />
            <InfographicPanels budget={budget} inference={inference} scorecards={scorecards} />
            <BriefingStrip budget={budget} inference={inference} scorecards={scorecards} onJump={goChapter} />
            <section>
              <h2 className="section-title">Training pipeline</h2>
              <DiagramGallery featuredOnly />
            </section>
            <div className="grid gap-5 lg:grid-cols-2">
              <FertilityExplorer fertility={fertility} inference={inference} />
              <LanguageMixCompare lang={lang} />
            </div>
          </div>
        </TabPanel>

        <TabPanel active={tab === "report"}>
          <div className="grid gap-5 lg:grid-cols-[220px_1fr]">
            <aside className="lg:sticky lg:top-[4.25rem] lg:self-start">
              <p className="mb-2 text-[10px] font-bold uppercase tracking-widest text-[var(--muted)]">
                {chapters.length} chapters
              </p>
              <nav ref={chapterNavRef} className="chapter-nav card max-h-[calc(100vh-5.5rem)] space-y-0.5 overflow-y-auto p-1.5 text-sm">
                {chapters.map((ch, i) => (
                  <button
                    key={ch.id}
                    type="button"
                    ref={(el) => {
                      chapterBtnRefs.current[i] = el;
                    }}
                    onClick={() => goChapter(i)}
                    className={`chapter-nav-btn ${safeChapter === i ? "chapter-nav-btn--active" : ""}`}
                    aria-current={safeChapter === i ? "true" : undefined}
                  >
                    <span className="chapter-nav-btn__num">{ch.shortTitle}</span>
                    <span className="chapter-nav-btn__label">{ch.title.replace(/^§\d+\s*/, "")}</span>
                  </button>
                ))}
              </nav>
            </aside>
            <article
              ref={articleRef}
              className="card report-prose report-article min-w-0 p-5 md:p-7"
            >
              {currentChapter && chapterMeta && <ChapterChrome meta={chapterMeta} />}
              {currentChapter ? (
                <ReportMarkdown markdown={currentChapter.markdown} />
              ) : (
                <p className="text-[var(--muted)]">Loading report…</p>
              )}
              {currentChapter && chapterMeta && <ChapterTakeaway meta={chapterMeta} />}
              <div className="mt-8 flex justify-between border-t border-[var(--border)] pt-3 text-sm">
                <button
                  type="button"
                  disabled={safeChapter <= 0}
                  onClick={() => goChapter(safeChapter - 1)}
                  className="font-semibold text-[var(--color-indigo)] disabled:opacity-30"
                >
                  ← Previous
                </button>
                <button
                  type="button"
                  disabled={safeChapter >= chapters.length - 1}
                  onClick={() => goChapter(safeChapter + 1)}
                  className="font-semibold text-[var(--color-indigo)] disabled:opacity-30"
                >
                  Next →
                </button>
              </div>
            </article>
          </div>
        </TabPanel>

        <TabPanel active={tab === "diagrams"}>
          <div className="space-y-4">
            <h2 className="section-title">Architecture diagrams</h2>
            <DiagramTabs />
          </div>
        </TabPanel>

        <TabPanel active={tab === "explore"}>
          <div className="space-y-6">
            <FertilityExplorer fertility={fertility} inference={inference} />
            <LanguageMixCompare lang={lang} />
            {Object.values(matrices).length > 0 && (
              <section>
                <h2 className="section-title">Decision matrices</h2>
                {Object.values(matrices).map((m) => (
                  <DecisionMatrix key={m.id} matrix={m} />
                ))}
              </section>
            )}
          </div>
        </TabPanel>
      </main>

      <footer className="border-t border-[var(--border)] py-5 text-center text-xs text-[var(--muted)]">
        erav5 session3
      </footer>
    </div>
  );
}
