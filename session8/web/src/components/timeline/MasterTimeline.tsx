import { useApp } from "../../context/AppContext";
import { CHRONOLOGY } from "../../data/chronology";
import { PressureBar } from "./PressureBar";

export function MasterTimeline() {
  const { activeEntryId, setActiveEntryId, setActiveChapter } = useApp();
  const years = [...new Set(CHRONOLOGY.map((e) => e.year))].sort();

  return (
    <section id="timeline" className="scroll-mt-20" aria-labelledby="timeline-heading">
      <div className="mb-6">
        <h2 id="timeline-heading" className="text-2xl font-bold tracking-tight sm:text-3xl">
          Master Timeline
        </h2>
        <p className="mt-2 max-w-2xl text-muted">
          Chronology drives the story. Select any node to see problem → idea → trade-off.
        </p>
      </div>

      <PressureBar year={CHRONOLOGY.find((e) => e.id === activeEntryId)?.year ?? 2017} />

      <div className="mt-8 overflow-x-auto pb-4">
        <div className="flex min-w-max gap-0 px-2">
          {years.map((year) => (
            <div key={year} className="flex flex-col items-center">
              <span className="mb-3 text-xs font-mono text-muted">{year}</span>
              <div className="flex flex-col gap-3 border-l border-white/10 pl-4">
                {CHRONOLOGY.filter((e) => e.year === year).map((entry) => (
                  <button
                    key={entry.id}
                    type="button"
                    onClick={() => {
                      setActiveEntryId(entry.id);
                      setActiveChapter(entry.chapter);
                      document.getElementById(`chapter-${entry.chapter}`)?.scrollIntoView({ behavior: "smooth" });
                    }}
                    className={`focus-ring group w-44 rounded-lg border px-3 py-2 text-left transition ${
                      activeEntryId === entry.id
                        ? "border-cyan/50 bg-cyan/10"
                        : "border-white/10 bg-surface hover:border-white/20"
                    }`}
                    aria-pressed={activeEntryId === entry.id}
                  >
                    <p className="text-xs font-semibold text-cyan">{entry.title}</p>
                    <p className="mt-0.5 line-clamp-2 text-[10px] text-muted">{entry.fullName}</p>
                    <span className="mt-1 inline-block rounded bg-white/5 px-1.5 py-0.5 text-[9px] uppercase text-muted">
                      {entry.sourceType}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
