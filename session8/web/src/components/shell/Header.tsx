import { useApp } from "../../context/AppContext";
import { Clock, BookOpen, Sun, Moon, Monitor } from "lucide-react";

export function Header() {
  const { mode, toggleMode, setShowSixtySecond, theme, setTheme } = useApp();

  const cycleTheme = () => {
    const order = ["light", "dark", "system"] as const;
    const i = order.indexOf(theme);
    setTheme(order[(i + 1) % order.length]);
  };

  const ThemeIcon = theme === "dark" ? Moon : theme === "light" ? Sun : Monitor;

  return (
    <header className="site-header">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <a href="#chapter-0" className="focus-ring group flex min-w-0 items-baseline gap-3">
          <span className="font-serif text-lg font-semibold tracking-tight text-text sm:text-xl">
            Attention Evolution
          </span>
          <span className="hidden text-[11px] font-medium uppercase tracking-[0.14em] text-muted sm:inline">
            ERA V5 · Session 8
          </span>
        </a>

        <div className="flex shrink-0 items-center gap-1.5">
          <button
            type="button"
            onClick={() => setShowSixtySecond(true)}
            className="toolbar-btn hidden sm:inline-flex"
            aria-label="Explain attention in 60 seconds"
          >
            <Clock size={13} strokeWidth={2} aria-hidden />
            <span>60s</span>
          </button>

          <button
            type="button"
            onClick={cycleTheme}
            className="toolbar-btn capitalize"
            aria-label={`Theme: ${theme}. Click to change.`}
            title={`Theme: ${theme}`}
          >
            <ThemeIcon size={13} strokeWidth={2} aria-hidden />
            <span className="hidden sm:inline">{theme}</span>
          </button>

          <button
            type="button"
            onClick={toggleMode}
            className={`toolbar-btn font-semibold ${mode === "expert" ? "toolbar-btn-expert" : "toolbar-btn-beginner"}`}
            aria-pressed={mode === "expert"}
            aria-label={`Switch to ${mode === "beginner" ? "expert" : "beginner"} mode`}
          >
            <BookOpen size={13} strokeWidth={2} aria-hidden />
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
    <div className={`mode-banner ${mode === "expert" ? "mode-banner-expert" : ""}`}>
      {mode === "beginner" ? (
        <>Guided narrative — equations hidden. Toggle <strong>Expert</strong> for full technical depth.</>
      ) : (
        <>Expert view — equations, complexity metrics, and primary-source detail enabled.</>
      )}
    </div>
  );
}
