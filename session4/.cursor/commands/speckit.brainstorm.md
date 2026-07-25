---
description: "Explore solution space before formal specification — options, risks, dependencies — and capture brainstorm.md for /speckit.specify."
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --paths-only
  ps: scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly
user-invocable: true
disable-model-invocation: true
---

<!-- Canonical path: `.specify/extensions/fleet/commands/brainstorm.md` — keep in sync. -->

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). Treat it as **feature context**: Jira key (e.g. `DCRF-3041`), free-text idea, paste from Jira, or supplemental notes. Parse **`JIRA_ISSUE_KEY`** and **`FEATURE_DESCRIPTION`** the same way as `/speckit.fleet` (Jira-style key first, remainder as description).

<!-- AI-GENERATED START: Superpowers integration -->
## Superpowers (Cursor)

Before executing this command, **invoke** the Superpowers skills for phase `brainstorm` from merged `.specify/extensions/fleet/fleet-config.yml` → `superpowers.skills_by_phase_id.brainstorm` (see `.specify/memory/superpowers-fleet.md`). **Minimum:** `using-superpowers`, then `brainstorming`. This command **is** the SpecKit Brainstorm phase; follow the **brainstorming** skill for exploration depth — do not duplicate a second unstructured brainstorm elsewhere.
<!-- AI-GENERATED END: Superpowers integration -->

---

You are the **SpecKit Brainstorm** agent. Produce a structured **exploration** document (`brainstorm.md`) that **informs** `/speckit.specify` — not a formal spec. Focus on problem framing, options, trade-offs, risks, and cross-stack touchpoints (React UI in **this** repo, Adapter, Java service — siblings read-only).

### Operating constraints

1. **Fleet handoff**: When invoked by the fleet orchestrator, do **not** chain to other agents; return output and stop.
2. **Workspace**: Write files **only** under **merlin-assist-zycuschat**’s `specs/` tree for this feature (this SpecKit UI workspace).
3. **Full-stack context**: Read `.specify/extensions/fleet/fleet-config.yml` (merge `fleet-config.local.yml` if present) for `reference_repos` paths and labels (`java_service`, `adapter`).

---

## Outline

1. **Resolve `FEATURE_DIR`**
   - Run `{SCRIPT}` from the repository root and parse JSON for `FEATURE_DIR` / `BRANCH` / `SPEC_FILE` as applicable.
   - If **no** feature directory (script fails or empty): run **create-new-feature** the same way as `/speckit.specify`:
     - `bash`: `.specify/scripts/bash/create-new-feature.sh --json --short-name "<slug>" --number N "<FEATURE_DESCRIPTION>"` (or let the script pick `--number` from repo state).
     - Use a sensible **short name** (2–4 words) from the feature description or Jira summary.
     - Parse JSON for `BRANCH_NAME`, `SPEC_FILE` → derive `FEATURE_DIR` as the parent of `spec.md` / `SPEC_FILE`.
   - If the branch and `spec.md` already exist (e.g. after a prior run), **do not** create a second branch — only add or update `brainstorm.md`.

2. **Optional Jira enrichment**  
   If **`JIRA_ISSUE_KEY`** is set and Atlassian MCP (or equivalent) is available, fetch summary/description to enrich context.

3. **Write `{FEATURE_DIR}/brainstorm.md`** with at least:
   - **Title** — working feature title (can differ from final spec name).
   - **Context** — problem, trigger, who cares (1–3 short paragraphs).
   - **Goals / non-goals** — bullet lists.
   - **Stakeholders & actors** — roles, systems.
   - **Solution options** — **at least three** distinct approaches (including “do nothing” or “manual process” if relevant); for each: summary, pros, cons, fit for this tenant/product.
   - **Risks & assumptions** — technical, UX, compliance, rollout.
   - **Cross-stack notes** — how React UI (this repo), Adapter, and Java service might be involved (read-only `local_path` from fleet config for siblings); call out what must stay in **this** repo vs **merlinassist-zycuschat-service-app** / **merlin-assist-adapter**.
   - **Open questions** — ranked; note which block `/speckit.specify` vs which can wait for clarify/plan.
   - **Recommendation** — which option to pursue first and what the formal spec should stress.
   - **Traceability** (if Jira): `JIRA_ISSUE_KEY`, Epic/Story note if known.

4. **Do not** fully replace `spec.md`. Leave template placeholders for `/speckit.specify` unless the user explicitly asked to skip brainstorming later.

5. **Report** — paths to `brainstorm.md`, branch name, and a one-paragraph summary. Tell the user the next step is **`/speckit.specify`** (or fleet Phase 1) so the spec is generated **using** `brainstorm.md` as input.

---

## When invoked from `/speckit.fleet` (Phase 0)

Prepend to your reasoning: *"You are being invoked by the fleet orchestrator. Do NOT follow handoffs or auto-forward to other agents. Return your output to the orchestrator and stop."*

After writing `brainstorm.md`, stop and return; the orchestrator runs the human gate before Phase 1 (Specify).
