from src.config import SimConfig, WORLD_SIZE
from src.memory import MemoryAccounting
from src.virtual_gpu import assign_replicated, make_cluster, shard_elements


def test_parameter_memory_formula():
    cfg = SimConfig(parameter_count=320, world_size=32)
    gpus = make_cluster(cfg)
    assign_replicated(gpus, cfg.parameter_count)
    mem = MemoryAccounting(cfg, gpus[0])
    assert mem.parameter_memory() == 320 * cfg.bytes_per_param_train


def test_optimizer_memory_adam_two_fp32_states():
    cfg = SimConfig(parameter_count=320, world_size=32)
    gpus = make_cluster(cfg)
    gpus[0].optimizer_element_ids = shard_elements(320, 32, 0)
    mem = MemoryAccounting(cfg, gpus[0])
    assert mem.optimizer_memory() == (320 // 32) * 4 * 2


def test_peak_memory_non_negative():
    cfg = SimConfig()
    gpus = make_cluster(cfg)
    assign_replicated(gpus, cfg.parameter_count)
    assert MemoryAccounting(cfg, gpus[0]).peak_memory() > 0
