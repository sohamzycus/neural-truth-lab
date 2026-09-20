from src.config import SimConfig
from src.simulation import run_strategy
from src.virtual_gpu import (
    assign_replicated,
    assign_zero1_optimizer_shard,
    assign_zero2_grad_opt_shard,
    assign_zero3_full_shard,
    count_replication_factor,
    make_cluster,
)


def test_strategy_runs_return_ordered_memory_drop():
    cfg = SimConfig()
    base = run_strategy("baseline_dp", cfg).peak_memory_per_gpu
    z1 = run_strategy("zero1", cfg).peak_memory_per_gpu
    z2 = run_strategy("zero2", cfg).peak_memory_per_gpu
    z3 = run_strategy("zero3", cfg).peak_memory_per_gpu
    assert base > z1 > z2
    # zero3 peak may include temporary full weights during forward
    assert z3 < base


def test_zero3_comm_exceeds_baseline():
    cfg = SimConfig()
    b = run_strategy("baseline_dp", cfg).communication_bytes
    z3 = run_strategy("zero3", cfg).communication_bytes
    assert z3 > b


def test_ownership_maps_not_formula_only():
    cfg = SimConfig()
    total = cfg.parameter_count
    gpus = make_cluster(cfg)
    assign_zero3_full_shard(gpus, total, cfg.world_size)
    assert count_replication_factor(gpus, "param_element_ids", total) == 1
    assign_replicated(gpus, total)
    assert count_replication_factor(gpus, "param_element_ids", total) == cfg.world_size
