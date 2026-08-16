# Hypotheses (falsifiable)

## H1 — Dynamic representation reduces capacity waste
Fixed 32-byte slots waste space on short tokens; dynamic encoding reports zero slot-waste for strings under max_bytes.

## H2 — Fewer observed collisions than fixed 32-byte Kronecker on evaluated corpus
Measured via collision_key on full feature vectors before projection.

## H3 — Parameter count is lower than vocabulary embedding at scale
Compare V×D table vs deterministic encoder + small decoder (measured in baseline_params).

## H4 — Projected 64-d latent supports held-out exact reconstruction
**Expected risk:** FAIL due to lossy projection.

## H5 — Representation useful for language modeling
NOT RUN in this submission.
