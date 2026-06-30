# Lab 3 — Embedding Universe

**Route:** `/lab/embeddings`  
**Lab ID:** `embeddings`  
**Accent:** Purple `#a855f7`

---

## Claim

> Words that appear in similar contexts end up close together in embedding space.

---

## Theory (Visual Chips)

1. **Embeddings** map discrete tokens to continuous vectors.
2. **Training** pulls similar contexts together (distributional hypothesis).
3. **Projection** (PCA/t-SNE) reveals cluster structure in 2D.
4. **Nearest neighbors** in embedding space reflect semantic similarity.

---

## Synthetic Language Corpus

Build a minimal synthetic language — no external dataset.

### Vocabulary

| Category | Tokens |
|----------|--------|
| Animals | cat, dog, cow, lion |
| Fruit | apple, banana, mango, orange |
| Verbs | eat, eats, run, runs, see, sees, chase, chases |

Total vocab: ~16 tokens (+ padding, unknown if needed).

### Sentence Templates

```
The {noun} eats
The {noun} runs
The {noun} sees
The {lion} chases the {noun}
```

Where `{noun}` is filled from animals or fruit lists. Generate all valid combinations → training sentences (~40–80 unique sequences).

**Module:** `datasets/synthetic-language.ts`

```typescript
interface SyntheticCorpus {
  vocab: string[];
  tokenToId: Record<string, number>;
  sequences: number[][];      // input token ids
  targets: number[];          // next token id
  categories: Record<string, 'animal' | 'fruit' | 'verb'>;
}
```

### Task

**Next-token prediction** (causal language modeling on bigrams/trigrams).

- Input: token sequence `[t0, t1, …, t_{n-1}]`
- Target: `t_n`
- Context window: 3 tokens

---

## Model

```
Input(sequence_length) → Embedding(vocab_size, embed_dim) → Flatten → Dense(vocab_size, softmax)
```

| Parameter | Default |
|-----------|---------|
| Embedding dimension | 16 |
| Sequence length | 3 |
| Optimizer | Adam, lr = 0.05 |
| Epochs | 200 |
| Loss | categoricalCrossentropy |

**Module:** `training/models/embedding-lm.ts`

---

## Interactive Experiment

### Controls

| Control | Behavior |
|---------|----------|
| **Train** | Start embedding training |
| **Pause / Resume** | Control training loop |
| **Epoch slider** | Scrub embedding snapshots |
| **Projection** | Toggle PCA / t-SNE (default PCA for speed) |
| **Projection frequency** | Snapshot every 5 epochs |
| **Hover token** | Highlight nearest neighbors |

---

## Visualizations

### 1. Embedding Galaxy (`EmbeddingGalaxy`)

- 2D projection of 16-dim embeddings
- Each token = star (dot)
- Color by category: animals (blue), fruit (green), verbs (amber)
- Size ∝ token frequency in corpus
- **Animate:** stars tween to new positions every 5 epochs (1.2s ease)
- Background: subtle radial gradient (deep space)

### 2. Projection Pipeline

```
embeddings [vocab, 16]
    → PCA (or t-SNE every 20 epochs for performance)
    → 2D coords [vocab, 2]
    → EmbeddingGalaxy
```

**Module:** `visualization/embedding-projection.ts`

- PCA: power iteration or SVD via tfjs — fast, every 5 epochs
- t-SNE: optional, slower, run every 20 epochs or on demand

### 3. Similarity Card (`SimilarityCard`)

On star hover/click:

| Field | Content |
|-------|---------|
| Token | e.g. "cat" |
| Category | animal |
| Top 3 neighbors | dog (0.92), lion (0.87), cow (0.81) |
| Metric | cosine similarity |

Draw faint lines to neighbors in galaxy.

### 4. Training Progress

- Loss chart (single line)
- Perplexity or accuracy (top-1 next token)
- Epoch counter

### 5. Sample Predictions (optional panel)

Show: `The cat ___` → model predicts `eats` with probability p.

---

## Live Training Flow

```
1. Build corpus from templates
2. For epoch 1…200:
   a. Train one epoch on all sequences
   b. If epoch % 5 === 0:
      - Extract embedding matrix
      - Run PCA → 2D coords
      - Push EmbeddingSnapshot to history
   c. Update loss chart
3. On complete → clusters visible (animals together, fruit together, verbs separate)
4. Reveal Key Insight
```

---

## Money Shot

**Mid-training → end:**

- Epoch 0: stars scattered randomly
- Epoch 100+: three clusters emerge — animals, fruit, verbs group separately
- Hover `cat` → neighbors are `dog`, `lion`, not `apple`

User scrubs timeline and watches clusters **form**.

---

## Key Insight

> **Embeddings encode meaning through context.** Similar words attract; unrelated words repel. Space learns semantics without being told categories.

---

## Replay

- Auto-replay embedding positions epoch 0 → 200
- Download galaxy PNG
- Toggle PCA ↔ t-SNE and re-project final embeddings

---

## Acceptance Criteria

- [ ] Synthetic corpus generates from templates
- [ ] Model trains to decreasing loss
- [ ] PCA projection updates every 5 epochs
- [ ] Stars animate smoothly between positions
- [ ] Category colors distinguish clusters visually by epoch 150+
- [ ] Hover shows nearest neighbors with cosine similarity
- [ ] Scrubber jumps to any snapshot
- [ ] Replay animation works
- [ ] Lab marked complete in progress

---

## Component Map

| Section | Components |
|---------|------------|
| Experiment | `EmbeddingGalaxy`, `SimilarityCard` |
| Progress | `LossChart`, `EpochSlider` |
| Controls | `TrainingControls`, projection toggle |
| Insight | Highlight card + `ReplayButton` |

---

## Copy (UI Strings)

| Element | Text |
|---------|------|
| Hero title | Embedding Universe |
| Hero subtitle | Lab 03 · Meaning in vector space |
| CTA | Train Embeddings |
| Hover hint | Hover a star to see neighbors |
| Final statement | Words used in similar contexts end up close together. |

---

## Performance Notes

- Vocab is tiny — full batch training per epoch is fine
- t-SNE: run off main thread or debounce; warn user "Computing projection…"
- Limit animated stars to vocab size (~20); no performance concern

---

## Future Enhancements (post-v1)

- 3D embedding view via R3F
- Custom template builder
- Word2Vec skip-gram variant toggle
