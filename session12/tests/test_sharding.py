from src.config import SimConfig, WORLD_SIZE
from src.virtual_gpu import (
    assign_replicated,
    assign_zero1_optimizer_shard,
    assign_zero2_grad_opt_shard,
    assign_zero3_full_shard,
    count_replication_factor,
    make_cluster,
    sum_shard_coverage,
)


def test_thirty_two_virtual_gpus():
    cfg = SimConfig()
    gpus = make_cluster(cfg)
    assert len(gpus) == WORLD_SIZE
    assert {g.rank for g in gpus} == set(range(WORLD_SIZE))


def test_shard_partition_covers_full_state():
    total = 1_000_000
    gpus = make_cluster(SimConfig(parameter_count=total))
    assign_zero3_full_shard(gpus, total, WORLD_SIZE)
    assert sum_shard_coverage(gpus, "param_element_ids", total) == total
    assert sum_shard_coverage(gpus, "grad_element_ids", total) == total
    assert sum_shard_coverage(gpus, "optimizer_element_ids", total) == total


def test_baseline_full_replication():
    total = 1_000_000
    gpus = make_cluster(SimConfig(parameter_count=total))
    assign_replicated(gpus, total)
    assert count_replication_factor(gpus, "param_element_ids", total) == WORLD_SIZE
    assert count_replication_factor(gpus, "grad_element_ids", total) == WORLD_SIZE
    assert count_replication_factor(gpus, "optimizer_element_ids", total) == WORLD_SIZE


def test_zero1_optimizer_partition_only():
    total = 1_000_000
    gpus = make_cluster(SimConfig(parameter_count=total))
    assign_zero1_optimizer_shard(gpus, total, WORLD_SIZE)
    assert count_replication_factor(gpus, "param_element_ids", total) == WORLD_SIZE
    assert count_replication_factor(gpus, "grad_element_ids", total) == WORLD_SIZE
    assert count_replication_factor(gpus, "optimizer_element_ids", total) == 1


def test_zero2_grad_and_optimizer_partition():
    total = 1_000_000
    gpus = make_cluster(SimConfig(parameter_count=total))
    assign_zero2_grad_opt_shard(gpus, total, WORLD_SIZE)
    assert count_replication_factor(gpus, "param_element_ids", total) == WORLD_SIZE
    assert count_replication_factor(gpus, "grad_element_ids", total) == 1
    assert count_replication_factor(gpus, "optimizer_element_ids", total) == 1


def test_zero3_all_partitioned():
    total = 1_000_000
    gpus = make_cluster(SimConfig(parameter_count=total))
    assign_zero3_full_shard(gpus, total, WORLD_SIZE)
    assert count_replication_factor(gpus, "param_element_ids", total) == 1
    assert count_replication_factor(gpus, "grad_element_ids", total) == 1
    assert count_replication_factor(gpus, "optimizer_element_ids", total) == 1
