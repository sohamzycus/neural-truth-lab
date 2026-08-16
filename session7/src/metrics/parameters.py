"""Trainable parameter accounting."""

from __future__ import annotations

from kronecker.dynamic import dynamic_deterministic_features
from kronecker.fixed import FixedKronecker
from kronecker.fourier import FourierKronecker
from decoder.byte_decoder import ByteDecoder
from decoder.autoregressive_decoder import AutoregressiveDecoder
from decoder.sequence_decoder import SequenceDecoder


def projection_params(feature_dim: int, latent_dim: int) -> int:
    return 0  # deterministic PRNG projection — not trainable


def decoder_params(kind: str, latent_dim: int) -> int:
    decoders = {
        "position_mlp": ByteDecoder,
        "sequence": SequenceDecoder,
        "autoregressive": AutoregressiveDecoder,
    }
    return decoders[kind](latent_dim=latent_dim).trainable_parameters


def accounting_table(vocab_size: int = 64, embed_dim: int = 64, latent_dim: int = 64) -> dict:
    feat_dim = len(dynamic_deterministic_features("x")[0])
    fixed = FixedKronecker()
    dynamic = FourierKronecker()
    rows = {
        "standard_embedding": {
            "input_representation": vocab_size * embed_dim,
            "projection": 0,
            "encoder": 0,
            "decoder": 0,
            "total_trainable": vocab_size * embed_dim,
            "deterministic_state": 0,
        },
        "fixed_kronecker_repr_only": {
            "input_representation": 0,
            "projection": 0,
            "encoder": 0,
            "decoder": 0,
            "total_trainable": 0,
            "deterministic_state": 65,
        },
        "dynamic_kronecker_repr_only": {
            "input_representation": 0,
            "projection": 0,
            "encoder": 0,
            "decoder": 0,
            "total_trainable": 0,
            "deterministic_state": feat_dim,
        },
        "fourier_repr_only": {
            "input_representation": 0,
            "projection": 0,
            "encoder": 0,
            "decoder": 0,
            "total_trainable": 0,
            "deterministic_state": dynamic.signal_len // 2 + 1,
        },
        "dynamic_end_to_end_64d_mlp": {
            "input_representation": 0,
            "projection": 0,
            "encoder": 0,
            "decoder": decoder_params("position_mlp", latent_dim),
            "total_trainable": decoder_params("position_mlp", latent_dim),
            "deterministic_state": feat_dim,
            "note": "64-d deterministic projection (not trainable) + position MLP decoder",
        },
        "dynamic_end_to_end_full_mlp": {
            "input_representation": 0,
            "projection": 0,
            "encoder": 0,
            "decoder": decoder_params("position_mlp", feat_dim),
            "total_trainable": decoder_params("position_mlp", feat_dim),
            "deterministic_state": feat_dim,
            "note": "no projection; full feature vector fed to decoder",
        },
    }
    return rows
