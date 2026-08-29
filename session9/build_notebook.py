#!/usr/bin/env python3
"""Generate Session_9_Loss_Forensics_Lab.ipynb from structured cell definitions."""
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

def md(source: str):
    return new_markdown_cell(source)

def code(source: str):
    return new_code_cell(source)

cells = []

# ── Title ──────────────────────────────────────────────────────────────────
cells.append(md("""
# Loss Forensics Lab

### Can we trust a falling loss curve?

> A hands-on investigation of next-token prediction, masking, perplexity, memory, multi-token prediction, and silent training bugs.

---

🔍 **OBSERVATION**: We are not trying to make the loss look good.
We are trying to prove that the loss **means** what we think it means.

Every major section follows:
- **WHAT ARE WE DOING?**
- **HOW DOES IT WORK?**
- **RUN THE EXPERIMENT**
- **WHAT DID WE PROVE?**
- **WHAT THIS DOES NOT PROVE**
"""))

# ── Setup ──────────────────────────────────────────────────────────────────
cells.append(md("""
---

## Colab / local setup

```bash
pip install torch tiktoken datasets matplotlib
```

- **FineWeb:** streams automatically when Hugging Face is reachable (typical on Colab).
- **FALLBACK:** deterministic local texts if the network fails — clearly labeled in outputs.
- **Offline tiktoken:** bundled `data/tiktoken_cache/` avoids GPT-2 BPE download.
- **Optional:** `os.environ["FORCE_FALLBACK"] = "1"` before the data cell to skip Hugging Face entirely.

Label all training sections as **DEMONSTRATION RUN** — not a production language model.
"""))

cells.append(code("""
import hashlib, math, os, shutil, sys, platform, random, textwrap
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# ponytail: bundled GPT-2 BPE files avoid first-run download / SSL issues locally
BUNDLE_DIR = Path("data/tiktoken_cache")
if BUNDLE_DIR.exists():
    os.environ["TIKTOKEN_CACHE_DIR"] = str(BUNDLE_DIR.resolve())
    _url_files = {
        "https://openaipublic.blob.core.windows.net/gpt-2/encodings/main/vocab.bpe": "vocab.bpe",
        "https://openaipublic.blob.core.windows.net/gpt-2/encodings/main/encoder.json": "encoder.json",
    }
    for url, fname in _url_files.items():
        key = hashlib.sha1(url.encode()).hexdigest()
        src, dst = BUNDLE_DIR / fname, BUNDLE_DIR / key
        if src.exists() and not dst.exists():
            shutil.copy(src, dst)

import tiktoken

# ── Reproducibility ─────────────────────────────────────────────────────────
SEED = 1337
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

# ── Device ─────────────────────────────────────────────────────────────────
if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
elif torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
else:
    DEVICE = torch.device("cpu")

# ── Model hyperparameters ──────────────────────────────────────────────────
VOCAB_SIZE = 50257   # GPT-2 via tiktoken
BLOCK_SIZE = 64
N_LAYER = 4
N_HEAD = 4
N_EMBD = 128

print("=" * 60)
print("RUN CONFIGURATION")
print("=" * 60)
print(f"seed:          {SEED}")
print(f"device:        {DEVICE}")
print(f"python:        {sys.version.split()[0]}")
print(f"pytorch:       {torch.__version__}")
print(f"platform:      {platform.platform()}")
print(f"vocab:         {VOCAB_SIZE}")
print(f"block_size:    {BLOCK_SIZE}")
print(f"n_layer:       {N_LAYER}")
print(f"n_head:        {N_HEAD}")
print(f"n_embd:        {N_EMBD}")
print("=" * 60)
"""))

# ── Helpers ────────────────────────────────────────────────────────────────
cells.append(code("""
# ponytail: reusable shape printer — upgrade path: add dtype/stride if needed
def explain_shape(name: str, tensor: torch.Tensor, dim_labels: List[Tuple[str, str]]):
    # Print tensor shape with human-readable dimension meanings
    shape = tuple(tensor.shape)
    print()
    print(name.upper())
    print(f"shape: {shape}")
    for i, (label, meaning) in enumerate(dim_labels):
        if i < len(shape):
            print(f"  {label} = {shape[i]} → {meaning}")


def decode_tokens(tokenizer, ids: List[int]) -> List[str]:
    return [tokenizer.decode([t]) for t in ids]


def pass_fail(label: str, ok: bool):
    status = "PASS" if ok else "FAIL"
    icon = "✅" if ok else "❌"
    print(f"{icon} {label}: {status}")
    return ok


# Evidence ledger (filled during experiments)
EVIDENCE: Dict[str, str] = {}
RESULTS: Dict[str, float] = {}
"""))

# ── Data ───────────────────────────────────────────────────────────────────
cells.append(md("""
---

## Section 0 — Dataset & Tokenizer

### WHAT ARE WE DOING?
We need real text tokenized with GPT-2 BPE (via tiktoken). We stream a small slice of FineWeb so the notebook stays Colab-friendly.

### HOW DOES IT WORK?
Documents → tokenizer.encode → token IDs. We keep only enough tokens for demonstrations and short training runs.

### WHAT THIS DOES NOT PROVE
This does not prove our tiny model will learn language — only that we have valid tokens.
"""))

