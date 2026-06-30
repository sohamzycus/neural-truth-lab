import type { Metadata } from "next";
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
          </p>
        </div>
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
      </div>
    </Section>
  );
}
