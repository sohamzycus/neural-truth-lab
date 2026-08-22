export interface Chapter {
  id: number;
  slug: string;
  title: string;
  navLabel: string;
  subtitle: string;
  hook: string;
}

export const CHAPTERS: Chapter[] = [
  { id: 0, slug: "opening", title: "The Question", navLabel: "Opening", subtitle: "Who should I listen to?", hook: "Every token asks one question." },
  { id: 1, slug: "pre-transformer", title: "Before Transformers", navLabel: "Pre-TFM", subtitle: "Alignment, not parallelism", hook: "Attention began as a fix for bottlenecks." },
  { id: 2, slug: "transformer", title: "The Breakthrough", navLabel: "Transformer", subtitle: "Attention is all you need", hook: "Parallel Q/K/V changed everything." },
  { id: 3, slug: "quadratic-wall", title: "The First Wall", navLabel: "O(n²)", subtitle: "O(n²) compute", hook: "Beautiful — until 100,000 tokens." },
  { id: 4, slug: "position-wall", title: "The Second Wall", navLabel: "Position", subtitle: "Position & context length", hook: "DOG BIT MAN ≠ MAN BIT DOG." },
  { id: 5, slug: "kv-wall", title: "The Third Wall", navLabel: "KV cache", subtitle: "Decoding memory", hook: "Generate one token at a time." },
  { id: 6, slug: "long-context", title: "The Fourth Wall", navLabel: "Long ctx", subtitle: "Long-context retrieval", hook: "Context Wars begin." },
  { id: 7, slug: "recurrence", title: "Return of Recurrence", navLabel: "Recurrent", subtitle: "Linear & delta memory", hook: "Can we avoid the full matrix?" },
  { id: 8, slug: "compression", title: "Compression", navLabel: "MLA", subtitle: "MLA & latent KV", hook: "Compress the cache itself." },
  { id: 9, slug: "sparsity", title: "Sparsity Returns", navLabel: "Sparse", subtitle: "Hardware-aware patterns", hook: "Which connections are worth paying for?" },
  { id: 10, slug: "future", title: "Where It's Going", navLabel: "Hybrid", subtitle: "Hybrid systems", hook: "No single winner." },
  { id: 11, slug: "lab", title: "Build Your Architecture", navLabel: "Lab", subtitle: "Interactive lab", hook: "Compose the compromises." },
  { id: 12, slug: "mental-model", title: "The Mental Model", navLabel: "Summary", subtitle: "What you should remember", hook: "Negotiated compromises." },
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
      children: ["MQA", "GQA", "MLA", "Sinks", "DeltaNet"],
    },
    {
      name: "COMPUTE",
      children: ["Sparse", "Sliding Window", "Top-k", "DSA/CSA", "Flash"],
    },
  ],
};