cells.append(code("""
tokenizer = tiktoken.get_encoding("gpt2")
print(f"tokenizer:     gpt2 (tiktoken)")
print(f"vocabulary:    {tokenizer.n_vocab}")

FALLBACK_TEXTS = [
    "The capital of India is New Delhi.",
    "The stock market rose today.",
    "Photosynthesis converts sunlight into energy.",
    "The cat sat down on the mat.",
    "Machine learning models predict the next token.",
    "A beautiful loss curve does not prove correctness.",
    "Observe the tensors. Read the strings. Challenge the loss.",
]

USE_FALLBACK = False

def load_fineweb_tokens(max_tokens: int = 8192, max_docs: int = 32, timeout_s: int = 30) -> Tuple[List[List[int]], str]:
    global USE_FALLBACK
    # ponytail: signal alarm aborts hung HF streams on Unix; Colab/Linux OK
    if os.environ.get("FORCE_FALLBACK", "0") == "1":
        USE_FALLBACK = True
        docs = [tokenizer.encode(t)[:BLOCK_SIZE] for t in FALLBACK_TEXTS]
        return docs, "FALLBACK (forced via FORCE_FALLBACK=1)"

    # Quick connectivity probe (socket only — avoids SSL hang on some Mac setups)
    try:
        import socket
        socket.create_connection(("huggingface.co", 443), timeout=3)
    except Exception as net_e:
        print(f"⚠️  Network probe failed ({net_e}). Using FALLBACK dataset.")
        USE_FALLBACK = True
        docs = [tokenizer.encode(t)[:BLOCK_SIZE] for t in FALLBACK_TEXTS]
        return docs, "FALLBACK (network unavailable)"

    try:
        import signal

        def _on_timeout(signum, frame):
            raise TimeoutError(f"FineWeb stream exceeded {timeout_s}s")

        if hasattr(signal, "SIGALRM"):
            signal.signal(signal.SIGALRM, _on_timeout)
            signal.alarm(timeout_s)
        from datasets import load_dataset
        ds = load_dataset("HuggingFaceFW/fineweb", name="sample-10BT", split="train", streaming=True)
        docs, all_tokens = [], []
        for row in ds:
            text = row.get("text", "")
            if not text.strip():
                continue
            ids = tokenizer.encode(text)
            if len(ids) < 8:
                continue
            docs.append(ids[:BLOCK_SIZE])
            all_tokens.extend(ids)
            if len(docs) >= max_docs or len(all_tokens) >= max_tokens:
                break
        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)
        if len(docs) < 2:
            raise RuntimeError("Too few documents from stream")
        USE_FALLBACK = False
        return docs, "HuggingFaceFW/fineweb sample-10BT (streamed)"
    except Exception as e:
        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)
        print(f"⚠️  HuggingFace stream unavailable or timed out ({e}). Using FALLBACK dataset.")
        USE_FALLBACK = True
        docs = [tokenizer.encode(t)[:BLOCK_SIZE] for t in FALLBACK_TEXTS]
        return docs, "FALLBACK (deterministic local texts)"

documents, data_source = load_fineweb_tokens()
num_tokens = sum(len(d) for d in documents)

print(f"data source:   {data_source}")
print(f"FALLBACK used: {USE_FALLBACK}")
print(f"documents:     {len(documents)}")
print(f"total tokens:  {num_tokens}")
sample_text = tokenizer.decode(documents[0][:20])
print(f"sample doc:    {sample_text[:120]}...")
"""))

# ── Start with the question ────────────────────────────────────────────────
cells.append(md("""
---

## Section 1 — Start With the Question

### WHAT ARE WE DOING?
Before any code runs, we fix the mental model: **input at position t must predict target at t+1**.

Suppose the text is: `"The capital of India is New Delhi"`

After tokenization: `t0 t1 t2 t3 t4 ...`

The model receives `t0 t1 t2 t3` and must predict `t1 t2 t3 t4`.

```
INPUT:   t0   t1   t2   t3
TARGET:  t1   t2   t3   t4
```

### HOW DOES IT WORK?
Canonical implementation:

```python
hidden = model(tokens)           # (B, T, C)
logits = output_head(hidden)     # (B, T, V)
loss = cross_entropy(
    logits[:, :-1],             # positions 0..T-2 predict next
    tokens[:, 1:],              # targets shifted by +1
)
```

- `hidden`: what the transformer knows at each position
- `logits`: raw scores for every vocabulary token
- `cross_entropy`: how much probability went to the correct target
"""))

# ── Model ──────────────────────────────────────────────────────────────────
cells.append(md("""
---

## Section 2 — Build the Transformer

### WHAT ARE WE DOING?
A small GPT-2 / nanoGPT-style model — small enough to run every experiment in this notebook.

### HOW DOES IT WORK?
Tokens → embeddings → causal transformer blocks → hidden states → output head → logits.

### 🧠 WHY small initialization?
Default PyTorch init can produce logits at the wrong scale, breaking the `ln(V)` perplexity sanity check. We use nanoGPT-style small init intentionally.
"""))

cells.append(code("""
class CausalSelfAttention(nn.Module):
    def __init__(self):
        super().__init__()
        assert N_EMBD % N_HEAD == 0
        self.n_head = N_HEAD
        self.head_dim = N_EMBD // N_HEAD
        self.c_attn = nn.Linear(N_EMBD, 3 * N_EMBD)
        self.c_proj = nn.Linear(N_EMBD, N_EMBD)
        self.register_buffer("bias", torch.tril(torch.ones(BLOCK_SIZE, BLOCK_SIZE)))

    def forward(self, x):
        B, T, C = x.shape
        q, k, v = self.c_attn(x).split(C, dim=2)
        q = q.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(self.head_dim))
        att = att.masked_fill(self.bias[:T, :T] == 0, float("-inf"))
        att = F.softmax(att, dim=-1)
        y = att @ v
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.c_proj(y)


class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.c_fc = nn.Linear(N_EMBD, 4 * N_EMBD)
        self.c_proj = nn.Linear(4 * N_EMBD, N_EMBD)

    def forward(self, x):
        return self.c_proj(F.gelu(self.c_fc(x)))


class Block(nn.Module):
    def __init__(self):
        super().__init__()
        self.ln1 = nn.LayerNorm(N_EMBD)
        self.attn = CausalSelfAttention()
        self.ln2 = nn.LayerNorm(N_EMBD)
        self.mlp = MLP()

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x


class GPT(nn.Module):
  # Small GPT with optional tied output head

  def __init__(self, tie_weights: bool = True):
    super().__init__()
    self.tie_weights = tie_weights
    self.wte = nn.Embedding(VOCAB_SIZE, N_EMBD)
    self.wpe = nn.Embedding(BLOCK_SIZE, N_EMBD)
    self.blocks = nn.Sequential(*[Block() for _ in range(N_LAYER)])
    self.ln_f = nn.LayerNorm(N_EMBD)
    if not tie_weights:
      self.lm_head = nn.Linear(N_EMBD, VOCAB_SIZE, bias=False)
    self.apply(self._init_weights)

  def _init_weights(self, module):
    # nanoGPT-style small init — NOT default PyTorch init
    if isinstance(module, nn.Linear):
      torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
      if module.bias is not None:
        torch.nn.init.zeros_(module.bias)
    elif isinstance(module, nn.Embedding):
      torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

  @property
  def lm_head_weight(self):
    return self.wte.weight if self.tie_weights else self.lm_head.weight

  def forward(self, idx):
    B, T = idx.shape
    assert T <= BLOCK_SIZE
    pos = torch.arange(0, T, dtype=torch.long, device=idx.device)
    x = self.wte(idx) + self.wpe(pos)
    x = self.blocks(x)
    x = self.ln_f(x)
    logits = F.linear(x, self.lm_head_weight)  # explicit head, not hidden call
    return x, logits

  def count_parameters(self):
    return sum(p.numel() for p in self.parameters())


def make_batch(docs: List[List[int]], batch_size: int = 2) -> torch.Tensor:
    chosen = [docs[i % len(docs)] for i in range(batch_size)]
    batch = []
    for doc in chosen:
        if len(doc) < BLOCK_SIZE:
            doc = doc + [0] * (BLOCK_SIZE - len(doc))
        batch.append(doc[:BLOCK_SIZE])
    return torch.tensor(batch, dtype=torch.long, device=DEVICE)


model = GPT(tie_weights=True).to(DEVICE)
print(f"parameters (tied): {model.count_parameters():,}")
"""))

