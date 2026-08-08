# Session 6 — Training Data Execution System

A miniature production-grade **Training Data Operating System** that models the full lifecycle of LLM training data: from raw documents through tokenization, sharding, curriculum scheduling, OPUS admission control, packing, fake training, ledger-based consumption tracking, checkpoint/resume, replay verification, fork/branch, and audit.

> This is not a data loader. This is an event-sourced training data OS.

## Unique Differentiators

This is **not a DataLoader**. The table below contrasts what reviewers typically see in an assignment vs what this system implements.

| | Typical `DataLoader` | Training Data OS (this project) |
|---|---|---|
| **Data model** | Mutable files on disk | Immutable, content-addressed artifacts (SHA-256) |
| **History** | Overwritten silently | Append-only ledgers — never mutate past events |
| **Admission** | Take everything | OPUS scores every shard — Accept / Reject / Deferred / Protected Override |
| **Eval leakage** | Often ignored | Eval firewall — held-out shards blocked from loss-bearing batches |
| **Crash recovery** | Restart from scratch | Checkpoint + resume — no skipped or duplicated batches |
| **Reproducibility** | Re-run and hope | Replay reads ledger, recomputes hashes, proves identity |
| **Experimentation** | Change code, lose trace | Fork from checkpoint — independent branch + independent ledger |
| **Debugging** | Print statements | Time Machine — inspect full state at any ledger offset |

### vs. a typical assignment

```mermaid
flowchart LR
    subgraph TYPICAL["❌ Typical Assignment / DataLoader"]
        T1[Read files]
        T2[Tokenize]
        T3[Yield batches]
        T4[Train]
        T1 --> T2 --> T3 --> T4
    end

    subgraph THIS["✅ Training Data OS — this project"]
        direction TB
        D1["Immutable artifacts<br/>every stage hashed"]
        D2["Event-sourced ledgers<br/>append-only, never mutate"]
        D3["OPUS admission gate<br/>no random accept"]
        D4["Eval firewall<br/>held-out never in loss"]
        D5["Crash → Resume → Replay<br/>identical hashes proven"]
        D6["Fork branches<br/>independent ledgers"]
        D7["Time Machine<br/>debug any ledger offset"]
        D1 --> D2 --> D3 --> D4 --> D5 --> D6 --> D7
    end

    TYPICAL -.->|"not comparable"| THIS
```

![DataLoader vs Training Data OS](assets/differentiators.png)

### The five things no assignment does

| # | Differentiator | Why it matters |
|---|----------------|----------------|
| 1 | **Immutable event log** | Every training decision is auditable months later |
| 2 | **OPUS + protected floors** | Low-resource lanes (e.g. Indic) cannot be starved by the scheduler |
| 3 | **Eval firewall** | Benchmark contamination is a real production failure mode |
| 4 | **Hash-verified replay** | Prove re-runs are identical without trusting the trainer |
| 5 | **Time Machine** | Debug "what was the model eating at step N?" without re-running |

## Quick Start

```bash
cd session6/project
python3 run_demo.py
```

**Push to GitHub** (if port 22 is blocked on your network):

```bash
# from repo root
bash scripts/push.sh
```

See [`session6/PUSH.md`](PUSH.md) for all push methods.

Time machine (debugger for training state at ledger offset N):

```bash
python3 run_demo.py --time-machine 45
```

Run tests:

```bash
python3 -m pytest tests/ -v
# or
python3 -m unittest discover -s tests -v
```

## Architecture

