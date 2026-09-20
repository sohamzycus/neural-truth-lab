# Session 12 — 32 Virtual GPU ZeRO Training Simulator

## Objective

Build a **CPU-executable distributed-training simulator** with **32 virtual GPUs** and compare:

| Strategy | Parameters | Gradients | Optimizer state |
|----------|------------|-----------|-----------------|
| A. Baseline data parallelism | Replicated | Replicated | Replicated |
| B. ZeRO Stage 1 | Replicated | Replicated | Sharded |
| C. ZeRO Stage 2 | Replicated | Sharded | Sharded |
| D. ZeRO Stage 3 | Sharded | Sharded | Sharded |

The simulator must demonstrate **conceptual behavior**: ownership maps, memory accounting, collectives, compute vs communication, and topology — not real GPU timings.

## Non-goals

This is **not**:

- A replacement for DeepSpeed or PyTorch FSDP
- A real 32-GPU cluster
- A benchmark claiming measured NVIDIA performance
- A pretense that CPU threads are physical GPUs

It is a **controlled educational laboratory** with explicitly labeled simulation assumptions.

## Virtual GPU topology (default)

- `WORLD_SIZE = 32`
- `GPUS_PER_NODE = 8`, `NUM_NODES = 4`
- Node `k` → ranks `[8k .. 8k+7]`
- Configurable intra-node vs inter-node bandwidth and latency (illustrative only)

## Demo model

Small deterministic transformer-like stack (`DemoModel`): embedding, `NUM_LAYERS` linear blocks, output projection. Memory is modeled **mathematically** from `PARAMETER_COUNT`; forward/backward use **small real tensors** for structure.

## Memory model

Per-GPU `MemoryAccounting` with traceable formulas for parameters, gradients, FP32 master weights (when applicable), Adam state (m, v), activations, communication buffers, temporaries, and peak memory.

## Communication model

Explicit `all_reduce`, `reduce_scatter`, `all_gather` returning bytes moved, participating ranks, simulated time, intra-node vs inter-node bytes. All bandwidth values labeled **simulation assumption**.

## Compute model

`compute_work` (abstract units) is separate from `simulated_compute_time` (derived from a configurable factor). CPU wall time is **not** presented as GPU time.

## Experiments (minimum)

1. Baseline DP  
2. ZeRO-1  
3. ZeRO-2  
4. ZeRO-3  
5. 32 GPUs single-node comm assumption  
6. 32 GPUs multi-node comm assumption  
7. ZeRO-3 bucket size sweep  
8. Model size sweep  

## Evidence chain

Concept → implementation (`src/`) → experiment (`experiments.py`) → measured output (`outputs/`, notebook) → student reflection cells (**not** AI-filled).

## Acceptance

- 32 distinct `VirtualGPU` objects participate in each strategy run
- Ownership maps enforce sharding invariants (tests in `tests/`)
- Notebook plots read simulator output only
- README + notebook include evidence-linked reflections