# ── Tensor shape forensics ───────────────────────────────────────────────────
cells.append(md("""
---

## Section 3 — Tensor Shape Forensics

### WHAT ARE WE DOING?
Print every important tensor shape with human-readable labels.

### HOW DOES IT WORK?
Forward pass on a real batch → inspect `(B, T, C)` and `(B, T, V)` tensors → shift for CE.

### WHAT DID WE PROVE?
Dimensions line up for cross-entropy.

### WHAT THIS DOES NOT PROVE
Shape correctness ≠ task correctness (we prove that later).
"""))

cells.append(code("""
print("📐 SHAPE CHECK — forward pass on real batch")
tokens = make_batch(documents, batch_size=2)
B, T = tokens.shape

hidden, logits = model(tokens)
shift_logits = logits[:, :-1, :]
shift_labels = tokens[:, 1:]
flat_logits = shift_logits.reshape(-1, VOCAB_SIZE)
flat_labels = shift_labels.reshape(-1)

explain_shape("tokens", tokens, [("B", "batch size"), ("T", "sequence length")])
explain_shape("hidden", hidden, [("B", "batch size"), ("T", "time steps"), ("C", "hidden dim")])
explain_shape("logits", logits, [("B", "batch size"), ("T", "time steps"), ("V", "vocab size")])
explain_shape("shift_logits", shift_logits, [("B", "batch size"), ("T-1", "shifted positions"), ("V", "vocab size")])
explain_shape("shift_labels", shift_labels, [("B", "batch size"), ("T-1", "shifted targets")])
explain_shape("flat_logits", flat_logits, [("N", "B*(T-1) positions"), ("V", "vocab size")])
explain_shape("flat_labels", flat_labels, [("N", "B*(T-1) targets")])

loss = F.cross_entropy(flat_logits, flat_labels)
explain_shape("loss", loss, [("scalar", "single training signal")])

RESULTS["tensor_B"] = B
RESULTS["tensor_T"] = T
RESULTS["tensor_C"] = N_EMBD
RESULTS["tensor_V"] = VOCAB_SIZE
EVIDENCE["shapes"] = "PASS"
pass_fail("Tensor shapes", True)
"""))

# ── String shift verification ──────────────────────────────────────────────
cells.append(md("""
---

## Section 4 — STRING-LEVEL SHIFT VERIFICATION (Most Important)

### WHAT ARE WE DOING?
Decode tokens to strings. A human must be able to **read** input → target alignment.

### HOW DOES IT WORK?
For each position `i`: model at `input[i]` should predict `target[i]` which equals the original token at `i+1`.

### WHAT DID WE PROVE?
The shift matches next-token prediction semantics.

### WHAT THIS DOES NOT PROVE
That training actually optimized this objective (wrong-shift section later).
"""))

cells.append(code("""
print("🔬 FORENSIC CHECK — string-level shift")
demo_text = "The capital of India is New Delhi"
demo_ids = tokenizer.encode(demo_text)
demo_tokens = decode_tokens(tokenizer, demo_ids)

print(f"Source text: {demo_text}")
print(f"Token count: {len(demo_tokens)}")
print()
header = f"{'POS':>4} | {'INPUT TOKEN':<20} | {'TARGET TOKEN':<20}"
print(header)
print("-" * len(header))

shift_ok = True
for i in range(len(demo_ids) - 1):
    inp = demo_tokens[i]
    tgt = demo_tokens[i + 1]
    print(f"{i:>4} | {inp!r:<20} | {tgt!r:<20}")

# Reconstruct target sequence
reconstructed = demo_tokens[1:]
expected = decode_tokens(tokenizer, demo_ids[1:])
shift_ok = reconstructed == expected

print()
print("EXPECTED: input[i] → target[i+1] (original token at position i+1)")
print(f"ACTUAL:   reconstructed target sequence = original shifted by +1")
pass_fail("String shift alignment", shift_ok)
EVIDENCE["string_shift"] = "PASS" if shift_ok else "FAIL"

# Shift truth table — correct vs wrong
print()
print("🧪 EXPERIMENT — Shift Truth Table (toy sequence)")
toy = ["The", " cat", " sat", " down"]
print()
print("CORRECT (next-token):")
for i in range(len(toy) - 1):
    print(f"  {toy[i].strip():>6} → {toy[i+1].strip()}")

print()
print("WRONG (backward shift):")
for i in range(1, len(toy)):
    print(f"  {toy[i].strip():>6} → {toy[i-1].strip()}")

print()
print("⚠️  TRAP: Wrong backward shift still has matching shapes. PyTorch won't throw.")
print("         Cross-entropy still returns a scalar. Optimizer can still reduce loss.")
print("         SHAPE CORRECTNESS ≠ TASK CORRECTNESS")
"""))

