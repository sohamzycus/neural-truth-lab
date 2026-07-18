---
description: AI code review with Alibaba open-code-review (ocr) — workspace, branch, commit, or Bitbucket PR. Read-only unless user asks to fix.
---

## User Input

```text
$ARGUMENTS
```

Invoke the **open-code-review** skill (`.cursor/skills/open-code-review/SKILL.md`).

## Outline

1. **Prerequisites** — `npx ocr version` and `npx ocr llm test`. If LLM test fails, stop and point user to `env/ocr.example` (never hardcode keys).
2. **Scope** — parse `$ARGUMENTS`:
   - Empty → workspace (`npx ocr review --audience agent`)
   - `main`, `vs main`, branch name → `--from main --to HEAD` (or named refs)
   - commit SHA → `--commit <sha>`
   - Bitbucket PR URL/id → `git fetch origin pull-requests/<id>/from:bb-pr-<id>` then `--from origin/<base> --to bb-pr-<id>` (base default `main`)
   - `preview` → `--preview` only (no LLM)
   - `fix` / `review and fix` → after report, apply High/Medium fixes with user confirmation
3. **Background** — pass `-b "…"` from PR title, branch, or user context.
4. **Run** — `npx ocr review --audience agent …` from repo root. Timeout 10 min per file (OCR default).
5. **Report** — classify comments (High/Medium; drop Low). Use the skill output template.
6. **Fixes** — only if user requested fix intent; verify with `npm run lint:check` / `npm run ts:check` on touched files when applicable.

**Do not** replace `/speckit.review-pr` (Code Oracle + Bitbucket context) — OCR complements it with LLM line-level review.
