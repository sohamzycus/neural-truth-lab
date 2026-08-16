# Methodology

## Fixed Kronecker
32 byte slots × [value, occupied] + overflow flag → deterministic PRNG projection → 64-d latent.

## Dynamic Kronecker (Option A)
Variable bytes (up to 256) with per-byte position features → optional projection → 64-d latent.
Full feature vector (771-d) available with `project_latent=False`.

## Reversibility layers
1. **Deterministic inverse** — parse feature layout (`kronecker/inverse.py`); exact on non-truncated inputs.
2. **Learned decoder** — position-wise MLP; tests invertibility of latent under training budget.

## Metrics
byte_exact_match, string_exact_match, byte/char accuracy, edit distance, collision groups, waste_ratio.
