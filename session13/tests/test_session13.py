import torch
from src.config import ModelConfig, load_config
from src.model import CausalLM, count_parameters, theoretical_param_count, build_model
from src.reversible import ReversibleBlock

def test_param_count_near_20m():
    cfg = ModelConfig()
    m = CausalLM(cfg)
    n = count_parameters(m)
    assert 18_000_000 < n < 22_000_000
    assert abs(theoretical_param_count(cfg) - n) / n < 0.05

def test_forward_shapes():
    cfg = ModelConfig(n_layer=2, block_size=32)
    m = CausalLM(cfg)
    x = torch.randint(0, cfg.vocab_size, (2, 32))
    logits, loss = m(x, targets=x)
    assert logits.shape == (2, 32, cfg.vocab_size)
    assert loss.ndim == 0

def test_reversible_reconstruction_euler():
    cfg = ModelConfig(n_layer=2, block_size=32)
    b = ReversibleBlock(cfg, method="euler")
    h = cfg.n_embd // 2
    x1 = torch.randn(2, 16, h)
    x2 = torch.randn(2, 16, h)
    err = b.reconstruction_error(x1, x2)
    assert err < 1e-4

def test_reversible_reconstruction_midpoint():
    cfg = ModelConfig(n_layer=2, block_size=32)
    b = ReversibleBlock(cfg, method="midpoint")
    h = cfg.n_embd // 2
    x1 = torch.randn(2, 16, h)
    x2 = torch.randn(2, 16, h)
    err = b.reconstruction_error(x1, x2)
    # midpoint inverse is approximate
    assert err < 5e-1

def test_config_load():
    from pathlib import Path
    cfg = load_config(Path(__file__).resolve().parents[1] / "config/experiment.yaml")
    cfg.model.validate()

def test_build_reversible_model():
    cfg = ModelConfig(n_layer=2)
    m = build_model(cfg, reversible_method="euler")
    x = torch.randint(0, cfg.vocab_size, (1, 16))
    m.train()
    _, loss = m(x, targets=x)
    assert loss is not None

def test_reversible_param_parity():
    cfg = ModelConfig()
    b = count_parameters(build_model(cfg, "none"))
    e = count_parameters(build_model(cfg, "euler"))
    assert e >= b * 0.95
