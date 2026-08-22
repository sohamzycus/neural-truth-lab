export interface Scenario {
  id: string;
  title: string;
  description: string;
  choices: {
    attention: string;
    position: string;
    kv: string;
    kernel: string;
  };
  rationale: string;
  pitfalls: string;
}

export const SCENARIOS: Scenario[] = [
  {
    id: "chat-2k",
    title: "2K Chatbot",
    description: "Short conversational turns, latency-sensitive, millions of users.",
    choices: { attention: "Dense", position: "RoPE", kv: "GQA", kernel: "FlashAttention" },
    rationale: "Short context keeps O(n²) cheap. GQA shrinks KV cache for throughput. FlashAttention makes dense attention practical on GPU.",
    pitfalls: "MQA might sacrifice too much quality; sparse attention adds complexity for little gain at 2K.",
  },
  {
    id: "doc-128k",
    title: "128K Document Analyst",
    description: "Full document in context, retrieval across sections, quality matters.",
    choices: { attention: "Sliding Window + Global", position: "RoPE + YaRN", kv: "GQA", kernel: "FlashAttention" },
    rationale: "Need context extension (YaRN) and efficient IO (Flash). Hybrid sparse-global patterns help very long docs.",
    pitfalls: "Pure dense 128K is memory-prohibitive without Flash + careful KV management.",
  },
  {
    id: "agent-1m",
    title: "1M-Token Agent",
    description: "Agent with massive tool logs, memory streams, multi-hour sessions.",
    choices: { attention: "Sparse / Linear hybrid", position: "RoPE + YaRN", kv: "MLA", kernel: "FlashAttention" },
    rationale: "At 1M tokens, quadratic dense is infeasible. MLA compresses KV; linear/recurrent layers handle state; sparsity selects connections.",
    pitfalls: "Naïve dense attention at 1M = ~1T interactions. No single trick suffices.",
  },
  {
    id: "coding-realtime",
    title: "Realtime Coding Assistant",
    description: "Low latency per token, moderate context, single user.",
    choices: { attention: "Dense", position: "RoPE", kv: "GQA", kernel: "FlashAttention" },
    rationale: "Moderate context, decode latency dominated by KV bandwidth — GQA helps. Flash for efficient attention.",
    pitfalls: "MLA adds complexity; linear attention changes retrieval behavior for code precision.",
  },
  {
    id: "inference-server",
    title: "High-Concurrency Inference Server",
    description: "Thousands of parallel requests, KV memory is the bottleneck.",
    choices: { attention: "Dense", position: "RoPE", kv: "GQA or MQA", kernel: "FlashAttention" },
    rationale: "KV cache size directly limits batch size. GQA/MQA trade quality for capacity.",
    pitfalls: "MHA maximizes quality but halves throughput on memory-bound servers.",
  },
  {
    id: "streaming-voice",
    title: "Streaming Voice Assistant",
    description: "Infinite conversation stream, bounded memory, low latency.",
    choices: { attention: "Sliding Window", position: "RoPE", kv: "GQA + Attention Sinks", kernel: "FlashAttention" },
    rationale: "StreamingLLM sinks stabilize sliding-window KV. GQA keeps cache small.",
    pitfalls: "Evicting sink tokens causes catastrophic quality drops.",
  },
  {
    id: "long-video",
    title: "Long-Video Model",
    description: "Hours of frames as tokens, extreme sequence length.",
    choices: { attention: "Sparse (window + global)", position: "RoPE", kv: "MLA", kernel: "FlashAttention" },
    rationale: "Must combine sparsity, compression, and IO optimization. Local windows for frames, global tokens for scene anchors.",
    pitfalls: "Dense attention on video token counts is computationally impossible.",
  },
  {
    id: "retrieval-agent",
    title: "Retrieval-Heavy Agent",
    description: "RAG with many retrieved chunks, needs precise attention to relevant passages.",
    choices: { attention: "Dense (on retrieved subset)", position: "RoPE", kv: "GQA", kernel: "FlashAttention" },
    rationale: "Retrieval reduces effective n. Dense attention on relevant chunks preserves precision.",
    pitfalls: "Linear attention may miss exact retrieval matches critical for factual agents.",
  },
];
