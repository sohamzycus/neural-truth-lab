import { useEffect } from "react";
import { CHAPTERS } from "../../data/chapters";
import { useApp } from "../../context/AppContext";

const NAV_CHAPTERS = CHAPTERS.filter((c) => c.id <= 12);

export function ChapterNav() {
  const { activeChapter, setActiveChapter } = useApp();

  useEffect(() => {
    const ids = NAV_CHAPTERS.map((c) => `chapter-${c.id}`);
    const elements = ids
      .map((id) => document.getElementById(id))
      .filter((el): el is HTMLElement => el !== null);

    if (!elements.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible?.target.id) {
          const num = Number(visible.target.id.replace("chapter-", ""));
          if (!Number.isNaN(num)) setActiveChapter(num);
        }
      },
      { rootMargin: "-20% 0px -55% 0px", threshold: [0, 0.25, 0.5] },
    );

    elements.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [setActiveChapter]);

  const go = (id: number) => {
    setActiveChapter(id);
    document.getElementById(`chapter-${id}`)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <nav
      className="sticky top-[57px] z-40 border-b border-theme bg-[var(--header-bg)] backdrop-blur-md"
      aria-label="All chapters"
    >
      <div className="mx-auto flex max-w-7xl gap-1 overflow-x-auto px-4 py-2 sm:px-6 scrollbar-thin">
        {NAV_CHAPTERS.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => go(c.id)}
            className={`focus-ring shrink-0 rounded-full px-3 py-1.5 text-xs font-medium transition-all ${
              activeChapter === c.id
                ? "bg-[var(--color-accent-soft)] text-[var(--color-accent)] shadow-sm"
                : "text-muted hover:bg-[var(--color-surface-2)] hover:text-text"
            }`}
            aria-current={activeChapter === c.id ? "true" : undefined}
          >
            <span className="font-mono opacity-60">{c.id}.</span> {c.title}
          </button>
        ))}
      </div>
    </nav>
  );
}
