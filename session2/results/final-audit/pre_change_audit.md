# Pre-Change Submission Audit

**Verdict:** SUBMISSION READY

## Authoritative artifacts

- `submission/tokenizer.json`
- `submission/corpus/{en,hi,te,bn}.faithful.txt` (`.md` identical)
- Corpus loader: submission/corpus/{lang}.faithful.txt (preferred; .md identical byte-for-byte)

## Claim classification

- **tokenizer.sha256**: VERIFIED (saved=8d515d68b3ce820dd7fa4b8c31e5e0a19bc7ec9e1f4f982117eaee3f628a0469, fresh=8d515d68b3ce820dd7fa4b8c31e5e0a19bc7ec9e1f4f982117eaee3f628a0469)
- **en.faithful_units**: VERIFIED (saved=147908, fresh=147908)
- **en.tokens**: VERIFIED (saved=126158, fresh=126158)
- **en.fertility**: VERIFIED (saved=0.8529491305406063, fresh=0.8529491305406063)
- **hi.faithful_units**: VERIFIED (saved=67473, fresh=67473)
- **hi.tokens**: VERIFIED (saved=55978, fresh=55978)
- **hi.fertility**: VERIFIED (saved=0.8296355579268745, fresh=0.8296355579268745)
- **te.faithful_units**: VERIFIED (saved=27225, fresh=27225)
- **te.tokens**: VERIFIED (saved=22993, fresh=22993)
- **te.fertility**: VERIFIED (saved=0.84455463728191, fresh=0.84455463728191)
- **bn.faithful_units**: VERIFIED (saved=68468, fresh=68468)
- **bn.tokens**: VERIFIED (saved=58100, fresh=58100)
- **bn.fertility**: VERIFIED (saved=0.8485715954898638, fresh=0.8485715954898638)
- **spread**: VERIFIED (saved=0.023313572613731792, fresh=0.023313572613731792)
- **raw_score**: VERIFIED (saved=42893.46882043277, fresh=42893.46882043277)
- **hindi_penalty**: VERIFIED (saved=1.0, fresh=1.0)
- **adjusted_score**: VERIFIED (saved=42893.46882043277, fresh=42893.46882043277)

## Fertility (fresh)

| Lang | SHA | Faithful units | Tokens | Fertility | Threshold |
| ---- | --- | -------------: | -----: | --------: | --------- |
| EN | `beefe609575008bc…` | 147908 | 126158 | 0.852949 | PASS |
| HI | `e7faf48f3010e942…` | 67473 | 55978 | 0.829636 | PASS |
| TE | `d0f5727be7ea9167…` | 27225 | 22993 | 0.844555 | — |
| BN | `be103ace9d5d2ada…` | 68468 | 58100 | 0.848572 | — |

## Round-trip

- Reviewer sample: PASS
- EN full corpus: PASS
- HI full corpus: PASS
- TE full corpus: PASS
- BN full corpus: PASS

## Risks (non-blocking)

- Rare Unicode symbols (€, @) fail isolated round-trip stress sample

## Vocabulary composition

| Category | Tokens | % |
| -------- | -----: | -: |
| Latin-dominant | 4113 | 41.1% |
| Devanagari-dominant | 1684 | 16.8% |
| Telugu-dominant | 1478 | 14.8% |
| Bengali-dominant | 1703 | 17.0% |
| Shared punctuation/digits/symbols | 895 | 8.9% |
| Mixed-script | 113 | 1.1% |
| Other Unicode | 13 | 0.1% |
| Special tokens | 1 | 0.0% |
| **Total** | **10000** | **100%** |
