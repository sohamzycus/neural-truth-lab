import { useEffect, useMemo, useState, type ReactNode } from "react";
import { Bird } from "lucide-react";
import { motion } from "framer-motion";

const NAV = [
  { id: "hero", label: "Overview" },
  { id: "why-notes", label: "Why notes" },
  { id: "dataset", label: "Dataset" },
  { id: "raw", label: "Raw noise" },
  { id: "strategies", label: "Cleaning" },
  { id: "domain", label: "Bird domain" },
  { id: "surgery", label: "Surgery" },
  { id: "compare", label: "Compare" },
  { id: "discoveries", label: "Discoveries" },
  { id: "stats", label: "Stats" },
  { id: "roadmap", label: "Roadmap" },
  { id: "lessons", label: "Lessons" },
];

export function ProgressBar({ progress }: { progress: number }) {
  return (
    <div className="h-[2px] w-full bg-white/[0.04]">
      <div
        className="h-full bg-gradient-to-r from-[var(--color-accent)] to-[var(--color-accent-sky)] transition-[width] duration-150 ease-out"
        style={{ width: `${Math.min(100, Math.max(0, progress * 100))}%` }}
      />
    </div>
  );
}

export function SectionNav({ activeId }: { activeId: string }) {
  return (
    <nav className="hidden gap-1 overflow-x-auto lg:flex">
      {NAV.map((item) => (
        <a
          key={item.id}
          href={`#${item.id}`}
          className={`whitespace-nowrap rounded-md px-2.5 py-1 text-xs transition ${
            activeId === item.id
              ? "bg-[var(--color-accent)]/15 text-[var(--color-accent)]"
              : "text-[var(--color-muted)] hover:text-[var(--color-text)]"
          }`}
        >
          {item.label}
        </a>
      ))}
    </nav>
  );
}

export function Section({
  id,
  eyebrow,
  title,
  subtitle,
  children,
}: {
  id: string;
  eyebrow?: string;
  title: string;
  subtitle?: string;
  children: ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-24 px-4 py-20 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        {eyebrow ? (
          <div className="mb-3 font-mono text-[11px] uppercase tracking-[0.2em] text-[var(--color-accent)]">
            {eyebrow}
          </div>
        ) : null}
        <h2 className="text-3xl font-semibold tracking-tight text-[var(--color-text)] sm:text-4xl">{title}</h2>
        {subtitle ? <p className="measure mt-3 text-[var(--color-muted)]">{subtitle}</p> : null}
        <div className="mt-10">{children}</div>
      </div>
    </section>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const [progress, setProgress] = useState(0);
  const [activeId, setActiveId] = useState("hero");
  const ids = useMemo(() => NAV.map((n) => n.id), []);

  useEffect(() => {
    const onScroll = () => {
      const doc = document.documentElement;
      const max = doc.scrollHeight - doc.clientHeight;
      setProgress(max > 0 ? window.scrollY / max : 0);

      let current = ids[0];
      for (const id of ids) {
        const el = document.getElementById(id);
        if (!el) continue;
        if (el.getBoundingClientRect().top <= 120) current = id;
      }
      setActiveId(current);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [ids]);

  return (
    <div className="min-h-screen text-[var(--color-text)]">
      <header className="sticky top-0 z-40 border-b border-[var(--color-border)] bg-[var(--color-bg)]/85 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
          <a href="#hero" className="flex items-center gap-2">
            <Bird className="h-4 w-4 text-[var(--color-accent)]" />
            <span className="text-sm font-semibold tracking-tight">Ataavi</span>
            <span className="text-sm text-[var(--color-muted)]">/</span>
            <span className="text-sm text-[var(--color-muted)]">Corpus Forge</span>
          </a>
          <SectionNav activeId={activeId} />
        </div>
        <ProgressBar progress={progress} />
      </header>
      <motion.main initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4 }}>
        {children}
      </motion.main>
      <footer className="border-t border-[var(--color-border)] px-4 py-10 text-center text-sm text-[var(--color-muted)]">
        Ataavi Corpus Forge · Bird knowledge engineering for multimodal AI
      </footer>
    </div>
  );
}

export { NAV };
