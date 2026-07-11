# Word-Unit Denominator (Official)

## Official assignment metric

`X_language = total_BPE_tokens / word_units`

### `count_word_units(text)` algorithm

1. **Normalize** the full text to Unicode NFC.
2. **Split** on Unicode whitespace using Python `str.split()` (no argument).
3. **Discard** empty segments.
4. **Count** remaining segments.

### Handling rules

| Case | Behavior |
|------|----------|
| NFC | Applied before splitting |
| Repeated whitespace | Collapsed by split semantics |
| Newlines/tabs | Treated as whitespace separators |
| Punctuation | Stays attached to adjacent word unit |
| ZWJ / ZWNJ | Preserved inside word units |
| Article markup | Frozen corpora are plain text extracts (no HTML) |

## Sensitivity check (NOT official)

`count_word_units_punct_aware()` splits letter runs from isolated punctuation clusters.
Displayed in UI as **Sensitivity check — not used for official score**.
