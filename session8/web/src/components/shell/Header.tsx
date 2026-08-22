import { useApp } from "../../context/AppContext";
import { Clock, BookOpen, Zap, Sun, Moon, Monitor } from "lucide-react";

export function Header() {
  const { mode, toggleMode, setShowSixtySecond, theme, setTheme } = useApp();

  const cycleTheme = () => {
    const order = ["light", "dark", "system"] as const;
    const i = order.indexOf(theme);
    setTheme(order[(i + 1) % order.length]);
  };

  const ThemeIcon = theme === "dark" ? Moon : theme === "light" ? Sun : Monitor;

  return (
    <header className="sticky top-0 z-50 border-b border-theme bg-[var(--header-bg)] backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-3 sm:px-6">
        <a href="#chapter-0" className="focus-ring flex items-center gap-3 rounded-lg">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--color-accent-soft)] text-[var(--color-accent)]">
            <Zap size={18} aria-hidden />
          </div>
          <div>
            <p className="text-sm font-semibold tracking-tight">Attention Evolution</p>
            <p className="text-xs text-muted">ERA V5 · Session 8</p>
          </div>
        </a>

        <div className="flex items-center gap-1.5 sm:gap-2">
          <button
            type="button"
            onClick={() => setShowSixtySecond(true)}
            className="focus-ring hidden items-center gap-1.5 rounded-lg border border-theme px-2.5 py-1.5 text-xs text-muted hover:border-[var(--color-accent)] hover:text-[var(--color-accent)] sm:flex"
            aria-label="Explain attention in 60 seconds"
          >
            <Clock size={14} aria-hidden />
            60 sec
          </button>

          <button
            type="button"
            onClick={cycleTheme}
            className="focus-ring flex items-center gap-1 rounded-lg border border-theme px-2.5 py-1.5 text-xs text-muted capitalize hover:border-theme"
            aria-label={`Theme: ${theme}. Click to change.`}
            title={`Theme: ${theme}`}
          >
            <ThemeIcon size={14} aria-hidden />
            <span className="hidden sm:inline">{theme}</span>
          </button>

          <button
            type="button"
            onClick={toggleMode}
            className={`focus-ring flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs font-semibold transition-colors ${
              mode === "expert"
                ? "border-violet/40 bg-violet/10 text-violet"
                : "border-[var(--color-accent)]/40 bg-[var(--color-accent-soft)] text-[var(--color-accent)]"
            }`}
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

export function ModeBanner() {
  const { mode } = useApp();
  return (
    <div
      className={`border-b px-4 py-2 text-center text-xs sm:text-sm ${
        mode === "beginner"
          ? "border-[var(--color-accent)]/20 bg-[var(--color-accent-soft)] text-[var(--color-accent)]"
          : "border-violet/20 bg-violet/10 text-violet"
      }`}
    >
      {mode === "beginner" ? (
        <>Guided path — plain language, hidden formulas. Switch to <strong>Expert</strong> for equations & complexity.</>
      ) : (
        <>Expert mode — full equations, complexity metrics, and technical trade-off cards visible.</>
      )}
    </div>
  );
}
