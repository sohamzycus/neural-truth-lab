import { useEffect, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import { BriefingStrip } from "./components/BriefingStrip";
import { DecisionMatrix } from "./components/DecisionMatrix";
import { DiagramGallery } from "./components/DiagramGallery";
import { FertilityExplorer } from "./components/FertilityExplorer";
import { LanguageMixCompare } from "./components/LanguageMixCompare";
import { UspSection } from "./components/UspSection";
import { parseChapters } from "./lib/parseReport";
import {
  loadJson,
  type DataMix,
  type FertilityProjections,
  type InferenceCosts,
  type LanguageWeights,
  type Matrix,
  type Scorecards,
  type TrainingBudget,
} from "./types";

type Tab = "overview" | "report" | "diagrams" | "explore";

const TABS: { id: Tab; label: string }[] = [
  { id: "overview", label: "Overview & USP" },
  { id: "report", label: "Report" },
  { id: "diagrams", label: "Architecture" },
  { id: "explore", label: "Explore" },
];

export default function App() {
  const [tab, setTab] = useState<Tab>("overview");
  const [chapterIdx, setChapterIdx] = useState(0);
  const [reportMd, setReportMd] = useState("");
  const [lang, setLang] = useState<LanguageWeights | null>(null);
  const [mix, setMix] = useState<DataMix | null>(null);
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
      loadJson<DataMix>("/data/data_mix.json"),
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
      .then(([lw, dm, mx, fert, inf, bud, sc, md]) => {
        setLang(lw);
        setMix(dm);
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
    <div className="min-h-screen font-ui">
      {loadError && (
        <div className="bg-red-100 px-4 py-2 text-center text-sm text-red-800">
          Data load failed — run <code>python3 scripts/export_report_data.py</code> ({loadError})
        </div>
      )}

      <header className="bg-[var(--ink)] text-white">
        <div className="mx-auto max-w-7xl px-4 py-2 font-mono text-[10px] tracking-wider text-white/45">
          DOC-ID: IN-40B-2026 · INTERNAL · PYTHON-DERIVED NUMBERS ONLY
        </div>
        <div className="mx-auto max-w-7xl px-4 pb-6">
          <p className="text-xs font-semibold uppercase tracking-widest text-[var(--accent)]">
            India-First 40B · Research Proposal
          </p>
          <h1
            className="mt-2 text-3xl font-bold leading-tight md:text-4xl"
            style={{ fontFamily: "Source Serif 4, serif" }}
          >
            Forty billion parameters.
            <br />
            <span className="text-white/85">One deployment constraint: India.</span>
          </h1>
        </div>

        <nav className="border-t border-white/10">
          <div className="mx-auto flex max-w-7xl gap-1 overflow-x-auto px-4">
            {TABS.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => navigate(t.id)}
                className={`shrink-0 border-b-2 px-4 py-3 text-sm font-medium transition ${
                  tab === t.id
                    ? "border-[var(--accent)] text-white"
                    : "border-transparent text-white/55 hover:text-white"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </nav>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-8">
        {tab === "overview" && (
          <div className="space-y-8">
            <UspSection />
            <BriefingStrip
              budget={budget}
              inference={inference}
              scorecards={scorecards}
              onJump={goChapter}
            />
            <div className="grid gap-6 lg:grid-cols-2">
              <FertilityExplorer fertility={fertility} inference={inference} />
              <LanguageMixCompare lang={lang} />
            </div>
            <section>
              <h2 className="mb-4 text-lg font-bold">Training pipeline (preview)</h2>
              <DiagramGallery compact />
            </section>
          </div>
        )}

        {tab === "report" && (
          <div className="grid gap-8 lg:grid-cols-[240px_1fr]">
            <aside className="lg:sticky lg:top-4 lg:self-start">
              <p className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-[var(--muted)]">
                Chapters ({chapters.length})
              </p>
              <nav className="max-h-[70vh] space-y-0.5 overflow-y-auto text-sm">
                {chapters.map((ch, i) => (
                  <button
                    key={ch.id}
                    type="button"
                    onClick={() => goChapter(i)}
                    className={`block w-full rounded px-3 py-2 text-left transition ${
                      safeChapter === i
                        ? "bg-[var(--ink)] text-white"
                        : "text-[var(--muted)] hover:bg-white"
                    }`}
                  >
                    {ch.title}
                  </button>
                ))}
              </nav>
            </aside>
            <article className="report-prose rounded-lg border border-[var(--border)] bg-white p-6 md:p-8">
              {currentChapter ? (
                <ReactMarkdown>{currentChapter.markdown}</ReactMarkdown>
              ) : (
                <p className="text-[var(--muted)]">Loading report…</p>
              )}
              <div className="mt-8 flex justify-between border-t border-[var(--border)] pt-4">
                <button
                  type="button"
                  disabled={safeChapter <= 0}
                  onClick={() => goChapter(safeChapter - 1)}
                  className="text-sm text-[var(--accent-2)] disabled:opacity-30"
                >
                  ← Previous
                </button>
                <button
                  type="button"
                  disabled={safeChapter >= chapters.length - 1}
                  onClick={() => goChapter(safeChapter + 1)}
                  className="text-sm text-[var(--accent-2)] disabled:opacity-30"
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
              <h2 className="text-xl font-bold">Architecture diagrams</h2>
              <p className="mt-1 text-sm text-[var(--muted)]">
                8 pipelines from the design proposal — rendered from Mermaid sources in{" "}
                <code>diagrams/src/</code>
              </p>
            </div>
            <DiagramGallery />
          </div>
        )}

        {tab === "explore" && (
          <div className="space-y-8">
            <FertilityExplorer fertility={fertility} inference={inference} />
            <LanguageMixCompare lang={lang} />
            {Object.values(matrices).length > 0 && (
              <section>
                <h2 className="mb-2 text-xl font-bold">Decision matrices</h2>
                <p className="mb-4 text-sm text-[var(--muted)]">
                  Drag criterion weights — see if our locked decisions still win.
                </p>
                {Object.values(matrices).map((m) => (
                  <DecisionMatrix key={m.id} matrix={m} />
                ))}
              </section>
            )}
          </div>
        )}
      </div>

      <footer className="mt-12 border-t border-[var(--border)] py-6 text-center text-xs text-[var(--muted)]">
        erav5 session3 · <code>python3 scripts/derive_all.py</code> ·{" "}
        <a href="?tab=overview" className="text-[var(--accent-2)] underline">
          Overview
        </a>
      </footer>
    </div>
  );
}
