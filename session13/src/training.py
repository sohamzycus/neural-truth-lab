"""Training loop shared by CLI and notebooks."""
from __future__ import annotations
import time
from pathlib import Path
from typing import Optional
import torch
import torch.nn as nn
from src.config import ExperimentConfig
from src.data import TinyCorpus, make_batch
from src.metrics import LossPoint, RunMetrics, utc_now
from src.memory import PeakMemoryTracker
from src.model import build_model, count_parameters, parameter_breakdown
from src.seed import set_seed

def resolve_device(name: str) -> torch.device:
    if name == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
    return torch.device(name)

def lr_at_step(base: float, step: int, warmup: int) -> float:
    if warmup <= 0:
        return base
    return base * min(1.0, (step + 1) / warmup)

def train_experiment(cfg: ExperimentConfig, max_steps: Optional[int] = None, results_dir: Optional[Path] = None) -> RunMetrics:
    set_seed(cfg.seed)
    device = resolve_device(cfg.runtime.device)
    dtype = torch.float32 if cfg.runtime.dtype == "float32" else torch.bfloat16
    method = cfg.mode.reversible_method
    model = build_model(cfg.model, reversible_method=method).to(device)
    if dtype != torch.float32:
        model = model.to(dtype)
    corpus = TinyCorpus()
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.training.learning_rate, weight_decay=cfg.training.weight_decay)
    seq = cfg.model.block_size
    steps = cfg.training.steps_for_tokens(seq)
    if max_steps is not None:
        steps = min(steps, max_steps)
    tokens_target = min(cfg.training.tokens, steps * cfg.training.batch_size * seq * cfg.training.grad_accumulation)
    run_id = cfg.run_label or f"{method}-{cfg.training.batch_size}"
    notes: list[str] = []
    loss_hist: list[LossPoint] = []
    min_loss = float("inf")
    final_loss = float("nan")
    nan_flag = False
    oom = False
    recon_err = None
    if method in ("euler", "midpoint") and cfg.model.n_layer > 0:
        block = model.blocks[0]
        if hasattr(block, "reconstruction_error"):
            with torch.no_grad():
                h = cfg.model.n_embd // 2
                x1 = torch.randn(2, seq, h, device=device)
                x2 = torch.randn(2, seq, h, device=device)
                recon_err = block.reconstruction_error(x1, x2)
    t0 = time.perf_counter()
    tokens_seen = 0
    tracker = PeakMemoryTracker(device)
    try:
        with tracker:
            for step in range(steps):
                lr = lr_at_step(cfg.training.learning_rate, step, cfg.training.warmup_steps)
                for pg in opt.param_groups:
                    pg["lr"] = lr
                loss_accum = 0.0
                for micro in range(cfg.training.grad_accumulation):
                    seed = cfg.seed + step * 100 + micro
                    x, y, _ = make_batch(corpus, cfg.training.batch_size, seq, seed)
                    x, y = x.to(device), y.to(device)
                    opt.zero_grad(set_to_none=True)
                    _, loss = model(x, targets=y)
                    if loss is None:
                        continue
                    lv = float(loss.item())
                    if lv != lv:
                        nan_flag = True
                    loss = loss / cfg.training.grad_accumulation
                    loss.backward()
                    loss_accum += lv
                if cfg.training.grad_clip > 0:
                    torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.training.grad_clip)
                opt.step()
                tokens_seen += cfg.training.batch_size * seq * cfg.training.grad_accumulation
                final_loss = loss_accum / max(cfg.training.grad_accumulation, 1)
                min_loss = min(min_loss, final_loss)
                if step % cfg.training.log_every == 0 or step == steps - 1:
                    loss_hist.append(LossPoint(tokens=tokens_seen, loss=final_loss))
                if cfg.training.checkpoint_every and (step + 1) % cfg.training.checkpoint_every == 0:
                    ckpt = Path(results_dir or ".") / "checkpoints" / f"{run_id}_step{step+1}.pt"
                    ckpt.parent.mkdir(parents=True, exist_ok=True)
                    torch.save({"model": model.state_dict(), "step": step}, ckpt)
    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            oom = True
            notes.append(str(e))
        else:
            raise
    elapsed = time.perf_counter() - t0
    tps = tokens_seen / elapsed if elapsed > 0 else 0.0
    status = "oom" if oom else ("nan" if nan_flag else "ok")
    mem = tracker.snapshot()
    metrics = RunMetrics(
        run_id=run_id,
        status=status,
        parameter_count=count_parameters(model),
        tokens_trained=tokens_seen,
        batch_size=cfg.training.batch_size,
        sequence_length=seq,
        grad_accumulation=cfg.training.grad_accumulation,
        training_time_s=elapsed,
        tokens_per_sec=tps,
        final_loss=final_loss,
        min_loss=min_loss if min_loss != float("inf") else final_loss,
        peak_memory_bytes=mem.peak_memory_bytes,
        peak_rss_bytes=mem.peak_rss_bytes,
        peak_mps_bytes=mem.peak_mps_bytes,
        cpu_user_time_s=mem.cpu_user_time_s,
        cpu_system_time_s=mem.cpu_system_time_s,
        memory_label=mem.label,
        device=str(device),
        dtype=cfg.runtime.dtype,
        reversible_method=method,
        seed=cfg.seed,
        timestamp=utc_now(),
        notes=notes,
        loss_history=loss_hist,
        reconstruction_error=recon_err,
        oom=oom,
        nan=nan_flag,
    )
    if results_dir:
        from src.metrics import save_run
        save_run(metrics, Path(results_dir))
    return metrics
