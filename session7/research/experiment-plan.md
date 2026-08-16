# Experiment plan

1. Collision test (fixed, dynamic, fourier, projected latent)
2. Waste metrics by language bucket
3. Deterministic inverse roundtrip (upper bound)
4. Train byte decoder per method; evaluate train + held-out
5. Fourier controlled comparison (same decoder, same budget)
6. Optional LM — deferred

Command: `python experiments/run_all.py`
