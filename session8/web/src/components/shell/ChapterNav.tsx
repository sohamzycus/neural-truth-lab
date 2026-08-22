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
      { rootMargin: "-18% 0px -58% 0px", threshold: [0, 0.2, 0.45] },
    );

    elements.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [setActiveChapter]);

  const go = (id: number) => {
    setActiveChapter(id);
    document.getElementById(`chapter-${id}`)?.scrollIntoView({ behavior: "smooth" });
  };

  const progress = (activeChapter / (NAV_CHAPTERS.length - 1)) * 100;

  return (
    <nav className="chapter-nav" aria-label="Chapter navigation">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="chapter-nav-grid">
          {NAV_CHAPTERS.map((c) => {
            const active = activeChapter === c.id;
            return (
              <button
                key={c.id}
                type="button"
                onClick={() => go(c.id)}
                title={`Ch. ${c.id}: ${c.title}`}
                className={`chapter-nav-item focus-ring ${active ? "chapter-nav-item-active" : ""}`}
                aria-current={active ? "true" : undefined}
              >
                <span className="chapter-nav-num">{c.id}</span>
                <span className="chapter-nav-label">{c.navLabel}</span>
              </button>
            );
          })}
        </div>
        <div className="chapter-nav-progress" aria-hidden>
          <div className="chapter-nav-progress-fill" style={{ width: `${progress}%` }} />
        </div>
      </div>
    </nav>
  );
}
