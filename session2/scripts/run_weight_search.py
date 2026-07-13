#!/usr/bin/env python3
"""SamaBPE adaptive weight search → experiments registry → freeze winner."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.hf_bpe_trainer import evaluate_tokenizer, load_faithful_corpora, sha256_file, train_hf_bpe
from samabpe.weight_optimizer import (
    CandidateResult,
    WeightConfig,
    coarse_grid,
    neighbor_configs,
    pick_winner,
    pick_winner_constrained,
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "faithful"
CAND = ROOT / "results" / "resubmission" / "candidates"
REGISTRY = ROOT / "results" / "resubmission" / "experiments.json"
FINAL = ROOT / "results" / "resubmission" / "final"


def _train_and_measure(
    corpora: dict[str, str],
    weights: WeightConfig,
    experiment_id: str,
) -> CandidateResult:
    path = CAND / f"weights_{weights.key()}.json"
    if path.exists():
        from tokenizers import Tokenizer

        tok = Tokenizer.from_file(str(path))
    else:
        tok, _ = train_hf_bpe(corpora, weights=weights.as_dict(), output_path=path)
    ev = evaluate_tokenizer(tok, corpora)
    return CandidateResult(
        weights=weights,
        tokenizer_path=str(path.relative_to(ROOT)),
        vocab_size=tok.get_vocab_size(with_added_tokens=True),
        fertilities=ev["fertilities"],
        spread=ev["spread"],
        raw_score=ev["raw_score"],
        hindi_penalty=ev["hindi_penalty"],
        final_grade=ev["final_grade"],
        tokenizer_sha256=sha256_file(path),
        experiment_id=experiment_id,
    )


def main() -> int:
    if not (CORPUS / "en.faithful.md").exists():
        print("Run scripts/build_wiki_faithful_markdown.py first")
        return 1
    CAND.mkdir(parents=True, exist_ok=True)
    corpora = load_faithful_corpora(CORPUS)
    candidates: list[CandidateResult] = []

    print("Phase A — coarse weight search…")
    for i, w in enumerate(coarse_grid(), start=1):
        c = _train_and_measure(corpora, w, f"hf-weight-{i:03d}")
        candidates.append(c)
        if i % 25 == 0:
            best = max(candidates, key=lambda x: x.final_grade)
            print(f"  {i} configs… best grade {best.final_grade:.2f}")

    candidates.sort(key=lambda c: c.final_grade, reverse=True)
    top = candidates[:8]
    print("Phase B — adaptive neighbors…")
    seen = {c.weights.key() for c in candidates}
    n_id = len(candidates) + 1
    for base in top[:5]:
        for w in neighbor_configs(base.weights):
            if w.key() in seen:
                continue
            seen.add(w.key())
            candidates.append(_train_and_measure(corpora, w, f"hf-weight-{n_id:03d}"))
            n_id += 1

    winner, selection = pick_winner_constrained(candidates)
    records = [c.to_experiment_record() for c in sorted(candidates, key=lambda x: x.final_grade, reverse=True)]
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "objective": "final_grade",
                "experiments": records,
                "winner_experiment_id": winner.experiment_id,
                "winner_selection": selection,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    FINAL.mkdir(parents=True, exist_ok=True)
    src = ROOT / winner.tokenizer_path
    dst = FINAL / "tokenizer.json"
    dst.write_bytes(src.read_bytes())
    subprocess.check_call(
        [
            sys.executable,
            str(ROOT / "scripts" / "evaluate_hf_tokenizer.py"),
            "--tokenizer",
            str(dst),
            "--corpus-dir",
            str(CORPUS),
            "--output",
            str(FINAL / "metrics.json"),
        ]
    )
    provenance = {
        "strategy": "adaptive-weight-search",
        "weights": winner.weights.as_dict(),
        "tokenizer_sha256": sha256_file(dst),
        "corpus_sha256": {
            lang: json.loads((CORPUS / f"{lang}.meta.json").read_text(encoding="utf-8")).get("sha256")
            or json.loads((CORPUS / f"{lang}.meta.json").read_text(encoding="utf-8")).get("sha256_md")
            for lang in ("en", "hi", "te", "bn")
            if (CORPUS / f"{lang}.meta.json").exists()
        },
        "experiment_id": winner.experiment_id,
        "evaluation_command": "python scripts/evaluate_hf_tokenizer.py --tokenizer results/resubmission/final/tokenizer.json --corpus-dir data/faithful --output results/resubmission/final/metrics.json",
        "training_command": "python scripts/run_weight_search.py",
    }
    try:
        provenance["git_commit"] = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        )
    except Exception:
        provenance["git_commit"] = "unknown"
    (FINAL / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")

    print(f"\nWinner {winner.experiment_id} weights={winner.weights.as_dict()}")
    print(f"  final_grade={winner.final_grade:.4f} raw={winner.raw_score:.4f} penalty={winner.hindi_penalty:.4f}")
    print(f"  → {FINAL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
