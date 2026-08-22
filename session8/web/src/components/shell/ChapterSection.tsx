import type { ReactNode } from "react";
import { CHAPTERS } from "../../data/chapters";
import { byChapter } from "../../data/chronology";
import { TradeoffCard } from "../ui/TradeoffCard";

export function ChapterSection({
  id,
  title,
  subtitle,
  children,
}: {
  id: number;
  title?: string;
  subtitle?: string;
  children?: ReactNode;
}) {
  const chapter = CHAPTERS.find((c) => c.id === id);
  const entries = byChapter(id);

  return (
    <section id={`chapter-${id}`} className="scroll-mt-20 py-16 border-t border-white/5 first:border-0 first:pt-8">
      <p className="text-xs font-mono uppercase tracking-widest text-cyan">Chapter {id}</p>
      <h2 className="mt-2 text-3xl font-bold tracking-tight">{title ?? chapter?.title}</h2>
      <p className="mt-2 text-lg text-muted">{subtitle ?? chapter?.subtitle}</p>
      {chapter?.hook && <p className="mt-1 text-sm italic text-violet/80">{chapter.hook}</p>}

      {children && <div className="mt-8 space-y-8">{children}</div>}

      {entries.length > 0 && (
        <div className="mt-10 space-y-4">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-muted">Mechanisms in this chapter</h3>
          {entries.map((e) => (
            <TradeoffCard key={e.id} entry={e} />
          ))}
        </div>
      )}
    </section>
  );
}
