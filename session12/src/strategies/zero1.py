"""ZeRO Stage 1 — optimizer state sharded."""

from __future__ import annotations

from ..communication import all_reduce, apply_comm_to_gpus
from ..compute import step_compute, simulated_time_from_work
from ..config import SimConfig
from ..memory import MemoryAccounting
from ..model import DemoModel
from ..strategies.baseline import StepMetrics
from ..virtual_gpu import assign_zero1_optimizer_shard, make_cluster


def run_zero1_step(cfg: SimConfig, model: DemoModel | None = None) -> StepMetrics:
    model = model or DemoModel.build(cfg)
    gpus = make_cluster(cfg)
    total = cfg.parameter_count
    assign_zero1_optimizer_shard(gpus, total, cfg.world_size)
    ranks = list(range(cfg.world_size))

    comp = step_compute(model, cfg)
    for gpu in gpus:
        gpu.compute_work = comp.total_work
        model.forward_backward(gpu.rank)

    grad_bytes = total * cfg.bytes_per_param_train
    comm = all_reduce(cfg, ranks, grad_bytes)
    apply_comm_to_gpus(gpus, comm)

    pending = grad_bytes // cfg.world_size
    peaks, agg = [], 0
    breakdown = None
    for gpu in gpus:
        mem = MemoryAccounting(cfg, gpu)
        bd = mem.breakdown(pending_comm_bytes=pending)
        gpu.peak_memory_bytes = bd.peak
        peaks.append(bd.peak)
        agg += bd.peak
        if gpu.rank == 0:
            breakdown = {
                "parameters": bd.parameters,
                "gradients": bd.gradients,
                "optimizer": bd.optimizer,
                "activations": bd.activations,
                "buffers": bd.comm_buffers,
                "temporary": bd.temporary,
            }

    compute_time = simulated_time_from_work(comp.total_work, cfg)
    comm_time = comm.simulated_time_s
    total_time = compute_time + comm_time
    return StepMetrics(
        strategy="zero1",
        peak_memory_per_gpu=max(peaks),
        aggregate_memory=agg,
        compute_work=comp.total_work,
        communication_bytes=comm.bytes_moved,
        communication_time=comm_time,
        compute_time=compute_time,
        total_step_time=total_time,
        communication_fraction=comm_time / total_time if total_time else 0.0,
        idle_fraction=comm_time / total_time if total_time else 0.0,
        memory_breakdown=breakdown or {},
    )
