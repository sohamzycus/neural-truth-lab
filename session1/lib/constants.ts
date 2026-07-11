export const LABS = [
  {
    id: "activations",
    slug: "activations",
    number: 1,
    title: "Activations",
    headline: "Activations Exist for a Reason",
    description: "Without nonlinearity, a network cannot separate concentric rings.",
    href: "/lab/activations",
    accent: "var(--lab-activations)",
    accentClass: "text-[var(--lab-activations)]",
    borderClass: "border-l-[var(--lab-activations)]",
  },
  {
    id: "depth",
    slug: "depth",
    number: 2,
    title: "Depth",
    headline: "Depth Without Nonlinearity",
    description: "Five linear layers collapse into one. Depth needs activation.",
    href: "/lab/depth",
    accent: "var(--lab-depth)",
    accentClass: "text-[var(--lab-depth)]",
    borderClass: "border-l-[var(--lab-depth)]",
  },
  {
    id: "embeddings",
    slug: "embeddings",
    number: 3,
    title: "Embeddings",
    headline: "Embedding Universe",
    description: "Words used in similar contexts end up close together in space.",
    href: "/lab/embeddings",
    accent: "var(--lab-embeddings)",
    accentClass: "text-[var(--lab-embeddings)]",
    borderClass: "border-l-[var(--lab-embeddings)]",
  },
  {
    id: "generalization",
    slug: "generalization",
    number: 4,
    title: "Generalization",
    headline: "Generalization Arena",
    description: "More data closes the gap between memorization and true learning.",
    href: "/lab/generalization",
    accent: "var(--lab-generalization)",
    accentClass: "text-[var(--lab-generalization)]",
    borderClass: "border-l-[var(--lab-generalization)]",
  },
] as const;

export type LabId = (typeof LABS)[number]["id"];

export const SITE = {
  name: "Neural Truth Lab",
  tagline: "Experience Deep Learning. Don't Just Read About It.",
  shortTagline: "Experience Deep Learning",
} as const;
