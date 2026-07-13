# SamaBPE

SamaBPE is one standard Hugging Face BPE tokenizer trained across faithful Markdown snapshots of India's Wikipedia page in English, Hindi, Telugu and Bengali.

**Production:** https://sama-bpe-tokenizer-413.netlify.app

---

## Verified architecture

| Property | Value |
| -------- | ----- |
| Languages | English, Hindi, Telugu, Bengali (`en`, `hi`, `te`, `bn`) |
| Vocabulary size | 10,000 |
| Normalizer | NFKC |
| Pretokenizer | Metaspace (`▁`, prepend_scheme=never) |
| Decoder | Metaspace |
| Round-trip | PASS (reviewer sample + 4 full corpora) |
| Tokenizer SHA-256 | `8d515d68b3ce820dd7fa4b8c31e5e0a19bc7ec9e1f4f982117eaee3f628a0469` |

Metrics below are reproduced by `python evaluate_tokenizer.py` from frozen `submission/` artifacts (not trusted from this table alone).

| Language | Faithful units | Tokens | Fertility | ≤1.2 |
| -------- | -------------: | -----: | --------: | ---- |
| English  | 147,908 | 126,158 | 0.8530 | ✓ |
| Hindi    | 67,473 | 55,978 | 0.8296 | ✓ |
| Telugu   | 27,225 | 22,993 | 0.8446 | — |
| Bengali  | 68,468 | 58,100 | 0.8486 | — |

| Metric | Value |
| ------ | ----- |
| Spread | 0.0233 |
| Adjusted evaluator score | 42,893.47 |
| Winning weights | EN 3 · HI 5 · TE 9 · BN 5 |
| Faithful experiments measured | 2,570 |

---

## Reproduce

```bash
cd submission
pip install -r requirements.txt
python evaluate_tokenizer.py
```

```bash
python scripts/generate_verified_submission_data.py   # UI source of truth
python scripts/run_final_audit.py                     # full audit
```

---

## Authoritative corpus

Evaluator loads `submission/corpus/{lang}.faithful.txt` (`.faithful.md` is byte-identical). Twelve files per language pack: `.md`, `.txt`, `.meta.json`.

---

## Legacy research history — not part of the current faithful resubmission

Earlier experiments used NFKC + punctuation-to-space replacement, Whitespace pretokenizer, word-ish denominator, and a custom JSON BPE. That pipeline failed `decode(encode(text))` on the reviewer sample and is **not** the current submission. Prior experiment counts (e.g. 2,971 non-faithful runs) must not be mixed with the 2,570 faithful-architecture measurements.

## License

MIT
