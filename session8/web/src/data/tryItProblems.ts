export interface TryItProblem {
  id: string;
  title: string;
  description: string;
  options: {
    attention: string[];
    position: string[];
    kv: string[];
    kernel: string[];
  };
  answer: {
    attention: string;
    position: string;
    kv: string;
    kernel: string;
  };
  rationale: string;
  pitfalls: string;
}

export const TRY_IT_PROBLEMS: TryItProblem[] = [
  {
    id: "chat-2k",
    title: "2K Chatbot",
    description: "Short turns, millions of users, latency-sensitive.",
    options: {
      attention: ["Dense", "Sliding Window", "Sparse / Linear", "Top-k only"],
      position: ["RoPE", "ALiBi", "Learned absolute", "No position"],
      kv: ["GQA", "MHA", "MLA", "MQA"],
      kernel: ["FlashAttention", "Standard matmul", "Reformer LSH", "Linear kernel"],
    },
    answer: { attention: "Dense", position: "RoPE", kv: "GQA", kernel: "FlashAttention" },
    rationale: "At 2K, dense O(n²) is cheap. GQA shrinks KV for throughput. FlashAttention makes dense practical on GPU.",
    pitfalls: "MQA may hurt quality; sparse/linear adds complexity for little gain at short context.",
  },
  {
    id: "doc-128k",
    title: "128K Document Analyst",
    description: "Full document in context; cross-section retrieval matters.",
    options: {
      attention: ["Dense only", "Sliding Window + Global", "MQA-only decode", "Pure linear"],
      position: ["RoPE + YaRN", "RoPE only", "ALiBi", "Sinusoidal"],
      kv: ["GQA", "MHA", "No KV cache", "MLA"],
      kernel: ["FlashAttention", "Standard", "CPU fallback", "Sparse kernel only"],
    },
    answer: { attention: "Sliding Window + Global", position: "RoPE + YaRN", kv: "GQA", kernel: "FlashAttention" },
    rationale: "Need YaRN for length, hybrid sparse-global for docs, Flash for IO, GQA for decode memory.",
    pitfalls: "Pure dense 128K without Flash + KV planning is memory-prohibitive.",
  },
  {
    id: "agent-1m",
    title: "1M-Token Agent",
    description: "Tool logs, memory streams, multi-hour sessions.",
    options: {
      attention: ["Dense", "Sparse / Linear hybrid", "Sliding window only", "Full MHA dense"],
      position: ["RoPE + YaRN", "Learned positions", "No position", "ALiBi only"],
      kv: ["MLA", "MHA", "GQA", "No cache"],
      kernel: ["FlashAttention", "Standard", "Reformer", "None"],
    },
    answer: { attention: "Sparse / Linear hybrid", position: "RoPE + YaRN", kv: "MLA", kernel: "FlashAttention" },
    rationale: "1M dense is infeasible. MLA compresses KV; hybrid sparsity/recurrence handles state.",
    pitfalls: "Naïve dense at 1M ≈ 1T interactions — no single trick suffices.",
  },
  {
    id: "streaming-voice",
    title: "Streaming Voice Assistant",
    description: "Infinite stream, bounded memory, low latency.",
    options: {
      attention: ["Sliding Window", "Dense full history", "Sparse random", "Linear only"],
      position: ["RoPE", "ALiBi", "Learned", "DroPE-only"],
      kv: ["GQA + Attention Sinks", "MHA", "MLA only", "No sinks"],
      kernel: ["FlashAttention", "Standard", "CPU", "Sparse only"],
    },
    answer: { attention: "Sliding Window", position: "RoPE", kv: "GQA + Attention Sinks", kernel: "FlashAttention" },
    rationale: "StreamingLLM sinks stabilize sliding-window KV; GQA keeps cache small.",
    pitfalls: "Evicting sink tokens causes catastrophic quality drops.",
  },
  {
    id: "inference-server",
    title: "High-Concurrency Inference Server",
    description: "Thousands of parallel requests; KV RAM is the bottleneck.",
    options: {
      attention: ["Dense", "Linear", "Sparse training-only", "Sliding + global"],
      position: ["RoPE", "Sinusoidal", "ALiBi", "None"],
      kv: ["GQA or MQA", "MHA", "MLA", "Full-rank only"],
      kernel: ["FlashAttention", "Standard", "Custom CPU", "None"],
    },
    answer: { attention: "Dense", position: "RoPE", kv: "GQA or MQA", kernel: "FlashAttention" },
    rationale: "KV size limits batch size — GQA/MQA trade a little quality for much more capacity.",
    pitfalls: "MHA maximizes quality but crushes throughput on memory-bound servers.",
  },
  {
    id: "long-video",
    title: "Long-Video Model",
    description: "Hours of frame tokens; extreme sequence length.",
    options: {
      attention: ["Dense", "Sparse (window + global)", "MQA decode", "Full attention"],
      position: ["RoPE", "Learned", "None", "ALiBi"],
      kv: ["MLA", "MHA", "GQA", "Uncompressed"],
      kernel: ["FlashAttention", "Standard", "None", "CPU"],
    },
    answer: { attention: "Sparse (window + global)", position: "RoPE", kv: "MLA", kernel: "FlashAttention" },
    rationale: "Combine sparsity, MLA compression, and IO optimization — dense video tokens are impossible.",
    pitfalls: "Dense attention on full video token counts does not fit on any real hardware.",
  },
];
