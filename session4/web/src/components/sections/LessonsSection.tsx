import type { Lesson } from "../../types";
import { Section } from "../shell/AppShell";

export function LessonsSection({ lessons }: { lessons: Lesson[] }) {
  return (
    <Section
      id="lessons"
      eyebrow="Principles"
      title="Lessons Learned"
      subtitle="What we take forward when engineering community bird text for foundation-model training."
    >
      <div className="space-y-3">
        {lessons.map((l, i) => (
          <article key={l.id} className="panel p-5">
            <div className="flex gap-4">
              <span className="font-mono text-sm text-[var(--color-accent)]">{String(i + 1).padStart(2, "0")}</span>
              <div>
                <h3 className="font-medium">{l.title}</h3>
                <p className="mt-2 text-sm text-[var(--color-muted)]">{l.body}</p>
              </div>
            </div>
          </article>
        ))}
      </div>
    </Section>
  );
}
