export interface Chapter {
  id: number;
  slug: string;
  title: string;
  subtitle: string;
  hook: string;
}

export const CHAPTERS: Chapter[] = [
  { id: 0, slug: "opening", title: "The Question", subtitle: "Who should I listen to?", hook: "Every token asks one question." },
  { id: 1, slug: "pre-transformer", title: "Before Transformers", subtitle: "Alignment, not parallelism", hook: "Attention began as a fix for bottlenecks." },
  { id: 2, slug: "transformer", title: "The Breakthrough", subtitle: "Attention is all you need", hook: "Parallel Q/K/V changed everything." },
  { id: 3, slug: "quadratic-wall", title: "The First Wall", subtitle: "O(n²) compute", hook: "Beautiful — until 100,000 tokens." },
  { id: 4, slug: "position-wall", title: "The Second Wall", subtitle: "Position & context length", hook: "DOG BIT MAN ≠ MAN BIT DOG." },
  { id: 5, slug: "kv-wall", title: "The Third Wall", subtitle: "Decoding memory", hook: "Generate one token at a time." },
  { id: 6, slug: "long-context", title: "The Fourth Wall", subtitle: "Long-context retrieval", hook: "Context Wars begin." },
  { id: 7, slug: "recurrence", title: "Return of Recurrence", subtitle: "Linear & delta memory", hook: "Can we avoid the full matrix?" },
  { id: 8, slug: "compression", title: "Compression", subtitle: "MLA & latent KV", hook: "Compress the cache itself." },
  { id: 9, slug: "sparsity", title: "Sparsity Returns", subtitle: "Hardware-aware patterns", hook: "Which connections are worth paying for?" },
  { id: 10, slug: "future", title: "Where It's Going", subtitle: "Hybrid systems", hook: "No single winner." },
  { id: 11, slug: "lab", title: "Build Your Architecture", subtitle: "Interactive lab", hook: "Compose the compromises." },
  { id: 12, slug: "mental-model", title: "The Mental Model", subtitle: "What you should remember", hook: "Negotiated compromises." },
];

export const FAMILY_TREE = {
  root: "ATTENTION",
  branches: [
    {
      name: "POSITION",
      children: ["RoPE", "ALiBi", "YaRN", "DroPE"],
    },
    {
      name: "MEMORY",
      children: ["MQA", "GQA", "MLA", "DeltaNet"],
    },
    {
      name: "COMPUTE",
      children: ["Sparse", "Linear", "Flash", "Top-k"],
    },
  ],
};
