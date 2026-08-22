import { useApp } from "../../context/AppContext";
import { CHAPTERS } from "../../data/chapters";
import { Clock, BookOpen, Zap } from "lucide-react";

export function Header() {
  const { mode, toggleMode, setShowSixtySecond } = useApp();

  return (
    <header className="sticky top-0 z-50 border-b border-white/8 bg-[#06080f]/85 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan/15 text-cyan">
            <Zap size={18} aria-hidden />
          </div>
          <div>
            <p className="text-sm font-semibold tracking-tight">Attention Evolution</p>
            <p className="text-xs text-muted">ERA V5 · Session 8</p>
          </div>
        </div>

        <nav className="hidden items-center gap-2 md:flex" aria-label="Quick navigation">
          {CHAPTERS.slice(0, 4).map((c) => (
            <a
              key={c.id}
              href={`#chapter-${c.id}`}
              className="focus-ring rounded-md px-2 py-1 text-xs text-muted hover:text-text"
            >
              {c.title}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setShowSixtySecond(true)}
            className="focus-ring hidden items-center gap-1.5 rounded-lg border border-white/10 px-3 py-1.5 text-xs text-muted hover:border-cyan/30 hover:text-cyan sm:flex"
            aria-label="Explain attention in 60 seconds"
          >
            <Clock size={14} aria-hidden />
            60 sec
          </button>
          <button
            type="button"
            onClick={toggleMode}
            className="focus-ring flex items-center gap-1.5 rounded-lg border border-white/10 px-3 py-1.5 text-xs font-medium hover:border-violet/30"
            aria-pressed={mode === "expert"}
            aria-label={`Switch to ${mode === "beginner" ? "expert" : "beginner"} mode`}
          >
            <BookOpen size={14} aria-hidden />
            {mode === "beginner" ? "Beginner" : "Expert"}
          </button>
        </div>
      </div>
    </header>
  );
}
