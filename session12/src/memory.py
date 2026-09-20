"""Explicit memory accounting — every byte traceable to a formula."""

from __future__ import annotations

from dataclasses import dataclass

from .config import SimConfig
from .virtual_gpu import VirtualGPU


@dataclass
class MemoryBreakdown:
    parameters: int
    gradients: int
    fp32_master: int
    optimizer: int
    activations: int
    comm_buffers: int
    temporary: int

    @property
    def peak(self) -> int:
        return (
            self.parameters
            + self.gradients
            + self.fp32_master
            + self.optimizer
            + self.activations
            + self.comm_buffers
            + self.temporary
        )


class MemoryAccounting:
    """Per-GPU memory from ownership sets + documented assumptions."""

    def __init__(self, cfg: SimConfig, gpu: VirtualGPU):
        self.cfg = cfg
        self.gpu = gpu

    def parameter_memory(self) -> int:
        n = len(self.gpu.param_element_ids)
        return n * self.cfg.bytes_per_param_train

    def gradient_memory(self) -> int:
        n = len(self.gpu.grad_element_ids)
        # gradients often same dtype as params in mixed precision training
        return n * self.cfg.bytes_per_param_train

    def fp32_master_memory(self) -> int:
        if not self.cfg.use_fp32_master:
            return 0
        n = len(self.gpu.param_element_ids)
        return n * 4

    def optimizer_memory(self) -> int:
        # Adam: m and v in FP32 per owned element
        n = len(self.gpu.optimizer_element_ids)
        return n * 4 * 2

    def activation_memory(self) -> int:
        # illustrative: seq * hidden * layers * batch * bytes
        act_elems = (
            self.cfg.seq_len
            * self.cfg.hidden_dim
            * self.cfg.num_layers
            * self.cfg.batch_per_gpu
        )
        return act_elems * self.cfg.bytes_per_activation_element

    def communication_buffer_memory(self, pending_comm_bytes: int = 0) -> int:
        return pending_comm_bytes

    def temporary_memory(self) -> int:
        # ZeRO-3 all-gather may materialize full weights transiently
        return self.gpu.temp_full_param_elements * self.cfg.bytes_per_param_train

    def breakdown(self, pending_comm_bytes: int = 0) -> MemoryBreakdown:
        return MemoryBreakdown(
            parameters=self.parameter_memory(),
            gradients=self.gradient_memory(),
            fp32_master=self.fp32_master_memory(),
            optimizer=self.optimizer_memory(),
            activations=self.activation_memory(),
            comm_buffers=self.communication_buffer_memory(pending_comm_bytes),
            temporary=self.temporary_memory(),
        )

    def peak_memory(self, pending_comm_bytes: int = 0) -> int:
        return self.breakdown(pending_comm_bytes).peak
