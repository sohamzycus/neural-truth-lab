import type { TokenCategory } from "@/datasets/synthetic-language";

interface SimilarityCardProps {
  token: string;
  category: TokenCategory;
  neighbors: { token: string; similarity: number }[];
}

const CATEGORY_LABEL: Record<TokenCategory, string> = {
  animal: "Animal",
  fruit: "Fruit",
  verb: "Verb",
  other: "Other",
};

export function SimilarityCard({
  token,
  category,
  neighbors,
}: SimilarityCardProps): React.ReactElement {
  return (
    <div className="glass-panel p-4">
      <p className="text-xs uppercase tracking-wider text-[var(--text-muted)]">
        Nearest neighbors
      </p>
      <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">
        {token}
      </p>
      <p className="text-sm text-[var(--lab-embeddings)]">
        {CATEGORY_LABEL[category]}
      </p>
      <ul className="mt-4 space-y-2">
        {neighbors.map((n) => (
          <li
            key={n.token}
            className="flex items-center justify-between font-mono text-sm text-[var(--text-secondary)]"
          >
            <span>{n.token}</span>
            <span>{n.similarity.toFixed(2)}</span>
          </li>
        ))}
      </ul>
      <p className="mt-3 text-[10px] text-[var(--text-muted)]">
        Cosine similarity
      </p>
    </div>
  );
}
