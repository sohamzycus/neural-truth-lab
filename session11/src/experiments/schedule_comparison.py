"""EXP-SCHEDULE-001 — Cosine vs WSD controlled comparison."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

from src.core.data import TinyCorpus
from src.core.model import TinyGPT
from src.core.mode_config import schedule_total_steps, schedule_warmup, schedule_stable
from src.core.schemas import DataConfig, LabConfig, ModelConfig, OptimizerConfig, RuntimeConfig, ScheduleConfig
from src.core.training import capture_init_state, train_with_schedule
from src.core.seed import set_seed
from src.validation.comparison_validator import RunConfig, validate_comparison
from src.reporting.ledger import EvidenceLedger, apply_decision_policy
from src.reporting.plots import save_figure
from src.reporting.tables import write_csv, write_json
from src.reporting.markdown_report import write_markdown

ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "figures"
OFFICIAL_INDEX = 199  # step 200


def _base_cfg(mode: str) -> LabConfig:
    steps = schedule_total_steps(mode)
    return LabConfig(
        model=ModelConfig(seed=1337),
        optimizer=OptimizerConfig(learning_rate=3e-4, weight_decay=0.0),
        schedule=ScheduleConfig(
            warmup_steps=schedule_warmup(mode),
            stable_steps=schedule_stable(mode),
            total_steps=steps,
        ),
        data=DataConfig(batch_size=2, seed_offset=0),
        runtime=RuntimeConfig(device="cpu", grad_clip=1.0, execution_mode=mode),
    )


def _run_one(cfg: LabConfig, corpus: TinyCorpus, schedule: str, init_state: dict) -> dict[str, Any]:
    result = train_with_schedule(
        cfg, corpus, cfg.schedule.total_steps, schedule_name=schedule, init_state=init_state
    )
    losses = [s.loss for s in result.steps]
    lrs = [s.learning_rate for s in result.steps]

    def loss_at(index: int) -> float:
        return losses[index] if index < len(losses) else float("nan")

    best_i = min(range(len(losses)), key=lambda i: losses[i])
    return {
        "schedule_type": schedule,
        "loss_at_step_200": loss_at(OFFICIAL_INDEX),
        "loss_at_step_300": loss_at(299),
        "best_loss": losses[best_i],
        "best_step": best_i,
        "final_learning_rate": lrs[-1] if lrs else 0,
        "loss_variance": float(sum((l - sum(losses) / len(losses)) ** 2 for l in losses) / max(len(losses), 1)),
        "divergence_flag": result.divergence_flag,
        "configuration_hash": cfg.full_hash(),
        "execution_mode": cfg.runtime.execution_mode,
        "losses": losses,
        "lrs": lrs,
    }


def run(execution_mode: str = "full", ledger: EvidenceLedger | None = None) -> dict:
    cfg = _base_cfg(execution_mode)
    corpus = TinyCorpus()
    set_seed(cfg.model.seed)
    init_model = TinyGPT(cfg.model, corpus.vocab_size)
    init_state = capture_init_state(init_model)

    controls_base = {
        "model": cfg.model.to_dict(),
        "initialization": cfg.model.seed,
        "data": "TinyCorpus",
        "data_order": "seed+step",
        "seed_policy": cfg.model.seed,
        "optimizer": cfg.optimizer.to_dict(),
        "batch_size": cfg.data.batch_size,
        "grad_accumulation": cfg.runtime.grad_accumulation,
        "dtype": cfg.runtime.dtype,
        "grad_clip": cfg.runtime.grad_clip,
        "weight_decay": cfg.optimizer.weight_decay,
        "total_steps": cfg.schedule.total_steps,
    }

    run_cosine_cfg = RunConfig(controls={**controls_base, "schedule": "cosine"}, changed_variable="schedule")
    run_wsd_cfg = RunConfig(controls={**controls_base, "schedule": "wsd"}, changed_variable="schedule")
    cmp = validate_comparison(run_cosine_cfg, run_wsd_cfg)

    cosine_result = _run_one(cfg, corpus, "cosine", init_state)
    wsd_result = _run_one(cfg, corpus, "wsd", init_state)

    for r in (cosine_result, wsd_result):
        r["comparison_validation_status"] = cmp.status

    rows = [{k: v for k, v in r.items() if k not in ("losses", "lrs")} for r in [cosine_result, wsd_result]]
    write_csv(OUTPUTS / "schedule_comparison.csv", rows)
    write_json(OUTPUTS / "schedule_comparison.json", rows)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(cosine_result["losses"], label="cosine")
    ax.plot(wsd_result["losses"], label="wsd")
    ax.axvline(OFFICIAL_INDEX, color="red", ls="--", linewidth=2, label="official stop @ step 200")
    ax.scatter([OFFICIAL_INDEX], [cosine_result["loss_at_step_200"]], color="C0", s=80, zorder=5)
    ax.scatter([OFFICIAL_INDEX], [wsd_result["loss_at_step_200"]], color="C1", s=80, zorder=5)
    ax.set_xlabel("Step")
    ax.set_ylabel("Loss")
    ax.legend()
    ax.set_title("Cosine vs WSD — both trained 300 steps, compared at step 200")
    save_figure(fig, FIGURES / "cosine_vs_wsd_loss.png")

    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.plot(cosine_result["lrs"], label="cosine")
    ax2.plot(wsd_result["lrs"], label="wsd")
    ax2.axvline(OFFICIAL_INDEX, color="red", ls="--", label="step 200")
    ax2.set_xlabel("Step")
    ax2.set_ylabel("Learning rate")
    ax2.legend()
    save_figure(fig2, FIGURES / "cosine_vs_wsd_lr.png")

    l200_c = cosine_result["loss_at_step_200"]
    l200_w = wsd_result["loss_at_step_200"]
    rel_diff = abs(l200_c - l200_w) / max(min(l200_c, l200_w), 1e-8)

    if not cmp.valid:
        status_val = "INVALID_EXPERIMENT"
        confidence = "NONE"
        model_to_keep = "NONE — invalid comparison"
    elif rel_diff < 0.01:
        status_val = "INCONCLUSIVE"
        confidence = "LOW"
        model_to_keep = "NEITHER — difference below 1% threshold"
    else:
        status, confidence = apply_decision_policy(
            controls_valid=True,
            result_missing=False,
            relative_improvement=rel_diff,
            inconclusive_threshold=0.01,
        )
        status_val = status.value
        model_to_keep = "WSD" if l200_w < l200_c else "cosine"

    md = f"""# Schedule Decision — EXP-SCHEDULE-001

