# Failure analysis

## Lossy 64-d projection
Projected latent collisions appear in summary under `dynamic_kronecker_projected_latent`. Decoder cannot recover unseen strings.

## Fixed window truncation
Telugu/Hindi/Bengali long strings lose tail bytes when >32 UTF-8 bytes.

## Fourier baseline
Frequency magnitudes collide on anagram byte patterns (ab vs ba).

## Decoder capacity
Small MLP + SGD budget insufficient for multilingual exact reconstruction from latent alone.

## Mitigations attempted
- Full feature vector (no projection)
- Full-epoch training for large latent
- Deterministic inverse as information-preserving upper bound

## Remaining limitations
No LM experiment; no production-scale vocab; decoder not autoregressive transformer.
