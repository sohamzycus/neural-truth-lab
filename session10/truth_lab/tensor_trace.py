"""Tensor shape tracing utilities."""

from __future__ import annotations

from typing import Dict, Iterable, Tuple

import torch

from truth_lab.model import TensorTrace, TinyGPT


DIM_MEANINGS = {
    "input_ids": ("B", "T", "batch × tokens"),
    "embeddings": ("B", "T", "D", "batch × tokens × hidden size"),
    "hidden_states_layer0": ("B", "T", "D", "batch × tokens × hidden size"),
    "attention_output_layer0": ("B", "T", "D", "batch × tokens × hidden size"),
    "mlp_output_layer0": ("B", "T", "D", "batch × tokens × hidden size"),
    "final_hidden": ("B", "T", "D", "batch × tokens × hidden size"),
    "logits": ("B", "T", "V", "batch × tokens × vocabulary"),
    "shifted_logits": ("B", "T-1", "V", "batch × shifted tokens × vocabulary"),
    "targets": ("B", "T-1", "batch × target tokens"),
    "mask": ("B", "T-1", "batch × valid-target flags"),
    "loss": ("scalar", "", "single number"),
}


def describe_tensor(name: str, t: torch.Tensor) -> str:
    shape = list(t.shape)
    lines = [
        name,
        f"  shape = {shape}",
        f"  dtype = {t.dtype}",
        f"  numel = {t.numel()}",
    ]
    meaning = DIM_MEANINGS.get(name)
    if meaning:
        dims, desc = meaning[:-1], meaning[-1]
        if dims and dims[0] != "scalar":
            lines.append("  Meaning:")
            for i, label in enumerate(dims):
                if i < len(shape):
                    lines.append(f"    dim {i} ({label}) = {shape[i]}")
            lines.append(f"    → {desc}")
    return "\n".join(lines)


def trace_training_step(
    model: TinyGPT,
    input_ids: torch.Tensor,
    targets: torch.Tensor,
    mask: torch.Tensor,
) -> Tuple[TensorTrace, Dict[str, torch.Tensor]]:
    model.zero_grad(set_to_none=True)
    _, trace = model(input_ids, targets=targets, mask=mask, trace=True)
    assert trace is not None and trace.loss is not None
    loss = trace.loss
    loss.backward()
    grads = {n: p.grad.detach().clone() for n, p in model.named_parameters() if p.grad is not None}
    return trace, grads


def pipeline_diagram() -> str:
    return """```text
WORDS
 ↓
TOKEN IDs
 ↓
EMBEDDINGS
 ↓
TRANSFORMER
 ↓
HIDDEN STATES
 ↓
LOGITS
 ↓
NEXT-WORD SCORES
 ↓
LOSS
```"""


def format_trace_table(trace: TensorTrace) -> str:
    rows = ["| Tensor | Shape | Dimension meaning |", "| --- | --- | --- |"]
    for name, t in trace.as_dict().items():
        meaning = DIM_MEANINGS.get(name, ("?", "?", "?"))
        rows.append(f"| {name} | {list(t.shape)} | {meaning[-1]} |")
    return "\n".join(rows)


def print_all_traces(trace: TensorTrace, grads: Dict[str, torch.Tensor]) -> str:
    chunks = []
    for name, t in trace.as_dict().items():
        chunks.append(describe_tensor(name, t))
        if t.numel() <= 64:
            chunks.append(f"  sample values:\n{t}")
        else:
            flat = t.reshape(-1)[:8]
            chunks.append(f"  first 8 values: {flat.tolist()}")
    chunks.append("\nGradients (parameter tensors):")
    for name, g in list(grads.items())[:6]:
        chunks.append(describe_tensor(f"grad/{name}", g))
    if len(grads) > 6:
        chunks.append(f"  ... and {len(grads) - 6} more parameter gradients")
    return "\n\n".join(chunks)