**Execution mode:** {execution_mode}
**Control validation:** {cmp.status}
**Training budget:** 300 steps each run
**Official comparison checkpoint:** step 200 (index {OFFICIAL_INDEX})

| Schedule | Loss @ step 200 | Loss @ step 300 | Best loss | Variance |
|----------|----------------:|----------------:|----------:|---------:|
| cosine | {l200_c:.4f} | {cosine_result['loss_at_step_300']:.4f} | {cosine_result['best_loss']:.4f} | {cosine_result['loss_variance']:.6f} |
| wsd | {l200_w:.4f} | {wsd_result['loss_at_step_300']:.4f} | {wsd_result['best_loss']:.4f} | {wsd_result['loss_variance']:.6f} |

**Relative diff at step 200:** {rel_diff:.4f} (MEASURED)
**Decision:** {status_val}
**Model I would keep:** {model_to_keep} (based on lower loss at step 200 under validated controls)

Step 300 reported as late-stage diagnostic only.
"""
    write_markdown(OUTPUTS / "schedule_decision.md", md)

    summary = {
        "execution_mode": execution_mode,
        "loss_cosine_step_200": l200_c,
        "loss_wsd_step_200": l200_w,
        "model_to_keep": model_to_keep,
        "comparison_validation_status": cmp.status,
        "decision": status_val,
    }
    write_json(OUTPUTS / "schedule_summary.json", summary)

    if ledger is not None:
        ledger.append(
            EvidenceLedger.make_record(
                evidence_id="EVD-SCHED-001",
                experiment_id="EXP-SCHEDULE-001",
                claim_id="CLAIM-004",
                hypothesis="Schedule affects loss under controls",
                controls=controls_base,
                changed_variable="schedule",
                seed=1337,
                model_config=cfg.model.to_dict(),
                optimizer_config=cfg.optimizer.to_dict(),
                schedule_config=cfg.schedule.to_dict(),
                data_config=cfg.data.to_dict(),
                runtime_config=cfg.runtime.to_dict(),
                raw_artifacts=[
                    "outputs/schedule_comparison.csv",
                    "outputs/schedule_comparison.json",
                    "outputs/schedule_decision.md",
                    "outputs/schedule_summary.json",
                    "outputs/figures/cosine_vs_wsd_loss.png",
                    "outputs/figures/cosine_vs_wsd_lr.png",
                ],
                derived_metrics={
                    "loss_at_step_200": {"cosine": l200_c, "wsd": l200_w, "label": "MEASURED"},
                    "model_to_keep": {"value": model_to_keep, "label": "CALCULATED"},
                },
                statistical_summary=summary,
                decision=status_val,
                confidence=confidence,
                limitations=["Tiny model, CPU, single seed"],
                reproducibility_command=f"python scripts/run_schedule_comparison.py --mode {execution_mode}",
                execution_mode=execution_mode,
            )
        )

    return summary