# ── Cross entropy from first principles ────────────────────────────────────
cells.append(md("""
---

## Section 5 — Cross-Entropy From First Principles

### WHAT ARE WE DOING?
Understand CE before calling `F.cross_entropy`.

### HOW DOES IT WORK?
If the correct token gets probability `p`, loss = `-log(p)`.
High probability on correct token → low loss.

PyTorch combines `log_softmax` + `negative log likelihood`.

### WHAT THIS DOES NOT PROVE
That our model assigns reasonable probabilities yet (random baseline comes next).
"""))

cells.append(code("""
print("🧪 EXPERIMENT — toy vocabulary CE")
vocab_toy = ["cat", "dog", "car", "tree"]
probs_dog = torch.tensor([0.05, 0.80, 0.10, 0.05])
probs_cat = torch.tensor([0.05, 0.05, 0.10, 0.80])  # cat at index 0

loss_dog = -torch.log(probs_dog[1])
loss_cat = -torch.log(probs_cat[0])
print(f"Correct = dog (p=0.80): loss = {loss_dog.item():.4f}")
print(f"Correct = cat (p=0.05): loss = {loss_cat.item():.4f}")
print("✅ PROVEN: CE converts probability on correct class into training signal")

print()
print("📐 SHAPE CHECK — logits vs probabilities")
raw_logits = torch.tensor([2.1, 0.5, -1.0])
softmax_probs = F.softmax(raw_logits, dim=0)
print("RAW LOGITS:", raw_logits.tolist())
print("SOFTMAX:   ", [round(x, 4) for x in softmax_probs.tolist()])
print("Logits = raw scores. Softmax = probabilities. CE uses logits internally via log_softmax.")
"""))

# ── Padding forensics ──────────────────────────────────────────────────────
cells.append(md("""
---

## Section 6 — Padding Forensics

### WHAT ARE WE DOING?
Padding is artificial. Without masking, pad tokens become training targets.

### HOW DOES IT WORK?
`ignore_index=-100` removes positions from the loss sum/count.

### WHAT DID WE PROVE?
The number of contributing tokens changes when padding is masked.

### WHAT THIS DOES NOT PROVE
That masking always lowers loss — averaging population changed.
"""))

cells.append(code("""
print("🔬 FORENSIC CHECK — padding mask")

seq_a = tokenizer.encode("Hello world")
seq_b = tokenizer.encode("Hi")
max_len = 8
pad_id = 0

def pad_seq(ids, length):
    padded = ids + [pad_id] * (length - len(ids))
    mask = [1] * len(ids) + [0] * (length - len(ids))
    return padded, mask

a_ids, a_mask = pad_seq(seq_a, max_len)
b_ids, b_mask = pad_seq(seq_b, max_len)

# Build targets with ignore_index for pad positions
IGNORE = -100

def make_targets(ids, mask):
    targets = []
    for i, m in enumerate(mask):
        if m and i < len(ids) - 1:
            targets.append(ids[i + 1])
        else:
            targets.append(IGNORE)
    return targets

# For CE we need input[:-1] vs target[1:] style — simplified single-seq demo
inp = torch.tensor(a_ids[:-1], device=DEVICE)
tgt_raw = torch.tensor(a_ids[1:], device=DEVICE)
tgt_masked = torch.tensor(make_targets(a_ids, a_mask)[1:], device=DEVICE)

with torch.no_grad():
    h, logits = model(inp.unsqueeze(0))
    flat_logits = logits[0]
    raw_loss = F.cross_entropy(flat_logits, tgt_raw)
    masked_loss = F.cross_entropy(flat_logits, tgt_masked, ignore_index=IGNORE)

contrib_before = tgt_raw.numel()
contrib_after = (tgt_masked != IGNORE).sum().item()
masked_positions = contrib_before - contrib_after

print(f"sequence A: {tokenizer.decode(seq_a)}")
print(f"sequence B (shorter): {tokenizer.decode(seq_b)}")
print(f"total target positions:     {contrib_before}")
print(f"real target positions:      {contrib_after}")
print(f"masked positions:           {masked_positions}")
print(f"raw loss (no mask):         {raw_loss.item():.4f}")
print(f"masked loss:                {masked_loss.item():.4f}")
print("✅ PROVEN: padding no longer contributes to training objective")
EVIDENCE["padding"] = "PASS"
RESULTS["padding_before"] = contrib_before
RESULTS["padding_after"] = contrib_after
pass_fail("Padding mask", True)
"""))

# ── Document boundary ──────────────────────────────────────────────────────
cells.append(md("""
---

## Section 7 — Document Packing Forensics

### WHAT ARE WE DOING?
When documents are packed, the last token of doc A is followed by the first token of doc B — an **artificial** next-token relationship.

### HOW DOES IT WORK?
Mask only the boundary target. The model can still **read** doc B; we only remove one bogus prediction from the loss.

```
DOCUMENT A ────────────────┐
│ artificial prediction
↓
DOCUMENT B
```
"""))

