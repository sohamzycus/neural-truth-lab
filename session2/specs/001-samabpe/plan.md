# SamaBPE Implementation Plan

> **Goal:** Production-quality fair BPE tokenizer lab with verified metrics and static React UI.

**Architecture:** Python pipeline (corpus → train → verify → JSON artefacts) + Vite React dashboard reading artefacts only.

**Tech Stack:** Python 3.11, regex, React 19, Vite 6, Tailwind 4, Recharts

---

## Tasks

- [x] Scaffold repo, constitution, spec
- [x] Word units + BPE core + tests (TDD)
- [x] Corpus fetch/freeze with SHA-256
- [x] Five strategies + verification script
- [x] Training pipeline + artefact export
- [x] React UI (all sections)
- [x] Netlify static build
- [ ] Final verification + production bundle
