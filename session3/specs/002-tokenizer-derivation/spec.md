# Tokenizer Derivation Spec

## Rules

1. `V_total = 128,000` (embedding efficiency; not 131,072)
2. Bucket sum must equal total (verified in `vocab_derivation.py`)
3. Algorithm: Unigram+BPE hybrid (M1 winner)
4. Exposure weights ≠ pretrain weights (tokenizer optimizes fertility)

## Inputs

`data/inputs/vocab_budget.json`

## Outputs

`data/derived/vocab_allocation.json`

## Acceptance

- Bucket sum == 128,000
- Embedding table size documented in derived JSON
