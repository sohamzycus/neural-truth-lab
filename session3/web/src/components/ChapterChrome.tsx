import type { ChapterMeta } from "../lib/chapterMeta";

export function ChapterChrome({ meta }: { meta: ChapterMeta }) {
  return (
    <div className="chapter-hero">
      <p className="chapter-hero__insight">{meta.insight}</p>
      <ul className="chapter-hero__bullets">
        {meta.bullets.map((b) => (
          <li key={b}>{b}</li>
        ))}
      </ul>
    </div>
  );
}

export function ChapterTakeaway({ meta }: { meta: ChapterMeta }) {
  return (
    <div className="chapter-takeaway">
      <span className="chapter-takeaway__label">Key Takeaway</span>
      <p>{meta.takeaway}</p>
    </div>
  );
}
