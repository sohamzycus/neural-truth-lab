import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { CHAPTERS } from "../../data/chapters";
import { byChapter } from "../../data/chronology";
import { TradeoffCard } from "../ui/TradeoffCard";
import { FadeIn } from "../ui/FadeIn";
import { useApp } from "../../context/AppContext";
import { BeginnerOnly } from "../ui/ExpertOnly";

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
  const { mode } = useApp();
  const chapter = CHAPTERS.find((c) => c.id === id);
  const entries = byChapter(id);

  return (
    <motion.section
      id={`chapter-${id}`}
      className="scroll-mt-28 border-t border-theme py-16 first:border-0 first:pt-8"
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.4 }}
    >
      <FadeIn>
        <p className="text-xs font-mono uppercase tracking-widest text-[var(--color-accent)]">Chapter {id}</p>
        <h2 className="mt-2 text-3xl font-bold tracking-tight">{title ?? chapter?.title}</h2>
        <p className="mt-2 text-lg text-muted">{subtitle ?? chapter?.subtitle}</p>
        {chapter?.hook && (
          <p className="mt-1 text-sm italic text-violet">
            {mode === "beginner" ? `💡 ${chapter.hook}` : chapter.hook}
          </p>
        )}
      </FadeIn>

      {children && (
        <div className="mt-8 space-y-8">
          {children}
        </div>
      )}

      {entries.length > 0 && (
        <div className="mt-10 space-y-4">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-muted">
            {mode === "beginner" ? "What changed in this era" : "Mechanisms in this chapter"}
          </h3>
          <BeginnerOnly>
            <p className="text-sm text-muted">
              Each card: what broke → what they tried → what got cheaper → what got worse.
            </p>
          </BeginnerOnly>
          {entries.map((e, i) => (
            <FadeIn key={e.id} delay={i * 0.05}>
              <TradeoffCard entry={e} />
            </FadeIn>
          ))}
        </div>
      )}
    </motion.section>
  );
}
