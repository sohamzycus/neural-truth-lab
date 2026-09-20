"""ZeRO Stage 3 — parameters, gradients, optimizer sharded; all-gather for compute."""

from __future__ import annotations

from ..communication import all_gather, apply_comm_to_gpus, overlap_adjusted_time, reduce_scatter
from ..compute import step_compute, simulated_time_from_work
from ..config import SimConfig
from ..memory import MemoryAccounting
from ..model import DemoModel
from ..strategies.baseline import StepMetrics
from ..virtual_gpu import assign_zero3_full_shard, make_cluster


def run_zero3_step(cfg: SimConfig, model: DemoModel | None = None) -> StepMetrics:
    model = model or DemoModel.build(cfg)
    gpus = make_cluster(cfg)
    total = cfg.parameter_count
    assign_zero3_full_shard(gpus, total, cfg.world_size)
    ranks = list(range(cfg.world_size))

    shard_bytes = (total // cfg.world_size) * cfg.bytes_per_param_train
    full_bytes = total * cfg.bytes_per_param_train

    # Forward/backward need full parameter view transiently
    for gpu in gpus:
        gpu.temp_full_param_elements = total

    gather_fwd = all_gather(cfg, ranks, shard_bytes)
    apply_comm_to_gpus(gpus, gather_fwd)

    comp = step_compute(model, cfg)
    for gpu in gpus:
        gpu.compute_work = comp.total_work
        model.forward_backward(gpu.rank)

    grad_comm = reduce_scatter(cfg, ranks, full_bytes)
    apply_comm_to_gpus(gpus, grad_comm)

    gather_param = all_gather(cfg, ranks, shard_bytes)
    apply_comm_to_gpus(gpus, gather_param)

    for gpu in gpus:
        gpu.temp_full_param_elements = 0

    comm_bytes = gather_fwd.bytes_moved + grad_comm.bytes_moved + gather_param.bytes_moved
    raw_comm_time = gather_fwd.simulated_time_s + grad_comm.simulated_time_s + gather_param.simulated_time_s

    compute_time = simulated_time_from_work(comp.total_work, cfg)
    comm_time = overlap_adjusted_time(
        raw_comm_time,
        compute_time,
        cfg.bucket_size_bytes,
        full_bytes,
        cfg.overlap_fraction,
    )

    peaks, agg = [], 0
    breakdown = None
    for gpu in gpus:
        mem = MemoryAccounting(cfg, gpu)
        # peak during forward: steady shard + temporary full view + comm buffer
        bd_steady = mem.breakdown(pending_comm_bytes=shard_bytes)
        gpu.peak_memory_bytes = bd_steady.peak
        with_temp = MemoryAccounting(cfg, gpu)
        gpu.temp_full_param_elements = total
        bd_peak = with_temp.breakdown(pending_comm_bytes=shard_bytes)
        peak = max(bd_steady.peak, bd_peak.peak)
        gpu.peak_memory_bytes = peak
        gpu.temp_full_param_elements = 0
        peaks.append(peak)
        agg += bd_steady.peak
        if gpu.rank == 0:
            breakdown = {
                "parameters": bd_steady.parameters,
                "gradients": bd_steady.gradients,
                "optimizer": bd_steady.optimizer,
                "activations": bd_steady.activations,
                "buffers": bd_steady.comm_buffers,
                "temporary": bd_peak.temporary,
            }

    total_time = compute_time + comm_time
    return StepMetrics(
        strategy="zero3",
        peak_memory_per_gpu=max(peaks),
        aggregate_memory=agg,
        compute_work=comp.total_work,
        communication_bytes=comm_bytes,
        communication_time=comm_time,
        compute_time=compute_time,
        total_step_time=total_time,
        communication_fraction=comm_time / total_time if total_time else 0.0,
        idle_fraction=comm_time / total_time if total_time else 0.0,
        memory_breakdown=breakdown or {},
    )