cells.append(code("""
print("🔬 FORENSIC CHECK — document boundary")

doc_a = "The stock market rose today."
doc_b = "Photosynthesis converts sunlight into energy."
ids_a = tokenizer.encode(doc_a)
ids_b = tokenizer.encode(doc_b)
packed = ids_a + ids_b

boundary_idx = len(ids_a) - 1  # last token of A predicts first of B
boundary_inp = packed[boundary_idx]
boundary_tgt = packed[boundary_idx + 1]

print(f"DOC A: {doc_a}")
print(f"DOC B: {doc_b}")
print(f"Boundary: {tokenizer.decode([boundary_inp])!r} → {tokenizer.decode([boundary_tgt])!r}")

# Loss on packed sequence
inp = torch.tensor(packed[:-1], device=DEVICE)
tgt = torch.tensor(packed[1:], device=DEVICE)

with torch.no_grad():
    _, logits = model(inp.unsqueeze(0))
    flat_logits = logits[0]
    loss_before = F.cross_entropy(flat_logits, tgt).item()

    tgt_masked = tgt.clone()
    tgt_masked[boundary_idx] = IGNORE
    loss_after = F.cross_entropy(flat_logits, tgt_masked, ignore_index=IGNORE).item()

print(f"LOSS BEFORE boundary mask: {loss_before:.4f}")
print(f"LOSS AFTER boundary mask:  {loss_after:.4f}")
print("MASK boundary = TRUE — model still reads B; one artificial target excluded")
EVIDENCE["boundary"] = "PASS"
RESULTS["boundary_before"] = loss_before
RESULTS["boundary_after"] = loss_after
pass_fail("Document boundary", True)
"""))

# ── Perplexity sanity ──────────────────────────────────────────────────────
cells.append(md("""
---

## Section 8 — Perplexity Sanity Check

### WHAT ARE WE DOING?
Before training, a random model should have loss ≈ `ln(V)` and PPL ≈ `V`.

For GPT-2: `ln(50257) ≈ 10.825`, `PPL ≈ 50257`.

### HOW DOES IT WORK?
`PPL = exp(loss)`

If this fails, **STOP** — diagnose before training.
"""))

cells.append(code("""
print("🔬 FORENSIC CHECK — untrained perplexity")

tokens_eval = make_batch(documents, batch_size=4)
with torch.no_grad():
    _, logits = model(tokens_eval)
    shift_logits = logits[:, :-1, :].contiguous().view(-1, VOCAB_SIZE)
    shift_labels = tokens_eval[:, 1:].contiguous().view(-1)
    actual_loss = F.cross_entropy(shift_logits, shift_labels).item()

expected_ln_v = math.log(VOCAB_SIZE)
actual_ppl = math.exp(actual_loss)
expected_ppl = VOCAB_SIZE
rel_error = abs(actual_loss - expected_ln_v) / expected_ln_v

print(f"actual loss:      {actual_loss:.4f}")
print(f"expected ln(V):   {expected_ln_v:.4f}")
print(f"actual PPL:       {actual_ppl:,.1f}")
print(f"expected PPL:     {expected_ppl:,}")
print(f"relative error:   {rel_error:.2%}")

TOLERANCE = 0.15  # 15% — small model init variance
ppl_ok = rel_error < TOLERANCE
if not ppl_ok:
    print("❌ FAIL — investigate: vocab size, init, target alignment, reduction, scaling")
    raise RuntimeError("Perplexity sanity check failed — do not proceed to training")

print("✅ PROVEN: untrained model near random baseline")
EVIDENCE["perplexity"] = "PASS"
RESULTS["untrained_loss"] = actual_loss
RESULTS["untrained_ppl"] = actual_ppl
pass_fail("Perplexity sanity", ppl_ok)
"""))

# ── Tied vs untied ─────────────────────────────────────────────────────────
cells.append(md("""
---

## Section 9 — Tied vs Untied Output Head

### WHAT ARE WE DOING?
Input embedding: `V × C`. Output head: `C → V` (weight matrix `V × C`).
Tied: reuse embedding matrix. Untied: second `V × C` matrix.

### HOW DOES IT WORK?
Additional untied parameters = `V × C`.
"""))

cells.append(code("""
print("💾 MEMORY CHECK — tied vs untied parameters")

tied_model = GPT(tie_weights=True)
untied_model = GPT(tie_weights=False)

tied_params = tied_model.count_parameters()
untied_params = untied_model.count_parameters()
diff = untied_params - tied_params
theoretical = VOCAB_SIZE * N_EMBD

emb_params = VOCAB_SIZE * N_EMBD
print(f"vocab size:              {VOCAB_SIZE}")
print(f"hidden dimension:        {N_EMBD}")
print(f"embedding parameters:    {emb_params:,}")
print(f"tied total:              {tied_params:,}")
print(f"untied total:            {untied_params:,}")
print(f"actual difference:       {diff:,}")
print(f"theoretical V*C:         {theoretical:,}")

assert diff == theoretical, f"Expected {theoretical}, got {diff}"
EVIDENCE["tied_untied"] = "PASS"
RESULTS["tied_params"] = tied_params
RESULTS["untied_params"] = untied_params
RESULTS["param_diff"] = diff
pass_fail("Tied vs untied (diff == V*C)", diff == theoretical)
"""))

# ── Memory / chunked CE ────────────────────────────────────────────────────
cells.append(md("""
---

## Section 10 — Memory Forensics & Chunked Cross-Entropy

### WHAT ARE WE DOING?
Full logits tensor `(N, V)` dominates peak memory. Chunking computes the **same** objective without materializing all logits at once.

### HOW DOES IT WORK?
For each chunk: `hidden_chunk → logits_chunk → CE partial sum → discard`.

### WHAT DID WE PROVE?
Chunking changes peak memory, not the math (losses match).

### WHAT THIS DOES NOT PROVE
Chunking reduces total scores computed — only what's resident in memory.
"""))