> Diagrams use [Mermaid](https://mermaid.js.org/) — they render natively on GitHub, GitLab, and Cursor.  
> Source: [`assets/*.mmd`](assets/). PNG/SVG exports: `bash scripts/render_diagrams.sh` (uses `npx @mermaid-js/mermaid-cli`)

### System overview

```mermaid
flowchart TB
    subgraph INGEST["① Ingestion Layer — immutable from first byte"]
        DOC[("📄 Documents")]
        TOK["🔒 Frozen Tokenizer<br/>SHA-256 verified"]
        SHARD["📦 Tokenized Shards<br/>content_hash · lane · stage"]
        MAN["📋 Manifests<br/>manifest_hash"]
    end

    subgraph SCHEDULE["② Scheduling Layer — what to train, when"]
        CURR["📅 Curriculum Engine<br/>Stage → Lane → Weight → Floor"]
        OPUS["⚖️ OPUS Admission<br/>quality · novelty · difficulty"]
        MIX["🎯 Mixture Compiler<br/>planned vs actual"]
    end

    subgraph EXECUTE["③ Execution Layer — batches into training"]
        PACK["🧩 Packing Policies<br/>Pad · Concat · Greedy · BestFit · Struct"]
        BATCH["📊 Batches<br/>batch_hash · shard_map"]
        FIREWALL{"🛡️ Eval Firewall"}
        TRAIN["🧠 Tiny Trainer<br/>Embedding + MLP"]
    end

    subgraph PERSIST["④ Persistence Layer — never overwrite history"]
        CONS[("📒 Consumption Ledger<br/>append-only JSONL")]
        LEARN[("📗 Learning Ledger<br/>loss · perplexity · OPUS")]
        CKPT[("💾 Checkpoints<br/>model · RNG · offset")]
        STORE[("🗄️ Immutable Store<br/>content-addressed SHA-256")]
    end

    subgraph RESILIENCE["⑤ Resilience Layer — production survival"]
        CRASH["💥 Crash @ batch 17"]
        RESUME["▶️ Resume<br/>no skip · no duplicate"]
        REPLAY["🔁 Replay<br/>recompute hashes · verify"]
        FORK["🌿 Fork<br/>new branch · new ledger"]
    end

    subgraph OBSERVE["⑥ Observability Layer"]
        TM["⏱️ Time Machine<br/>--time-machine N"]
        AUDIT["✅ Audit Engine"]
        EVID["📑 Evidence Bundle<br/>run.log · evidence.json"]
    end

    DOC --> TOK --> SHARD --> MAN
    MAN --> CURR --> OPUS --> MIX
    MIX --> PACK --> BATCH
    BATCH --> FIREWALL
    FIREWALL -->|"eval shard"| BLOCK["❌ eval_shard_blocked"]
    FIREWALL -->|"training shard"| TRAIN
    TRAIN --> CONS & LEARN
    TRAIN --> CKPT
    SHARD & MAN & BATCH & CKPT --> STORE
    CKPT --> CRASH --> RESUME --> REPLAY
    CKPT --> FORK
    CONS & LEARN & CKPT --> TM
    CONS & LEARN & REPLAY & FORK --> AUDIT --> EVID
```

![System architecture — 6 layers](assets/architecture.png)

Every artifact is **immutable** and **content-addressed** (SHA-256). Every decision is **logged**. Every replay **recomputes hashes** and verifies identity — it never regenerates batches.

### Design Philosophy

| Principle | Implementation |
|-----------|----------------|
| Immutability | Append-only ledgers, write-once artifact store |
| Determinism | Fixed seeds, LCG RNG, frozen tokenizer |
| Traceability | Consumption + learning ledgers with hashes |
| Reproducibility | Replay engine reconstructs from ledger |
| Extensibility | Pluggable packing policies, curriculum stages |

### Folder Structure

```
project/
├── core/                    # Engine modules
│   ├── tokenizer_engine.py  # Frozen tokenizer
│   ├── shard_engine.py      # Immutable tokenized shards
│   ├── manifest_engine.py   # Shard aggregation manifests
│   ├── curriculum_engine.py # Timeline mixture compiler
│   ├── opus_engine.py       # Quality admission control
│   ├── packing_engine.py    # 5 pluggable packing policies
│   ├── batch_engine.py      # Batch construction + eval firewall
│   ├── trainer_engine.py    # Fake training orchestration
│   ├── checkpoint_engine.py # Immutable checkpoints
│   ├── replay_engine.py     # Ledger-based replay verification
│   ├── fork_engine.py       # Branch from checkpoint
│   ├── audit_engine.py      # Full execution audit
│   └── metrics_engine.py    # Performance reporting
├── ledger/                  # Event-sourced ledgers
│   ├── event_store.py       # JSONL append-only events
│   ├── consumption_ledger.py
│   └── learning_ledger.py
├── models/
│   └── tiny_model.py        # Embedding + MLP (no torch)
├── storage/
│   ├── immutable_store.py   # Content-addressed artifacts
│   └── hash_utils.py        # SHA-256 utilities
├── submission_artifacts/    # Generated evidence bundle
├── run_demo.py              # Full pipeline entry point
└── tests/                   # Automated test suite
```

## Execution Flow

1. **Tokenizer** — Build vocabulary from documents, freeze, verify hash
2. **Shards** — Tokenize documents into immutable shards with full metadata
3. **Manifests** — Aggregate shards into hash-verified manifests
4. **Curriculum** — Compile stage-based mixture (planned vs actual)
5. **OPUS** — Score every candidate (quality, novelty, difficulty); record decisions
6. **Eval Firewall** — Block evaluation shards from loss-bearing batches
7. **Packing** — Greedy packing (switchable to 4 other policies)
8. **Training** — Forward/loss on tiny model; record to both ledgers
9. **Crash** — Simulated crash after batch 17
10. **Resume** — Restore from checkpoint; continue without duplicates
11. **Replay** — Reconstruct batches from ledger; verify hash identity
12. **Fork** — Branch from checkpoint with different packing policy
13. **Audit** — Verify all invariants; generate evidence bundle

## Deep Dives

### Git + Kafka + Event Sourcing

The design borrows three production patterns and applies them to training data:

```mermaid
flowchart TB
    subgraph GIT["Git mental model"]
        G1["Documents = commits"]
        G2["Shards = blobs"]
        G3["Manifests = trees"]
        G4["Checkpoints = tags"]
        G5["Fork = branch"]
    end

    subgraph KAFKA["Kafka mental model"]
        K1["Consumption events = topic A"]
        K2["Learning events = topic B"]
        K3["Monotonic offset per event"]
        K4["Replay = consumer rewind"]
    end

    subgraph ES["Event Sourcing mental model"]
        E1["State = fold over events"]
        E2["Ledgers = source of truth"]
        E3["Batches reconstructed, not regenerated"]
        E4["Audit = verify event chain"]
    end

    GIT --- KAFKA --- ES

    subgraph RESULT["Combined in this system"]
        R1["Write once · hash everything"]
        R2["Append only · never overwrite"]
        R3["Replay recomputes · must match"]
        R4["Fork copies checkpoint · new ledger stream"]
    end

    GIT --> RESULT
    KAFKA --> RESULT
    ES --> RESULT
```

### Time Machine — debugger for training data

```mermaid
flowchart LR
    subgraph LEDGER["Consumption + Learning Ledgers"]
        E0["offset 0"]
        E1["offset 1"]
        E2["offset …"]
        EN["offset N"]
        E0 --> E1 --> E2 --> EN
    end

    TM["⏱️ Time Machine<br/>python run_demo.py --time-machine N"]

    EN --> TM

    subgraph SNAPSHOT["State at offset N"]
        S1["Current batch"]
        S2["Current checkpoint"]
        S3["Curriculum stage + mixture"]
        S4["OPUS decision"]
        S5["Loss + perplexity"]
        S6["Ledger event count"]
    end

    TM --> SNAPSHOT
```

```bash
python3 run_demo.py --time-machine 45
# → current batch, checkpoint, curriculum, OPUS decision, loss, perplexity
```

### Crash → Resume → Replay

```mermaid
sequenceDiagram
    participant T as Trainer
    participant L as Ledgers
    participant C as Checkpoint
    participant X as Crash
    participant R as Resume
    participant P as Replay

    T->>L: append consumption + learning events
    T->>C: save checkpoint every 5 batches
    loop batches 1–17
        T->>L: record batch hash + loss
    end
    T->>C: save checkpoint at batch 17
    T->>X: 💥 simulated crash
    Note over X: process dies — state only in C + L

    R->>C: load model · RNG · ledger offset
    R->>T: resume from batch 18
    loop batches 18–25
        T->>L: append (no duplicates)
    end

    P->>L: read all events
    P->>P: recompute batch hashes
    Note over P: ✅ replay_hash_matched
```

### OPUS, Eval Firewall, Packing

- **OPUS** — Every shard scored on quality, novelty, difficulty. Decisions: Accept, Reject, Deferred, Protected Override. No random acceptance.
- **Eval Firewall** — Evaluation shards blocked from loss-bearing batches (`eval_shard_blocked`).
- **Packing** — Five switchable policies: `PadOnly`, `Concatenate`, `Greedy`, `BestFit`, `StructurePreserving`.

## Deterministic Execution

- Frozen tokenizer with verified SHA-256 hash
- LCG pseudo-random number generator (no `random` module)
- Content-addressed artifacts in immutable store
- Replay recomputes batch hashes without regeneration

## Submission Artifacts

After `run_demo.py`, find in `submission_artifacts/`:

| File | Description |
|------|-------------|
| `run.log` | PASS/FAIL log for every check |
| `evidence.json` | Machine-readable evidence bundle |
| `evidence.md` | Human-readable evidence report |
| `performance.json` | Packing %, tokens/sec, timing metrics |
| `ledgers/` | Consumption + learning JSONL |
| `checkpoints/` | Training checkpoints |
| `manifests/` | Shard manifests |

### Diagram source files

| Diagram | Mermaid source |
|---------|----------------|
| System architecture (6 layers) | [`assets/architecture.mmd`](assets/architecture.mmd) |
| vs. typical assignment | [`assets/differentiators.mmd`](assets/differentiators.mmd) |
| Git + Kafka + event sourcing | [`assets/event-sourcing.mmd`](assets/event-sourcing.mmd) |
| Time Machine | [`assets/time-machine.mmd`](assets/time-machine.mmd) |
| Crash / resume / replay | [`assets/resilience.mmd`](assets/resilience.mmd) |
