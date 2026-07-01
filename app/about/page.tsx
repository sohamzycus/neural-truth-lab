import type { Metadata } from "next";
import Link from "next/link";
import { SITE } from "@/lib/constants";
import { Section } from "@/components/layout/section";

export const metadata: Metadata = {
  title: "About",
  description: `About ${SITE.name} — interactive deep learning education.`,
};

const TRUTHS = [
  "Nonlinearity enables separation (Activations)",
  "Depth without activation collapses to one layer (Depth)",
  "Embeddings organize meaning in space (Embeddings)",
  "More data closes the generalization gap (Generalization)",
] as const;

const STACK = [
  "Next.js 15 · React 19 · TypeScript",
  "Tailwind CSS v4 · shadcn/ui",
  "TensorFlow.js · Framer Motion",
] as const;

export default function AboutPage(): React.ReactElement {
  return (
    <Section eyebrow="About" title={SITE.name} className="min-h-[60vh]">
      <div className="grid gap-12 lg:grid-cols-2">
        <div>
          <p className="text-lg leading-relaxed text-[var(--text-secondary)]">
            {SITE.tagline} Neural Truth Lab is a browser-only educational
            application where you discover fundamental deep learning concepts
            through live TensorFlow.js training and rich visualizations.
          </p>
          <p className="mt-4 text-[var(--text-secondary)]">
            No backend. No accounts. Everything runs locally in your browser.
            Progress and achievements persist in{" "}
            <code className="rounded bg-[var(--surface)] px-1.5 py-0.5 text-sm">
              localStorage
            </code>
            .
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/labs"
              className="rounded-lg bg-[var(--accent-primary)] px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent-primary)]"
            >
              Start experimenting
            </Link>
            <a
              href="https://github.com/sohamzycus/neural-truth-lab"
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg border border-[var(--border)] px-4 py-2 text-sm text-[var(--text-secondary)] transition-colors hover:border-[var(--accent-primary)] hover:text-[var(--text-primary)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent-primary)]"
            >
              View on GitHub
            </a>
          </div>
        </div>
        <div className="space-y-6">
          <div className="glass-panel p-8">
            <h3 className="text-sm font-medium uppercase tracking-wider text-[var(--text-muted)]">
              Four truths
            </h3>
            <ul className="mt-4 space-y-3">
              {TRUTHS.map((truth) => (
                <li
                  key={truth}
                  className="flex items-start gap-3 text-[var(--text-secondary)]"
                >
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--accent-primary)]" />
                  {truth}
                </li>
              ))}
            </ul>
          </div>
          <div className="glass-panel p-8">
            <h3 className="text-sm font-medium uppercase tracking-wider text-[var(--text-muted)]">
              Tech stack
            </h3>
            <ul className="mt-4 space-y-2">
              {STACK.map((item) => (
                <li key={item} className="text-sm text-[var(--text-secondary)]">
                  {item}
                </li>
              ))}
            </ul>
            <p className="mt-4 text-sm text-[var(--text-muted)]">
              See{" "}
              <code className="rounded bg-[var(--surface)] px-1 py-0.5 text-xs">
                docs/ARCHITECTURE.md
              </code>{" "}
              and{" "}
              <code className="rounded bg-[var(--surface)] px-1 py-0.5 text-xs">
                specs/
              </code>{" "}
              in the repository.
            </p>
          </div>
        </div>
      </div>
      <p className="mt-16 text-center text-sm text-[var(--text-muted)]">
        Built for learners who want to see neural networks think, not just read
        about them.
      </p>
    </Section>
  );
}