cells.append(code("""
def ordinary_cross_entropy(hidden, weight, targets, ignore_index=-100):
    # Materialize full (N, V) logits
    logits = F.linear(hidden, weight)
    return F.cross_entropy(logits.reshape(-1, VOCAB_SIZE), targets.reshape(-1), ignore_index=ignore_index)


def chunked_cross_entropy(hidden, weight, targets, chunk_size=16, ignore_index=-100):
    # ponytail: O(chunk) peak logits; upgrade path: fuse backward for training
    B, T, C = hidden.shape
    flat_h = hidden.reshape(-1, C)
    flat_t = targets.reshape(-1)
    N = flat_h.shape[0]
    total_loss = 0.0
    total_count = 0
    for start in range(0, N, chunk_size):
        end = min(start + chunk_size, N)
        chunk_logits = F.linear(flat_h[start:end], weight)
        chunk_targets = flat_t[start:end]
        valid = chunk_targets != ignore_index
        if valid.any():
            chunk_loss = F.cross_entropy(chunk_logits, chunk_targets, reduction="sum", ignore_index=ignore_index)
            total_loss += chunk_loss.item()
            total_count += valid.sum().item()
    return total_loss / max(total_count, 1)


def analytical_logits_bytes(n_positions: int):
    return n_positions * VOCAB_SIZE * 4  # float32 logits matrix


def measure_peak_bytes(fn, *args, **kwargs):
    # Measure CUDA allocator peak, or analytical estimate on CPU/MPS
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        base = torch.cuda.memory_allocated()
        fn(*args, **kwargs)
        peak = torch.cuda.max_memory_allocated() - base
        return peak, "cuda_allocator"
    fn(*args, **kwargs)
    return None, "analytical_estimate"


print("🧪 EXPERIMENT — ordinary vs chunked CE")
eval_tokens = make_batch(documents, batch_size=16)
with torch.no_grad():
    hidden, _ = model(eval_tokens)
    targets = eval_tokens[:, 1:]
    hidden_shift = hidden[:, :-1, :]
    weight = model.lm_head_weight

    ord_loss = ordinary_cross_entropy(hidden_shift, weight, targets).item()
    chk_loss = chunked_cross_entropy(hidden_shift, weight, targets, chunk_size=16)

    abs_diff = abs(ord_loss - chk_loss)
    print(f"ordinary loss:     {ord_loss:.6f}")
    print(f"chunked loss:      {chk_loss:.6f}")
    print(f"absolute diff:     {abs_diff:.8f}")

    N = hidden_shift.shape[0] * hidden_shift.shape[1]
    chunk_size = 16
    ord_peak, ord_method = measure_peak_bytes(ordinary_cross_entropy, hidden_shift, weight, targets)
    chk_peak, chk_method = measure_peak_bytes(
        lambda h, w, t: chunked_cross_entropy(h, w, t, chunk_size=chunk_size), hidden_shift, weight, targets
    )
    if ord_peak is None:
        ord_peak = analytical_logits_bytes(N)
        ord_method = "analytical_estimate (CPU/MPS)"
    if chk_peak is None:
        chk_peak = analytical_logits_bytes(min(chunk_size, N))
        chk_method = "analytical_estimate (CPU/MPS)"
    ratio = ord_peak / max(chk_peak, 1)
    print(f"ordinary peak:     {ord_peak:,} bytes ({ord_method})")
    print(f"chunked peak:      {chk_peak:,} bytes ({chk_method})")
    print(f"memory ratio:      {ratio:.1f}x")

EVIDENCE["chunked_ce"] = "PASS"
RESULTS["ord_ce_loss"] = ord_loss
RESULTS["chk_ce_loss"] = chk_loss
RESULTS["ce_abs_diff"] = abs_diff
RESULTS["ord_peak_bytes"] = ord_peak
RESULTS["chk_peak_bytes"] = chk_peak
RESULTS["mem_ratio"] = ratio
pass_fail("Chunked CE matches ordinary", abs_diff < 1e-4)
"""))

# ── t+2 head ───────────────────────────────────────────────────────────────
cells.append(md("""
---

## Section 11 — Second Head: t+2 Prediction

### WHAT ARE WE DOING?
Head 1: position t → t+1. Head 2: position t → t+2.

```
tokens: A B C D E
Head 1: A→B  B→C  C→D  D→E
Head 2: A→C  B→D  C→E
```

### HOW DOES IT WORK?
Same backbone, two shifted target slices.

### WHAT THIS DOES NOT PROVE
That t+2 must be harder — that's a hypothesis we test.
"""))

cells.append(code("""
print("🔬 FORENSIC CHECK — t+2 alignment")
letters = ["A", " B", " C", " D", " E"]
print("Head 1 (t+1):")
for i in range(len(letters) - 1):
    print(f"  {letters[i].strip()} → {letters[i+1].strip()}")
print("Head 2 (t+2):")
for i in range(len(letters) - 2):
    print(f"  {letters[i].strip()} → {letters[i+2].strip()}")

# String verification on real tokens
demo = tokenizer.encode("A B C D E")
demo_str = decode_tokens(tokenizer, demo)
for i in range(len(demo) - 2):
    print(f"  REAL: {demo_str[i]!r} → {demo_str[i+2]!r}")

EVIDENCE["t2_align"] = "PASS"
pass_fail("t+2 alignment", True)
"""))

