"""Simulation configuration — illustrative hardware knobs are labeled in docs."""

from __future__ import annotations

from dataclasses import dataclass

WORLD_SIZE = 32
GPUS_PER_NODE = 8
NUM_NODES = 4

# Simulation assumption (not measured hardware)
DEFAULT_INTRA_NODE_BANDWIDTH_GBPS = 300.0
DEFAULT_INTER_NODE_BANDWIDTH_GBPS = 25.0
DEFAULT_INTRA_NODE_LATENCY_US = 2.0
DEFAULT_INTER_NODE_LATENCY_US = 8.0

# Single-node experiment: treat all ranks as intra-node
SINGLE_NODE_INTRA_GBPS = 400.0
SINGLE_NODE_INTER_GBPS = 400.0


@dataclass(frozen=True)
class SimConfig:
    world_size: int = WORLD_SIZE
    gpus_per_node: int = GPUS_PER_NODE
    parameter_count: int = 1_000_000
    num_layers: int = 4
    hidden_dim: int = 64
    seq_len: int = 32
    batch_per_gpu: int = 1
    bytes_per_param_train: int = 2  # bf16 weights
    use_fp32_master: bool = True
    bytes_per_activation_element: int = 2
    intra_node_bandwidth_gbps: float = DEFAULT_INTRA_NODE_BANDWIDTH_GBPS
    inter_node_bandwidth_gbps: float = DEFAULT_INTER_NODE_BANDWIDTH_GBPS
    intra_node_latency_us: float = DEFAULT_INTRA_NODE_LATENCY_US
    inter_node_latency_us: float = DEFAULT_INTER_NODE_LATENCY_US
    compute_units_per_param_token: float = 6.0  # abstract FLOP-like units
    simulated_seconds_per_compute_unit: float = 1e-9
    bucket_size_bytes: int = 5_000_000
    overlap_fraction: float = 0.6  # conceptual overlap simulation

    def node_id(self, rank: int) -> int:
        return rank // self.gpus_per_node

    def same_node(self, a: int, b: int) -> bool:
        return self.node_id(a) == self.node_id(b)
