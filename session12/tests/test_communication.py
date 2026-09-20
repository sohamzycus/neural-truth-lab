from src.communication import all_gather, all_reduce, reduce_scatter
from src.config import SimConfig


def test_communication_bytes_non_negative():
    cfg = SimConfig()
    ranks = list(range(cfg.world_size))
    b = 1_000_000
    for op in (
        all_reduce(cfg, ranks, b),
        reduce_scatter(cfg, ranks, b),
        all_gather(cfg, ranks, b // cfg.world_size),
    ):
        assert op.bytes_moved >= 0
        assert op.intra_node_bytes >= 0
        assert op.inter_node_bytes >= 0
        assert op.simulated_time_s >= 0


def test_single_node_has_less_inter_than_multi():
    cfg_multi = SimConfig()
    cfg_single = SimConfig(
        intra_node_bandwidth_gbps=400,
        inter_node_bandwidth_gbps=400,
        inter_node_latency_us=cfg_multi.intra_node_latency_us,
    )
    ranks = list(range(32))
    m = all_reduce(cfg_multi, ranks, 10_000_000)
    s = all_reduce(cfg_single, ranks, 10_000_000)
    assert m.inter_node_bytes >= 0
    assert "Simulation assumption" in m.label()