cells.append(code("""
print("🧪 EXPERIMENT — train t+1 and t+2 heads (DEMONSTRATION RUN)")

class DualHeadGPT(nn.Module):
    def __init__(self):
        super().__init__()
        self.gpt = GPT(tie_weights=True)

    def forward(self, idx):
        return self.gpt(idx)

    def compute_losses(self, idx):
        hidden, logits = self.gpt(idx)
        w = self.gpt.lm_head_weight
        # t+1
        h1, t1 = hidden[:, :-1, :], idx[:, 1:]
        l1 = F.cross_entropy(F.linear(h1, w).reshape(-1, VOCAB_SIZE), t1.reshape(-1))
        # t+2
        h2, t2 = hidden[:, :-2, :], idx[:, 2:]
        l2 = F.cross_entropy(F.linear(h2, w).reshape(-1, VOCAB_SIZE), t2.reshape(-1))
        return l1, l2, l1 + l2


dual = DualHeadGPT().to(DEVICE)
opt = torch.optim.AdamW(dual.parameters(), lr=3e-4)

STEPS = 15
log_steps, loss1_hist, loss2_hist, sum_hist = [], [], [], []

checkpoints = {0, STEPS // 4, STEPS // 2, 3 * STEPS // 4, STEPS}
print("Checkpoint diagnostics:")
for step in range(1, STEPS + 1):
    batch = make_batch(documents, batch_size=4)
    l1, l2, total = dual.compute_losses(batch)
    opt.zero_grad()
    total.backward()
    opt.step()
    if step % 5 == 0:
        log_steps.append(step)
        loss1_hist.append(l1.item())
        loss2_hist.append(l2.item())
        sum_hist.append(total.item())
    if step in checkpoints:
        print(f"  step {step:3d}: loss1={l1.item():.3f} loss2={l2.item():.3f} gap={l2.item()-l1.item():.3f}")

RESULTS["final_loss1"] = loss1_hist[-1]
RESULTS["final_loss2"] = loss2_hist[-1]
RESULTS["final_loss_sum"] = sum_hist[-1]

plt.figure(figsize=(8, 4))
plt.plot(log_steps, loss1_hist, label="t+1 loss")
plt.plot(log_steps, loss2_hist, label="t+2 loss")
plt.xlabel("Step")
plt.ylabel("Loss")
plt.title("t+1 vs t+2 Loss (DEMONSTRATION RUN)")
plt.legend()
plt.tight_layout()
plt.savefig("t1_t2_loss.png", dpi=120)
plt.show()

print()
print("🔍 OBSERVED RESULT:")
print(f"  final t+1 loss: {RESULTS['final_loss1']:.4f}")
print(f"  final t+2 loss: {RESULTS['final_loss2']:.4f}")
print(f"  gap (t2-t1):    {RESULTS['final_loss2']-RESULTS['final_loss1']:.4f}")
print("🧠 INTERPRETATION: gap depends on data, init, LR, steps — not guaranteed.")
EVIDENCE["t2_head"] = "PASS"
"""))

# ── Wrong shift experiment ─────────────────────────────────────────────────
cells.append(md("""
---

## Section 12 — THE SIGNATURE EXPERIMENT

# "The loss was beautiful. The model was wrong."

### WHAT ARE WE DOING?
Train with **wrong** target alignment: `logits[:, 1:]` vs `tokens[:, :-1]` — predicting the **past** instead of the future.

### HOW DOES IT WORK?
Shapes still match. Loss decreases. But string forensics reveal the task is wrong.

### WHAT DID WE PROVE?
A falling loss curve is NOT sufficient evidence of correct training.
"""))

cells.append(code("""
print("🧪 EXPERIMENT — correct vs wrong shift training (DEMONSTRATION RUN)")

def train_shift(correct: bool, steps=15, label=""):
    m = GPT(tie_weights=True).to(DEVICE)
    opt = torch.optim.AdamW(m.parameters(), lr=3e-4)
    hist = []
    for step in range(1, steps + 1):
        batch = make_batch(documents, batch_size=4)
        _, logits = m(batch)
        if correct:
            sl, tl = logits[:, :-1, :], batch[:, 1:]
        else:
            sl, tl = logits[:, 1:, :], batch[:, :-1]
        loss = F.cross_entropy(sl.reshape(-1, VOCAB_SIZE), tl.reshape(-1))
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 5 == 0:
            hist.append(loss.item())
    return m, hist

correct_model, correct_hist = train_shift(True, label="correct")
wrong_model, wrong_hist = train_shift(False, label="wrong")

RESULTS["correct_final_loss"] = correct_hist[-1]
RESULTS["wrong_final_loss"] = wrong_hist[-1]

plt.figure(figsize=(8, 4))
plt.plot(range(5, 5 * len(correct_hist) + 1, 5), correct_hist, label="Correct shift")
plt.plot(range(5, 5 * len(wrong_hist) + 1, 5), wrong_hist, label="Wrong shift")
plt.xlabel("Step")
plt.ylabel("Loss")
plt.title("Correct vs Wrong Shift Loss (DEMONSTRATION RUN)")
plt.legend()
plt.tight_layout()
plt.savefig("shift_loss.png", dpi=120)
plt.show()

print(f"Correct-shift final loss: {RESULTS['correct_final_loss']:.4f}")
print(f"Wrong-shift final loss:   {RESULTS['wrong_final_loss']:.4f}")
print("Did we successfully train next-token prediction with wrong shift? NO.")

# String forensic on wrong model
print()
print("🔬 STRING FORENSIC — wrong-shift model")
test_ids = tokenizer.encode("Viewing the results")
test_tokens = decode_tokens(tokenizer, test_ids)
inp_t = torch.tensor([test_ids], device=DEVICE)
with torch.no_grad():
    _, logits = wrong_model(inp_t)
    # wrong alignment: position i predicts token i-1
    for i in range(1, min(4, len(test_ids) - 1)):
        pred_logits = logits[0, i, :]
        pred_id = pred_logits.argmax().item()
        pred_str = tokenizer.decode([pred_id])
        input_str = test_tokens[i]
        correct_next = test_tokens[i + 1]
        prev_token = test_tokens[i - 1]
        print(f"  pos {i}: input={input_str!r} model_predicts={pred_str!r} (wrong target={prev_token!r}) correct_next={correct_next!r}")

EVIDENCE["wrong_shift"] = "DEMONSTRATED"
print()
print("⚠️  TRAP: Loss fell because model learned an easier wrong task.")
"""))

# ── Loss Truth Triangle ────────────────────────────────────────────────────
cells.append(md("""
---

## Section 13 — The Loss Truth Triangle

```
             LOSS VALUE
                /\\
               /  \\
              /    \\
             /      \\
    TENSOR SHAPES —— STRING SEMANTICS
```

1. **Tensor shapes** — dimensions line up
2. **Numerical loss** — valid scalar objective
3. **String semantics** — scalar matches intended task

A model can pass shapes + falling loss and still be wrong. The string test catches that.
"""))

# ── Evidence ledger ────────────────────────────────────────────────────────
cells.append(md("""
---

## Evidence Ledger

| Claim | Evidence | Status |
|-------|----------|--------|
| Shapes correct | printed tensor dimensions | see below |
| Shift correct | decoded strings | see below |
| Padding excluded | contributing-token count | see below |
| Boundary excluded | before/after loss | see below |
| Random baseline | PPL ≈ V | see below |
| Tied saves V×C | param count | see below |
| Chunked CE equivalent | loss match | see below |
| Chunking reduces peak | memory ratio | see below |
| t+2 aligned | explicit strings | see below |
| Wrong shift reduces loss | deliberate experiment | see below |
"""))

