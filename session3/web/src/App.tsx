import { useEffect, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import { BriefingStrip } from "./components/BriefingStrip";
import { DecisionMatrix } from "./components/DecisionMatrix";
import { DiagramGallery, DiagramTabs } from "./components/PipelineDiagrams";
import { FertilityExplorer } from "./components/FertilityExplorer";
import { LanguageMixCompare } from "./components/LanguageMixCompare";
import { UspSection } from "./components/UspSection";
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

const TRUST = [
  "Python-derived numbers",
  "128k India tokenizer",
  "7-factor MCDA weights",
  "13-chapter proposal",
];

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

  const chapters = useMemo(() => parseChapters(reportMd), [reportMd]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const t = params.get("tab") as Tab | null;
    if (t && TABS.some((x) => x.id === t)) setTab(t);
    const ch = Number(params.get("chapter"));
    if (!Number.isNaN(ch) && ch >= 0) setChapterIdx(ch);
  }, []);

  const navigate = (nextTab: Tab, ch?: number) => {
    setTab(nextTab);
    if (ch !== undefined) setChapterIdx(ch);
    const url = new URL(window.location.href);
    url.searchParams.set("tab", nextTab);
    if (ch !== undefined) url.searchParams.set("chapter", String(ch));
    window.history.replaceState({}, "", url);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const goChapter = (i: number) => {
    setChapterIdx(i);
    navigate("report", i);
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

  return (
    <div className="min-h-screen">
      {loadError && (
        <div className="bg-red-100 px-4 py-2 text-center text-sm text-red-800">
          Run <code>python3 scripts/export_report_data.py</code> — {loadError}
        </div>
      )}

      <header className="hero-mesh relative overflow-hidden text-white">
        <span className="script-watermark left-4 top-8 text-white">४०B</span>
        <span className="script-watermark right-8 top-24 font-[family-name:var(--font-serif)] text-white">भारत</span>
        <div className="relative mx-auto max-w-6xl px-4 pb-8 pt-10 md:pt-14">
          <p className="text-[10px] font-bold uppercase tracking-[0.3em] text-[var(--color-saffron)]">
            Internal Research Proposal · IN-40B-2026
          </p>
          <h1 className="mt-3 text-[clamp(2.25rem,6vw,4.5rem)] font-extrabold leading-[1.05] tracking-tight">
            India-First 40B
          </h1>
          <p className="mt-3 max-w-2xl text-lg font-semibold text-white/90 md:text-xl">
            Forty billion parameters. One deployment constraint:{" "}
            <span className="text-[var(--color-saffron)]">India.</span>
          </p>
          <p className="mt-2 max-w-xl text-sm text-white/65">
            Spec-driven $100M foundation model design — tokenizer fertility, MCDA language weights,
            inference TCO. Every number from <code className="text-white/80">derive_all.py</code>.
          </p>
          <ul className="mt-6 flex flex-wrap gap-2">
            {TRUST.map((t) => (
              <li
                key={t}
                className="rounded-full border border-white/25 bg-white/10 px-3 py-1 text-xs font-medium backdrop-blur-sm"
              >
                {t}
              </li>
            ))}
          </ul>
        </div>

        <nav className="relative border-t border-white/15 bg-black/20 backdrop-blur-md">
          <div className="mx-auto flex max-w-6xl gap-1 overflow-x-auto px-4">
            {TABS.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => navigate(t.id)}
                className={`shrink-0 px-5 py-3.5 text-sm font-semibold transition ${
                  tab === t.id
                    ? "border-b-2 border-[var(--color-saffron)] text-white"
                    : "text-white/55 hover:text-white"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </nav>
      </header>

      <div className="mx-auto max-w-6xl px-4 py-10">
        {tab === "overview" && (
          <div className="space-y-10">
            <UspSection />
            <BriefingStrip budget={budget} inference={inference} scorecards={scorecards} onJump={goChapter} />
            <section>
              <h2 className="mb-4 text-lg font-bold text-[var(--color-indigo)]">Training pipeline</h2>
              <DiagramGallery featuredOnly />
            </section>
            <div className="grid gap-6 lg:grid-cols-2">
              <FertilityExplorer fertility={fertility} inference={inference} />
              <LanguageMixCompare lang={lang} />
            </div>
          </div>
        )}

        {tab === "report" && (
          <div className="grid gap-8 lg:grid-cols-[260px_1fr]">
            <aside className="lg:sticky lg:top-4 lg:self-start">
              <p className="mb-3 text-[10px] font-bold uppercase tracking-widest text-[var(--muted)]">
                {chapters.length} chapters
              </p>
              <nav className="card max-h-[70vh] space-y-0.5 overflow-y-auto p-2 text-sm">
                {chapters.map((ch, i) => (
                  <button
                    key={ch.id}
                    type="button"
                    onClick={() => goChapter(i)}
                    className={`block w-full rounded-lg px-3 py-2 text-left transition ${
                      safeChapter === i
                        ? "bg-[var(--color-indigo)] font-semibold text-white"
                        : "text-[var(--muted)] hover:bg-white"
                    }`}
                  >
                    {ch.title}
                  </button>
                ))}
              </nav>
            </aside>
            <article className="card report-prose p-6 md:p-10">
              {currentChapter ? (
                <ReactMarkdown>{currentChapter.markdown}</ReactMarkdown>
              ) : (
                <p className="text-[var(--muted)]">Loading report…</p>
              )}
              <div className="mt-10 flex justify-between border-t border-[var(--border)] pt-4 font-sans text-sm">
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
        )}

        {tab === "diagrams" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-extrabold text-[var(--color-indigo)]">Architecture diagrams</h2>
              <p className="mt-1 text-sm text-[var(--muted)]">
                Six pipelines from the design proposal — objectives through deployment.
              </p>
            </div>
            <DiagramTabs />
            <DiagramGallery />
          </div>
        )}

        {tab === "explore" && (
          <div className="space-y-8">
            <FertilityExplorer fertility={fertility} inference={inference} />
            <LanguageMixCompare lang={lang} />
            {Object.values(matrices).length > 0 && (
              <section>
                <h2 className="text-xl font-bold">Decision matrices</h2>
                <p className="mb-4 text-sm text-[var(--muted)]">
                  Drag criterion weights — see if locked decisions still win.
                </p>
                {Object.values(matrices).map((m) => (
                  <DecisionMatrix key={m.id} matrix={m} />
                ))}
              </section>
            )}
          </div>
        )}
      </div>

      <footer className="border-t border-[var(--border)] py-8 text-center text-xs text-[var(--muted)]">
        erav5 session3 · <a href="?tab=overview" className="text-[var(--color-indigo)] underline">Overview</a>
      </footer>
    </div>
  );
}
