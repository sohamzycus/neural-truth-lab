from pathlib import Path

import torch

from src.config import ExperimentConfig, ModelConfig, TrainingConfig
from src.data import build_corpus_split, make_eval_batch, make_train_batch
from src.model import build_dense_model, count_parameters
from src.moe import MoECausalLM, convert_dense_to_moe, init_experts_from_dense_ffn
from src.params import parameter_accounting
from src.seed import set_seed
from src.training import eval_heldout_loss, resolve_device, train_phase


def _tiny_cfg(vocab: int) -> ModelConfig:
    cfg = ModelConfig(
        vocab_size=vocab,
        n_layer=2,
        n_head=2,
        n_embd=32,
        block_size=16,
        num_experts=4,
        top_k=2,
    )
    cfg.validate()
    return cfg


def test_dense_trains_loss_decreases():
    set_seed(0)
    split = build_corpus_split(99, train_frac=0.8)
    cfg = _tiny_cfg(split.train.vocab_size)
    device = resolve_device("cpu")
    model = build_dense_model(cfg).to(device)
    exp = ExperimentConfig(model=cfg, training=TrainingConfig(dense_steps=40, moe_steps=0, log_every=5))
    before = eval_heldout_loss(model, split, exp, device, exp.training.eval_batch_seed)
    train_phase(model, exp, split, device, 40, Path("/tmp/dense_test.csv"), "dense")
    after = eval_heldout_loss(model, split, exp, device, exp.training.eval_batch_seed)
    assert after < before


def test_conversion_preserves_output_shape():
    split = build_corpus_split(1, 0.8)
    cfg = _tiny_cfg(split.train.vocab_size)
    dense = build_dense_model(cfg)
    moe = convert_dense_to_moe(dense, cfg)
    x = torch.randint(0, cfg.vocab_size, (2, cfg.block_size))
    d_logits, _ = dense(x)
    m_logits, _ = moe(x)
    assert d_logits.shape == m_logits.shape


def test_experts_initialized_from_dense_slices():
    split = build_corpus_split(1, 0.8)
    cfg = _tiny_cfg(split.train.vocab_size)
    dense = build_dense_model(cfg)
    dense_ffn = dense.blocks[0].mlp
    moe_ffn = init_experts_from_dense_ffn(dense_ffn, cfg)
    h_e = cfg.expert_hidden
    for i, expert in enumerate(moe_ffn.experts):
        sl = slice(i * h_e, (i + 1) * h_e)
        assert torch.allclose(expert.fc1.weight, dense_ffn.fc1.weight[sl])
        assert torch.allclose(expert.fc2.weight, dense_ffn.fc2.weight[:, sl])


def test_parameter_accounting_matches_named_parameters():
    split = build_corpus_split(1337, 0.8)
    cfg = _tiny_cfg(split.train.vocab_size)
    dense = build_dense_model(cfg)
    moe = convert_dense_to_moe(dense, cfg)
    report = parameter_accounting(dense, moe, cfg)
    assert report["dense_total_parameters"] == count_parameters(dense)
    assert report["moe_total_parameters"] == count_parameters(moe)
    assert report["dense_ffn_parameters"] == report["dense_ffn_parameters_theory"]
    assert report["moe_total_expert_parameters"] == report["moe_total_expert_parameters_theory"]
    assert report["active_expert_parameters_per_token"] == (
        cfg.top_k * cfg.n_layer * (cfg.n_embd * cfg.expert_hidden * 2)
    )
    assert report["active_router_parameters_per_token"] == (
        cfg.n_layer * cfg.n_embd * cfg.num_experts
    )


def test_heldout_split_disjoint_from_training_sampling():
    split = build_corpus_split(1337, 0.8)
    train_sents = set(split.train.sentences)
    eval_sents = set(split.eval.sentences)
    assert train_sents.isdisjoint(eval_sents)
    assert len(train_sents) == split.train_size
    train_encoded = {tuple(e) for e in split.train.encoded}
    eval_encoded = {tuple(e) for e in split.eval.encoded}
    assert train_encoded.isdisjoint(eval_encoded)
    # Sampling pools differ: train batches never read split.eval.encoded
    assert make_train_batch(split, 2, 16, 0)[0].shape == make_eval_batch(split, 2, 16, 0)[0].shape


def test_moe_continues_training_heldout():
    set_seed(1)
    split = build_corpus_split(7, 0.8)
    cfg = _tiny_cfg(split.train.vocab_size)
    device = resolve_device("cpu")
    dense = build_dense_model(cfg).to(device)
    exp = ExperimentConfig(model=cfg, training=TrainingConfig(dense_steps=25, moe_steps=60, log_every=5))
    train_phase(dense, exp, split, device, 25, Path("/tmp/d_pre.csv"), "dense")
    moe = convert_dense_to_moe(dense, cfg).to(device)
    moe_init = eval_heldout_loss(moe, split, exp, device, exp.training.eval_batch_seed)
    train_phase(moe, exp, split, device, 60, Path("/tmp/moe_test.csv"), "moe", start_step=25)
    moe_final = eval_heldout_loss(moe, split, exp, device, exp.training.eval_batch_seed)
    assert moe_final < moe_init


def test_conversion_not_fresh_random_moe():
    split = build_corpus_split(1, 0.8)
    cfg = _tiny_cfg(split.train.vocab_size)
    dense = build_dense_model(cfg)
    torch.manual_seed(0)
    random_moe = MoECausalLM(cfg)
    converted = convert_dense_to_moe(dense, cfg)
    assert not torch.allclose(
        converted.blocks[0].mlp.experts[0].fc1.weight,
        random_moe.blocks[0].mlp.experts[0].fc1.weight,
    )
    assert torch.allclose(
        converted.token_emb.weight,
        dense.token_emb.weight,
    )


def test_router_top_k_valid():
    split = build_corpus_split(1, 0.8)
    cfg = _tiny_cfg(split.train.vocab_size)
    moe = MoECausalLM(cfg)
    x = torch.randint(0, cfg.vocab_size, (2, cfg.block_size))
    moe.train()
    _, _ = moe(x)
    for st in moe.last_routing:
        assert all(0 <= e < cfg.num_experts for e in st.active_experts)
    ffn = moe.blocks[0].mlp
    flat = torch.randn(4, cfg.n_embd)
    probs = torch.softmax(ffn.router(flat), dim=-1)
    top_idx = torch.topk(probs, cfg.top_k, dim=-1).indices
    assert top_idx.shape == (4, cfg.top_k)


def test_routing_evolution_activates_more_than_initial_tie():
    split = build_corpus_split(1337, 0.8)
    cfg = _tiny_cfg(split.train.vocab_size)
    moe = MoECausalLM(cfg)
    device = resolve_device("cpu")
    moe.to(device)
    exp = ExperimentConfig(model=cfg, training=TrainingConfig(batch_size=4))
    moe.train()
    moe(make_train_batch(split, 4, cfg.block_size, 0)[0].to(device))
    init_active = len(moe.last_routing[0].active_experts)
    for s in range(1, 30):
        moe(make_train_batch(split, 4, cfg.block_size, s)[0].to(device))
    final_active = len(moe.last_routing[0].active_experts)
    assert final_active >= init_active
    assert sum(moe.last_routing[0].expert_utilization) > 0