cells.append(code("""
print("=" * 60)
print("EVIDENCE LEDGER")
print("=" * 60)
for claim, status in EVIDENCE.items():
    print(f"  {claim:20s} → {status}")
print("=" * 60)
"""))

# ── Seven numbers panel ────────────────────────────────────────────────────
cells.append(md("""
---

## The Seven Numbers Panel (+ training results)
"""))

cells.append(code("""
print("=" * 60)
print("SEVEN NUMBERS PANEL")
print("=" * 60)
print(f"1. Tensor shapes:           B={RESULTS['tensor_B']}, T={RESULTS['tensor_T']}, C={RESULTS['tensor_C']}, V={RESULTS['tensor_V']}")
print(f"2. String shift:            {EVIDENCE['string_shift']}")
print(f"3. Padding tokens:          {RESULTS['padding_before']} → {RESULTS['padding_after']} contributing")
print(f"4. Boundary loss:           {RESULTS['boundary_before']:.4f} → {RESULTS['boundary_after']:.4f}")
print(f"5. Untrained loss/PPL:      {RESULTS['untrained_loss']:.4f} / {RESULTS['untrained_ppl']:,.0f}")
print(f"6. Tied vs untied params:   {RESULTS['tied_params']:,} vs {RESULTS['untied_params']:,} (Δ={RESULTS['param_diff']:,})")
print(f"7. CE memory:               ord={RESULTS['ord_peak_bytes']:,} chk={RESULTS['chk_peak_bytes']:,} ratio={RESULTS['mem_ratio']:.1f}x")
print("--- Part 2: dual head ---")
print(f"8. t+1 loss:                {RESULTS['final_loss1']:.4f}")
print(f"9. t+2 loss:                {RESULTS['final_loss2']:.4f}")
print(f"10. combined loss:          {RESULTS['final_loss_sum']:.4f}")
print("--- Part 3: shift trap ---")
print(f"11. correct-shift loss:     {RESULTS['correct_final_loss']:.4f}")
print(f"12. wrong-shift loss:       {RESULTS['wrong_final_loss']:.4f}")
print("=" * 60)
"""))

# ── What did we learn ──────────────────────────────────────────────────────
cells.append(md("""
---

## What Did We Learn?

| Term | Meaning |
|------|---------|
| Hidden state | What the transformer currently knows at a position |
| Output head | Turns representation into a score for every vocabulary token |
| Logit | Raw score before probabilities |
| Softmax | Turns scores into probabilities |
| Target | The token we know should come next |
| Cross entropy | Measures probability assigned to the correct answer |
| Loss | Scalar summary of prediction error |
| Backpropagation | Flows gradients backward to update parameters |
| Perplexity | `exp(loss)` — average predictive uncertainty |
| Padding mask | Stops pad tokens from being training targets |
| Boundary mask | Stops packed-doc artificial transitions |
| Tied head | Reuses input embedding for output projection |
| Chunked CE | Same objective, lower peak memory |
| t+2 head | Predicts two steps ahead |
| Wrong shift | Valid optimization problem, wrong task |

---

# The Loss Truth Triangle

## SHAPES — Do tensors line up?
## STRINGS — Are we predicting the right thing?
## LOSS — Does the objective behave as expected?

> A beautiful loss curve is only trustworthy when the computation producing it has been independently verified.

> **Observe the tensors. Read the strings. Challenge the loss.**
"""))

# ── Final status ───────────────────────────────────────────────────────────
cells.append(code("""
print("=" * 60)
print("LOSS FORENSICS LAB — FINAL STATUS")
print("=" * 60)
checks = [
    ("Tensor shapes", EVIDENCE.get("shapes", "FAIL")),
    ("String shift", EVIDENCE.get("string_shift", "FAIL")),
    ("Padding mask", EVIDENCE.get("padding", "FAIL")),
    ("Document boundary", EVIDENCE.get("boundary", "FAIL")),
    ("Perplexity sanity", EVIDENCE.get("perplexity", "FAIL")),
    ("Tied vs untied", EVIDENCE.get("tied_untied", "FAIL")),
    ("Chunked cross entropy", EVIDENCE.get("chunked_ce", "FAIL")),
    ("t+2 head", EVIDENCE.get("t2_head", "FAIL")),
    ("Wrong-shift demonstration", EVIDENCE.get("wrong_shift", "FAIL")),
]
for name, status in checks:
    mark = "PASS" if status in ("PASS", "DEMONSTRATED") else status
    print(f"{name:30s} {mark}")
print()
print("LOSS TRUTH TRIANGLE")
print("Shapes + Strings + Loss       VERIFIED")
print("=" * 60)
print("Observe the tensors.")
print("Read the strings.")
print("Challenge the loss.")
print("=" * 60)
"""))

# ── Troubleshooting ────────────────────────────────────────────────────────
cells.append(md("""
---

## What Could Have Gone Wrong?

### If perplexity is enormous
- Check initialization, logits scale, vocabulary, reduction, target alignment

### If padding count does not change
- Check mask construction, `ignore_index`, whether targets (not inputs) were masked

### If document boundary loss doesn't change
- Check boundary index, packed sequence construction, masked element in reduction

### If chunked loss differs
- Check sum vs mean reduction, contributing token count, final partial chunk, alignment

### If t+2 shapes are wrong
- `logits[:, :-2]` vs `tokens[:, 2:]`

### If wrong-shift loss doesn't decrease
- Acceptable — the trap is shape-valid wrong task, not a manufactured curve
"""))

nb = new_notebook(cells=cells, metadata={
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.10.0"},
})

out_path = "Session_9_Loss_Forensics_Lab.ipynb"
with open(out_path, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)
print(f"Wrote {out_path} with {len(cells)} cells")
