# Training Data Execution System — Evidence Report

**Generated:** 2026-08-08T03:45:58.486478+00:00
**Evidence Hash:** `c31cd2e07e72aeff49a4b0a6c5f5708c…`

## What Was Consumed

- Consumption events: 125
- Unique shards: 5
- Ledger hash: `5ed219c25d2645b68bd4b09964034dfa…`

## Why It Was Consumed

- Curriculum stage: **stage_a**
- Planned mixture: `{'english': 0.4, 'code': 0.2, 'indic': 0.4}`
- Actual mixture: `{'english': 0.36363636363636365, 'code': 0.36363636363636365, 'indic': 0.2727272727272727}`
- Protected floors: `{'english': 10, 'code': 5, 'indic': 15}`

### OPUS Decisions

- deferred: 8
- accept: 2
- protected_override: 3

## What The Model Learned

- Learning events: 125
- Final loss: 4.520712083956399
- Final perplexity: 91.9010159228735
- OPUS in learning ledger: `{'accept': 50, 'protected_override': 75}`

## How To Reconstruct

1. Load tokenizer and verify hash
2. Load manifest and verify manifest_hash
3. Read consumption ledger — batch_ids_in_order defines training sequence
4. Read learning ledger — loss/perplexity per batch with OPUS attribution
5. Load checkpoint at crash point — resume from current_batch offset
6. Replay: recompute batch hashes from registry without regeneration

- Resume from batch: 25
- Batch sequence verified: True

## Audit Results

- Total checks: 19
- Passed: 19
- All passed: True

### Check Details

- ✅ **tokenizer_hash_verified**: 7fa988eb7af48db8993c942c04c0f40bb552a8044ec652e9958309fadb8a31f0
- ✅ **shards_created**: 13 shards
- ✅ **manifests_verified**: 1 manifests
- ✅ **mixture_compiled**: stage_a
- ✅ **opus_decisions_recorded**: 13 decisions
- ✅ **eval_shard_blocked**: 2 eval shards blocked
- ✅ **packing_completed**: util=67.19%
- ✅ **crash_simulated**: 
- ✅ **checkpoint_saved**: 4555bef0-f1df-43bd-b262-34e3bf48aaa3
- ✅ **resume_next_batch_matched**: 
- ✅ **replay_hash_matched**: 
- ✅ **fork_created**: 1 forks
- ✅ **consumption_ledger_recorded**: 125 events
- ✅ **learning_ledger_recorded**: 125 events
- ✅ **no_duplicate_batches**: 
- ✅ **no_skipped_batches**: 
- ✅ **protected_floors_active**: 
- ✅ **metrics_reconstructable**: 
- ✅ **audit_completed**: 

## Metrics Verification (recomputed from batches)

- All metrics match: **True**
- Useful tokens: reported=1075 recomputed=1075
- Packing %: reported=67.19% recomputed=67.19%

## Replay Verification

- Batches verified: 25/25
- All matched: True

## Hashes

- Tokenizer: `7fa988eb7af48db8993c942c04c0f40b…`
- Manifest: `75d7efe1a2e7a2804b622ac24d296700…`