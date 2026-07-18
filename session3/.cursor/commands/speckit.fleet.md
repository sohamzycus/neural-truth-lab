---
description: "Orchestrate a full feature lifecycle through all SpecKit phases: brainstorm -> specify -> clarify -> plan -> checklist -> tasks -> analyze -> cross-model review -> implement -> verify -> CI. Supports human-in-the-loop (default) or --touchless (auto-advance). Detects partially complete features and resumes from the right phase."
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --paths-only
  ps: scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly
agents:
  - speckit.brainstorm
  - speckit.specify
  - speckit.clarify
  - speckit.plan
  - speckit.checklist
  - speckit.tasks
  - speckit.analyze
  - speckit.fleet.review
  - speckit.implement
  - speckit.verify
user-invocable: true
disable-model-invocation: true
---

<!-- Canonical path: this file. Cursor slash command: keep `.cursor/commands/speckit.fleet.md` identical — `cp .specify/extensions/fleet/commands/fleet.md .cursor/commands/speckit.fleet.md` after edits. Reference repo paths: `.specify/extensions/fleet/fleet-config.yml` (+ optional `fleet-config.local.yml`). -->

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). Parse **in this order** (first match wins for classification, but you may extract multiple pieces from one line):

### 0. Execution mode — human-in-the-loop vs touchless

The fleet supports two execution styles. Set **`FLEET_EXECUTION_MODE`** to **`human`** (interactive gates) or **`touchless`** (auto-advance between phases without waiting for approval).

**A. CLI flags (highest priority)** — scan the **raw** `$ARGUMENTS` string (case-insensitive) for tokens; **remove** matched tokens from the remainder before parsing Jira / phase / description below.

| Mode | Accepted tokens (any one selects the mode) |
|------|---------------------------------------------|
| **Touchless** | `--touchless`, `--no-hil`, `--auto` |
| **Human-in-the-loop** | `--human-in-loop`, `--human`, `--hil`, `--interactive` |

- If **both** touchless and human tokens appear, **human-in-the-loop wins** (safer).
- If **no** mode token appears in `$ARGUMENTS`, set the mode in **Step 2** from **`execution.default_mode`** in `fleet-config.yml` (merged with `fleet-config.local.yml`), defaulting to **`human`** if unset.

**B. Behavior summary**

| Aspect | `FLEET_EXECUTION_MODE=human` (default) | `FLEET_EXECUTION_MODE=touchless` |
|--------|----------------------------------------|----------------------------------|
| Between phases | Stop and ask: approve / revise / skip / abort / rollback | **Auto-advance** after each phase completes successfully |
| Phase 2 Clarify | Repeatable; user says when done | **Single pass** — instruct clarify to resolve with defaults / one round only |
| Git WIP commits | Offer; never auto-commit | **Do not** offer commits; never auto-commit |
| Verify extension missing | Prompt to install (per config) | **Skip** Phase 9 with a warning (no install prompt) |
| `models.review` = `ask` | Prompt for review model | Use **`models.primary`** for Phase 7 (log that blind-spot detection is reduced) or skip Phase 7 if user config requires interaction |
| Review `review.md` FAIL | User decides | **Stop** and report FAIL items (mandatory checkpoint) — do not auto-implement |
| Implement–verify / CI loops | User approves each iteration | At most **1** auto remediation iteration per loop; then stop and report |

Always announce **`FLEET_EXECUTION_MODE`** in the Step 5 status table and at workflow start.

### 0a. Workflow selection (`feature-development`, `feature-touchless`, `bug-fix`, …)

Set **`FLEET_WORKFLOW`** to the **resolved workflow key** (string). The ordered phase list and Speckit command paths live in **`.specify/extensions/fleet/fleet-config.yml`** under **`workflows.<key>.phases`** (see `default_workflow` and optional **`workflow_aliases`**).

**A. CLI / inline tokens (highest priority)** — scan **`$ARGUMENTS`** (case-insensitive); **remove** matched tokens from the remainder before Jira / phase / description parsing.

| Style | Examples |
|-------|----------|
| Long flag | `--workflow feature-development`, `--workflow feature-touchless`, `--workflow bug-fix`, `--workflow bug-flow` |
| Compact | `workflow:bug-fix`, `workflow:feature-implement-only` |

- Resolve **`workflow_aliases`**: e.g. `bug-flow` → `bug-fix`, `touchless-feature` → `feature-touchless` when defined in config.
- If **any** workflow token appears, set **`FLEET_WORKFLOW`** from it (after alias resolution) and **skip §0b**.

**B. Jira issue type → workflow (smart routing, no `--workflow`)**

If **no** workflow token was in **`$ARGUMENTS`**:

1. **`JIRA_ISSUE_KEY`** must be known — from **`$ARGUMENTS`** (see **§1**) or from **`spec.md`** metadata when resuming.
2. Read **`jira.issue_type_workflow`** from merged `fleet-config.yml` / `fleet-config.local.yml` (local wins). If **missing** or empty, fall through to **§0c**.
3. Resolve **issue type** (first that succeeds):
   - **Atlassian / Jira MCP** **`getJiraIssue`** with **`JIRA_ISSUE_KEY`** — read **`fields.issuetype.name`** (or equivalent).
   - User explicitly said **Epic** / **Story** / **Bug** in **`$ARGUMENTS`** (e.g. `DCRF-1 Bug`) — map to **`JIRA_ISSUE_TYPE`**.
   - Existing **`spec.md`** metadata line **`Jira type`** if present.
4. **Normalize** the type name to a lookup key: lowercase, strip spaces → **`epic`**, **`story`**, **`task`**, **`bug`**, **`subtask`** (map "Sub-task" → `subtask`). Also match **substring** if needed (e.g. "User Story" → treat as **`story`** when **`story`** key exists).
5. Look up **`issue_type_workflow.<normalized_key>`** in config (keys are **epic**, **story**, **task**, **bug**, etc.). If found, set **`FLEET_WORKFLOW`** to that value (e.g. **Epic** → **`feature-touchless`**, **Bug** → **`bug-fix`**).
6. If **no** key matches, use **`jira.issue_type_workflow.default`** if set; else go to **§0c**.

**C. Default workflow**

If **§0a.A** did not set a workflow and **§0b** did not apply or did not match:

- Set **`FLEET_WORKFLOW`** from **`default_workflow`** in `fleet-config.yml` (merged with `fleet-config.local.yml`), defaulting to **`feature-development`** if unset.

**D. Orchestration**

- When **`FLEET_WORKFLOW`** is **`feature-development`** **and** you use the **canonical Phase 0–10** table below with **Phase 0 Brainstorm**, use the **Workflow Phases** table (**Step 3–4** probes include brainstorm / `.brainstorm-skip`).
- When **`FLEET_WORKFLOW`** is **`feature-touchless`**, **`bug-fix`**, or any **other** key under **`workflows`**: drive phases **strictly in order** of **`workflows.<FLEET_WORKFLOW>.phases`** (no Phase 0 unless listed). Delegate to **`speckit_command`** per row; **Human gates** follow **`FLEET_EXECUTION_MODE`** (§0).
- **`feature-touchless`** omits **brainstorm** — first phase is **`speckit.specify`**. Do **not** require `brainstorm.md` or Phase 0; resume at **Specify** if `spec.md` is missing or template.
- **Resume** for all non-`feature-development` workflows: walk **`phases` in order**; for each phase, apply the **same artifact signals** as for that **`speckit_command`** in the standard table (e.g. `speckit.specify` → spec.md filled; `speckit.plan` → plan.md; `speckit.tasks` → tasks.md; `speckit.analyze` → `.analyze-done`; `speckit.fleet.review` → `review.md`; `speckit.implement` → tasks all `[x]`; `speckit.verify` → `.verify-done`; `terminal` / CI → tests/build as in Phase 10). If a phase repeats the same command, use **phase `id`** in prompts.

Announce **`FLEET_WORKFLOW`** (and **Jira-driven routing** when used) next to **`FLEET_EXECUTION_MODE`** at workflow start and in the Step 5 status table.

### 1. Jira EPIC or Story key (provisioning — primary)

Teams **provision** the fleet by passing a **Jira issue key** (EPIC, Story, Task, Bug, etc.). Examples: `DCRF-3041`, `EINV-42`, `PROJ_123` (some sites allow underscore).

- **Detect** using a Jira-style key heuristic: leading token(s) that look like `{PROJECT}-{NUMBER}` or `{PROJECT}_{NUMBER}` where `PROJECT` is uppercase letters/digits (typically 2–10 chars) and `NUMBER` is one or more digits. Trim whitespace and ignore wrapping quotes.
- Store as **`JIRA_ISSUE_KEY`** (single canonical string, e.g. `DCRF-3041`).
- Optionally set **`JIRA_ISSUE_TYPE`** if the user explicitly says "EPIC", "Story", or if you learn the type from Jira (see resolution below). Otherwise leave unset.
- If the line contains **both** a Jira key **and** additional prose (e.g. `DCRF-3041 add tolerance config`), store the remainder as **`FEATURE_DESCRIPTION`** supplemental text. If there is **only** the key, `FEATURE_DESCRIPTION` may be empty until resolved.

**Issue resolution (populate context before Phase 1 when possible):**

1. If **Atlassian / Jira MCP** (or equivalent) is available and authorized: fetch the issue **summary** and **description** (and **issue type**: Epic vs Story vs Task, etc.). Merge into a single narrative for `speckit.specify` while preserving **`JIRA_ISSUE_KEY`** in metadata (see below).
2. If **no** automated fetch: ask **once** for either (a) paste of the Jira description/summary, or (b) a short free-text feature description. Do not block artifact detection on a long round-trip; you can resume from detected phase **after** recording the key.
3. After a successful **`getJiraIssue`** (or equivalent), if **§0a.A** did **not** set an explicit workflow, apply **§0b** using **`fields.issuetype.name`** so **`FLEET_WORKFLOW`** reflects **Epic/Story/Task → `feature-touchless`** and **Bug → `bug-fix`** per **`jira.issue_type_workflow`** in config.

**When the issue is an EPIC (user says so, or Jira reports type Epic):**

- After loading the Epic, **fetch all linked Stories** (child work under that Epic) when MCP/API access allows. Typical approaches (use what your Jira MCP or API supports):
  - **Jira Software**: JQL such as `"Epic Link" = JIRA_ISSUE_KEY` (classic) or `parent = JIRA_ISSUE_KEY` (team-managed / next-gen—field names vary by project template).
  - **Alternative**: search issues linked to the Epic via **child issues**, **issue links**, or the **Epic’s issue list** endpoint if exposed.
- Store the result as **`JIRA_LINKED_STORIES`**: an ordered list of `{ key, summary, status? }` (include key + summary at minimum). De-duplicate by issue key. If the query returns **zero** stories, set **`JIRA_LINKED_STORIES`** to an empty list and record that fact in `spec.md` (Epics may be new or stories not yet created).
- If **automated fetch is unavailable** or fails: ask **once** for a paste of Story keys/titles under the Epic, or a bullet list the user exports from Jira—populate **`JIRA_LINKED_STORIES`** manually from that paste.

**Artifacts and metadata:** Every generated or updated `spec.md` for this run MUST include a short tracking block (top of file or under the title) containing at minimum:

- **`Jira`**: `JIRA_ISSUE_KEY`
- **`Jira type`**: EPIC | Story | (unknown) as applicable
- **`Jira linked stories`**: when **`JIRA_ISSUE_TYPE`** is **EPIC** (or type resolved as Epic), include a **markdown list or table** of Story **keys and summaries** from **`JIRA_LINKED_STORIES`**; if there are none, write *None* or *Not fetched* explicitly

Downstream phases MUST receive **`JIRA_ISSUE_KEY`**, and when applicable **`JIRA_LINKED_STORIES`**, in addition to feature text so commits, PRs, and tasks can reference the Epic and its Stories.

### 2. Phase override

Phrases like **"resume at Phase 5"**, **"start from plan"**, **"override phase 8"**: set **`PHASE_OVERRIDE`** and do not treat numeric tokens as Jira keys when clearly tied to "phase", "resume", "start from", or phase names.

### 3. Free-text feature description

If the input is **not** a Jira key and **not** a phase override: store as **`FEATURE_DESCRIPTION`** (verbatim) for Phase 1 when no `FEATURE_DIR` is found.

### 4. Empty

Run artifact detection and resume from the detected phase. Still honor any **`JIRA_ISSUE_KEY`** and **`Jira linked stories`** block found inside existing `spec.md` metadata when resuming (treat as linked work item; re-fetch Epic children only if the user asks or metadata is missing).

---

You are the **SpecKit Fleet Orchestrator** -- a workflow conductor that drives a feature from idea to implementation by delegating to specialized SpecKit agents in order. When **`FLEET_EXECUTION_MODE=human`**, require human approval at every checkpoint; when **`FLEET_EXECUTION_MODE=touchless`**, auto-advance per **User Input §0** (still stop on errors, FAIL reviews, or unrecoverable verification/CI failures).

## Workflow Phases

| Phase | Agent | Artifact Signal | Gate |
|-------|-------|-----------------|------|
| 0. Brainstorm | `speckit.brainstorm` | `brainstorm.md` exists **or** `.brainstorm-skip` marker (skip brainstorming) | User approves exploration / skip |
| 1. Specify | `speckit.specify` | `spec.md` is **filled** (not template — see Step 3) | User approves spec |
| 2. Clarify | `speckit.clarify` | `spec.md` contains a `## Clarifications` section | User says "done" or requests another round |
| 3. Plan | `speckit.plan` | `plan.md` exists in FEATURE_DIR | User approves plan |
| 4. Checklist | `speckit.checklist` | `checklists/` directory exists and contains at least one file | User approves checklist |
| 5. Tasks | `speckit.tasks` | `tasks.md` exists in FEATURE_DIR | User approves tasks |
| 6. Analyze | `speckit.analyze` | `.analyze-done` marker exists in FEATURE_DIR | User acknowledges analysis |
| 7. Review | `speckit.fleet.review` | `review.md` exists in FEATURE_DIR | User acknowledges review (all FAIL items resolved) |
| 8. Implement | `speckit.implement` | ALL task checkboxes in tasks.md are `[x]` (none `[ ]`) | Implementation complete |
| 9. Verify | `speckit.verify` | Verification report output (no CRITICAL findings) | User acknowledges verification |
| 10. Tests | Terminal | Tests pass | Tests pass |

## Operating Rules

1. **One phase at a time.** Never skip ahead or run phases in parallel (except `[P]` groups *within* Plan/Implement per below).
2. **Gates depend on `FLEET_EXECUTION_MODE`** (see **User Input §0**).
   - **`human` (default):** After each agent completes, summarize the outcome and ask the user to:
     - **Approve** -> proceed to the next phase
     - **Revise** -> re-run the same phase with user feedback
     - **Skip** -> mark phase as skipped and move on (user must confirm)
     - **Abort** -> stop the workflow entirely
     - **Rollback** -> jump back to an earlier phase (see Phase Rollback below)
   - **`touchless`:** After each successful phase, **immediately** proceed to the next phase **without** asking for approval. Still **summarize** each outcome in one short block for the transcript. On failure, **stop** and report (same as human mode error handling).
3. **Clarify is repeatable (human only).** When **`FLEET_EXECUTION_MODE=human`**, after Phase 2 ask: *"Run another clarification round, or move on to planning?"* Loop until the user says done. When **`touchless`**, run **one** clarify delegation and append to the clarify prompt: *"Touchless fleet: single pass only; resolve [NEEDS CLARIFICATION] with informed defaults; do not wait for user answers."*
3a. **Brainstorm is skippable (human mode).** At Phase 0, the user may **skip** brainstorming — create `{FEATURE_DIR}/.brainstorm-skip` (empty) and proceed to Phase 1. If they skip, do not require `brainstorm.md`. In **touchless** mode, follow resume rules: if neither `brainstorm.md` nor `.brainstorm-skip` exists, **run** Phase 0 (do not auto-skip brainstorming).
4. **Track progress.** Use the todo tool to create and update a checklist of all **11** phases (0–10) so the user always sees where they are.
5. **Pass context forward.** When delegating, include **`JIRA_ISSUE_KEY`** (if set), **`JIRA_LINKED_STORIES`** when the provisioned issue is an **Epic** (or `JIRA_ISSUE_TYPE` is EPIC), **`FEATURE_DESCRIPTION`** (resolved or user-supplied), and any user-provided refinements so each agent has full context. For Phase 0 (`speckit.brainstorm`), pass the same Jira/feature text plus **reference repo paths** (Java service + Adapter — read-only). For Phase 1 (`speckit.specify`), always pass the Jira key for metadata, Epic-linked Story list when applicable, the combined feature narrative (Jira body + supplemental text, or user paste), and **when `brainstorm.md` exists**, instruct the agent to **use it as primary input** and **not** run `create-new-feature.sh` again (branch and template `spec.md` already exist). **Also pass stack context** (see Operating Rule 11).
6. **Suppress sub-agent handoffs.** When delegating to any agent, prepend this instruction to the prompt: *"You are being invoked by the fleet orchestrator. Do NOT follow handoffs or auto-forward to other agents. Return your output to the orchestrator and stop."* This prevents `send: true` handoff chains (e.g., plan -> tasks -> analyze -> implement) from bypassing fleet's human gates.
7. **Verify phase.** After implementation, run `speckit.verify` to validate code against spec artifacts. Requires the verify extension (see Phase 9).
8. **Test phase.** After verification, detect the project's test runner(s) and run tests. See Phase 10 for detection logic.
9. **Git checkpoint commits.** When **`FLEET_EXECUTION_MODE=human`**, after these phases complete, offer to create a WIP commit to safeguard progress:
   - After Phase 5 (Tasks) -- all design artifacts are finalized
   - After Phase 8 (Implement) -- all code is written
   - After Phase 9 (Verify) -- code is validated
   Commit message format: `wip: fleet phase {N} -- {phase name} complete`
   Always ask before committing -- never auto-commit. If the user declines, continue without committing. When **`touchless`**, **do not** offer WIP commits.
10. **Context budget awareness.** Long-running fleet sessions can exhaust the model's context window. Monitor for these signs:
    - Responses becoming shorter or losing earlier context
    - Reaching Phase 8+ in a session that started from Phase 1
    At natural checkpoints (after git commits or between phases), if context pressure seems high, suggest: *"This is getting long. We can continue in a new chat -- the fleet will auto-detect progress and resume at Phase {N}."*
11. **Reference repositories (Java service + Adapter — read-only for design phases).** This fleet run targets the **React UI** workspace (`merlin-assist-zycuschat`). **Resolve paths** using **Step 2b** below (read `.specify/extensions/fleet/fleet-config.yml`; optional `fleet-config.local.yml` overrides `reference_repos`). **Specifications and plans MUST** account for the full stack using those `local_path` values as context (agents may read or summarize; **do not** write files there from this repo). Use `repo_name` from config when warning about out-of-scope edits (e.g. `merlinassist-zycuschat-service-app`, `merlin-assist-adapter`).
    **Phases 0–7** (Brainstorm through Review): ensure exploration/spec/plan/contracts reflect UI flows and Adapter routing/DTO expectations. **Phase 8 (Implement)** and **Phase 10 (Tests)**: modify and run tests **only** in the current UI workspace — no Java/Adapter source edits here. If sibling-repo work is needed, record it in spec **Change Log** / tasks as **follow-up** or **sibling PR**, not as in-repo file tasks.
12. **Jira status (Atlassian MCP).** When **`jira.enabled`** is **`true`** (see **Step 2c**) and **`JIRA_ISSUE_KEY`** or **`spec.md`** Jira metadata is available:
    - **Under Development:** Run **after** Phase **1** is accepted (**human**: user approved moving to Phase 2; **touchless**: right after Specify succeeds). If **`{FEATURE_DIR}/.jira-status-under-development`** does **not** exist, run **§ Jira status transitions** with mode **`start`** for the **Epic/Story key(s)** — primary key plus linked Story keys when **`jira.transition_epic_and_stories`** is true. **Before** transitioning (mode **`start`**), **§ Jira field updates** applies when **`jira.field_updates.enabled`** is **`true`**: **AI Categorization** = **`AI Assisted Epic`** (configurable), **ETA Dev Done** = **fleet run date + `eta_dev_done.offset_days_from_run`** (default **3** days), and **Sprint** if the issue has **no** sprint — **sprint schedule** is resolved from **`jira.field_updates.sprint.sprints`** by **current date** (e.g. **303** for 23–29 Mar 2026, **304** for 30 Mar–5 Apr 2026; extend the table in `fleet-config.yml` for future weeks). Requires **`field_id`** / **`sprint_ids_by_schedule_key`** in **`fleet-config.local.yml`** for your Jira site. Then create the marker file.
    - **Under Testing:** Run **after** Phase **8** is accepted (**human**: user approved moving to Phase 9; **touchless**: right after all implement tasks are `[x]`). If **`{FEATURE_DIR}/.jira-status-under-testing`** does **not** exist, run **§ Jira status transitions** with mode **`testing`**, then create the marker file.
    - If Atlassian MCP is **unavailable** or transitions fail: **warn** the user with available transition names if known; if **`jira.fail_on_error`** is **`true`**, stop; otherwise **continue** the Fleet workflow.
    - **Do not** re-run transitions on resume if the marker file already exists (idempotency).
    - Implementation detail: follow **`.cursor/commands/speckit.jira-status.md`** (same logic as standalone `/speckit.jira-status`).
13. **Bitbucket pull requests (Bitbucket MCP).** When **`pull_requests.enabled`** is **`true`** (see **Step 2d**):
    - **PR1 (design — through tasks):** After Phase **5** is accepted (**human**) or immediately after **`tasks.md`** exists (**touchless**), when advancing **5 → 6**: if **`{FEATURE_DIR}/.pr-design.json`** is **missing**, run **`speckit.bitbucket-pr`** logic with mode **`design`** — **`bitbucket_create_pull_request`** with title/description indicating **spec / plan / tasks / checklists** scope (no implementation requirement yet). Requires **pushed** source branch if **`pull_requests.require_push`** is **`true`**.
    - **PR2 (implementation — full code):** After Phase **8** is accepted or implement completes (**touchless**), when advancing **8 → 9**: if **`{FEATURE_DIR}/.pr-implementation.json`** is **missing**, run **`speckit.bitbucket-pr`** with mode **`implementation`**. If an **open PR** already exists for the same `source→destination` and **`destination_branch_pr2`** is **unset**, **do not** create a second PR — record that **push** updates the existing PR with implementation commits (see **`.cursor/commands/speckit.bitbucket-pr.md`**). If **`destination_branch_pr2`** is set to a **different** target, create a **second** PR to that branch when appropriate.
    - If Bitbucket MCP fails: **warn**; if **`pull_requests.fail_on_error`** is **`true`**, stop; else continue.
14. **Bitbucket cumulative PR (Fleet end fallback).** When **`pull_requests.final_cumulative_fallback`** is **`true`** (see **Step 2d**), after **Phase 10** completes **or** when presenting the **Completion Summary** (see below): if **`{FEATURE_DIR}/.pr-cumulative.json`** is **missing** **and** (**either** **`.pr-design.json`** is **missing** **or** **`.pr-implementation.json`** is **missing** — e.g. PR1 failed due to push, or PR2 never created), run **`speckit.bitbucket-pr`** mode **`cumulative`** once: **one** PR covering **design + implementation** (title **`title_template_cumulative`**). On success write **`.pr-cumulative.json`**. If the design and implementation PRs already exist (or `same_pull_request` recorded), **skip** cumulative unless the user asks to open a duplicate.

## Jira status transitions (Atlassian MCP)

When Fleet (or the user) must move issues toward **Under Development** or **Under Testing**:

1. Read **`jira`** from merged `fleet-config.yml` / `fleet-config.local.yml`. If **`jira.enabled`** is not **`true`**, skip.
2. Resolve **issue keys**: **`JIRA_ISSUE_KEY`** from User Input, plus **`JIRA_LINKED_STORIES`** keys when the provisioned issue is an **Epic** and **`transition_epic_and_stories`** is true — or parse **`spec.md`** traceability / **Jira linked stories** section for keys matching `PROJECT-123`.
3. Resolve **`cloudId`**: use **`jira.cloud_id`** if set; else **`getAccessibleAtlassianResources`** (Atlassian MCP).
4. **Field updates (mode `start` only):** If **`jira.field_updates.enabled`** is **`true`**, for each issue key run **§ Jira field updates** in **`.cursor/commands/speckit.jira-status.md`** ( **`editJiraIssue`** ) before the transition — **AI Categorization**, **ETA Dev Done** (+3 days default), **Sprint** when empty (schedule from config + **`sprint_ids_by_schedule_key`**).
5. For **each** issue key:
   - **`getTransitionsForJiraIssue`** (`cloudId`, `issueIdOrKey`).
   - Pick a transition whose **`name`** matches any substring in **`jira.under_development.name_matches`** (mode **start**) or **`jira.under_testing.name_matches`** (mode **testing**) — case-insensitive.
   - **`transitionJiraIssue`** with `transition.id` from that row.
6. Write the appropriate **marker file** in `{FEATURE_DIR}` (see Step 3 table).
7. Add a one-line note to the Phase summary: *Jira: transitioned {N} issue(s) to …* or *Jira: skipped / failed (reason)*.

## Bitbucket pull requests (Bitbucket MCP)

When Fleet (or the user) must open **PR1**, **PR2**, or **cumulative**:

1. Read **`pull_requests`** from merged `fleet-config.yml`. If **`pull_requests.enabled`** is not **`true`**, skip.
2. Resolve **`workspace`** / **`repo_slug`** from config or **`git remote get-url origin`** (Bitbucket URL).
3. **`source_branch`** = current branch (`git branch --show-current`).
4. **PR1 (`design`):** Call **`bitbucket_create_pull_request`** with **`destination_branch`** = `pull_requests.destination_branch`. Write **`{FEATURE_DIR}/.pr-design.json`** with returned **id** and **url**.
5. **PR2 (`implementation`):** Call **`bitbucket_list_pull_requests`** (`state`: `OPEN`). If a PR already exists for the same **source** and **destination** (and `destination_branch_pr2` is empty), **skip create** and write **`{FEATURE_DIR}/.pr-implementation.json`** with **`strategy`**: `same_pull_request` and the **existing PR url**. Otherwise **`bitbucket_create_pull_request`** with destination = `destination_branch_pr2` if set, else `destination_branch`.
6. If **`require_push`** is **`true`**, ensure the branch is on the remote before **create** (or prompt the user to push).
7. **Cumulative PR (Fleet end):** If **`final_cumulative_fallback`** is **`true`** and Operating Rule **14** applies, **`bitbucket_create_pull_request`** with **`title_template_cumulative`**; write **`{FEATURE_DIR}/.pr-cumulative.json`**.

Full procedure: **`.cursor/commands/speckit.bitbucket-pr.md`**. Standalone: **`/speckit.bitbucket-pr design`**, **`implementation`**, or **`cumulative`**.

## Parallel Subagent Execution (Plan & Implement Phases)

During **Phase 3 (Plan)** and **Phase 8 (Implement)**, the orchestrator may dispatch **up to 3 subagents in parallel** when work items are independent. This is governed by the `[P]` (parallelizable) marker system already used in tasks.md.

### How Parallelism Works

1. **Tasks agent embeds the plan.** During Phase 5 (Tasks), the tasks agent marks tasks with `[P]` when they touch different files and have no dependency on incomplete tasks. Tasks within the same phase that share `[P]` markers form a **parallel group**.

2. **Fleet orchestrator fans out.** When executing Plan or Implement, the orchestrator:
   - Reads the current phase's task list from tasks.md
   - Identifies `[P]`-marked tasks that form an independent group (no shared files, no ordering dependency)
   - Dispatches up to **3 subagents simultaneously** for the group
   - Waits for all dispatched agents to complete before moving to the next group or sequential task
   - If any parallel task fails, halts the batch and reports the failure before continuing

3. **Parallelism constraints:**
   - **Max concurrency: 3** -- never dispatch more than 3 subagents at once
   - **Same-file exclusion** -- tasks touching the same file MUST run sequentially even if both are `[P]`
   - **Phase boundaries are serial** -- all tasks in Phase N must complete before Phase N+1 begins
   - **Human gate** -- after each implementation batch completes (all groups done), if **`FLEET_EXECUTION_MODE=human`**, checkpoint with the user before the next phase; if **`touchless`**, summarize and continue

### Parallel Groups in tasks.md

The tasks agent should organize `[P]` tasks into explicit parallel groups using comments in tasks.md:

```markdown
### Phase 1: Setup

<!-- parallel-group: 1 (max 3 concurrent) -->
- [ ] T002 [P] Create CapabilityManifest.cs in Models/Generation/
- [ ] T003 [P] Create DocumentIndex.cs in Models/Generation/
- [ ] T004 [P] Create ResolvedContext.cs in Models/Generation/

<!-- parallel-group: 2 (max 3 concurrent) -->
- [ ] T005 [P] Create GenerationResult.cs in Models/Generation/
- [ ] T006 [P] Create BatchGenerationJob.cs in Models/Generation/
- [ ] T007 [P] Create SchemaExport.cs in Models/Generation/

<!-- sequential -->
- [ ] T013 Create generation.ts with all TypeScript interfaces
```

### Plan Phase Parallelism

During Phase 3 (Plan), the plan agent's Phase 0 (Research) can dispatch up to 3 research sub-tasks in parallel:
- Each `NEEDS CLARIFICATION` item or technology best-practice lookup is an independent research task
- Fan out up to 3 at a time, consolidate results into research.md
- Phase 1 (Design) artifacts -- data-model.md, contracts/, quickstart.md -- can be generated in parallel if they don't depend on each other's output

### Implement Phase Parallelism

During Phase 8 (Implement), for each implementation phase in tasks.md:
1. Read the phase and identify parallel groups (marked with `<!-- parallel-group: N -->` comments)
2. For each group, dispatch up to 3 `speckit.implement` subagents simultaneously, each given a specific subset of tasks
3. When all tasks in a group complete, move to the next group or sequential task
4. After the entire phase completes, if **`human`** mode, checkpoint with the user before proceeding; if **`touchless`**, continue to the next phase

### Instructions for Tasks Agent

When the fleet orchestrator delegates to `speckit.tasks`, append this instruction:

> "Organize [P]-marked tasks into explicit parallel groups using `<!-- parallel-group: N -->` HTML comments. Each group should contain up to 3 tasks that can execute concurrently (different files, no dependencies). Add `<!-- sequential -->` before tasks that must run in order. This enables the fleet orchestrator to fan out up to 3 subagents per group during implementation."

## First-Turn Behavior -- Artifact Detection & Resume

On **every** invocation, before doing anything else, run artifact detection to determine where the workflow stands. This allows the orchestrator to resume mid-flight even in a fresh conversation.

### Step 0: Branch safety pre-flight

Before anything else, run basic git health checks:

1. **Uncommitted changes**: Run `git status --porcelain`. If there are uncommitted changes, warn the user:
   > WARNING: You have uncommitted changes. Starting the fleet may create conflicts. Commit or stash first?
   > - **Continue** -- proceed with uncommitted changes (risky)
   > - **Stash** -- run `git stash` and continue
   > - **Abort** -- stop and let the user handle it

2. **Detached HEAD**: Run `git branch --show-current`. If empty (detached HEAD), abort:
   > Cannot run fleet on a detached HEAD. Please check out a feature branch first.

3. **Branch freshness** (advisory): Run `git log --oneline HEAD..origin/main 2>/dev/null | wc -l`. If the main branch has commits not in the current branch, advise:
   > Your branch is {N} commits behind main. Consider rebasing before starting implementation to avoid merge conflicts later.

This check runs only once on first invocation. It does NOT block the workflow (except for detached HEAD).

### Step 1: Discover the feature directory

Run `{SCRIPT}` from the repo root to get the feature directory paths as JSON. Parse the output to get `FEATURE_DIR`.

If the script fails (e.g., not on a feature branch):

- If **`JIRA_ISSUE_KEY`** was parsed from `$ARGUMENTS` (with or without supplemental text), proceed to Phase 1 when no suitable `FEATURE_DIR` exists: pass **`JIRA_ISSUE_KEY`**, **`JIRA_ISSUE_TYPE`**, **`JIRA_LINKED_STORIES`** (when Epic—fetch or user-provided), resolved Jira summary/description (if any), and **`FEATURE_DESCRIPTION`** to `speckit.specify` so the new feature directory and `spec.md` include Jira tracking metadata and linked Stories under Epics.
- Else if **`FEATURE_DESCRIPTION`** was provided (free text only), proceed directly to Phase 1 -- pass the description to `speckit.specify` and it will create the feature directory.
- Else if `$ARGUMENTS` is empty, run artifact detection under `specs/` if your repo convention allows manual discovery; if still no `FEATURE_DIR`, ask the user for a **Jira issue key** and/or feature description, then start Phase 1.

When **`JIRA_ISSUE_KEY`** is set, prefer **branch names** that include the issue key or slug (e.g. `001-dcrf-3041-smart-duplicates`) if `speckit.specify` or your team convention supports it—otherwise keep SpecKit defaults and rely on `spec.md` metadata for the Jira link.

### Step 2: Check model configuration

Check if `{FEATURE_DIR}/../../../.specify/extensions/fleet/fleet-config.yml` (or the project's config location) has model settings. If the config file doesn't exist or models are set to defaults:

1. **Detect the platform**: Identify which IDE/agent platform you're running in (VS Code Copilot, Claude Code, Cursor, etc.) based on available context.

2. **Primary model**: If `models.primary` is `"auto"`, use whatever model you are currently running as. No action needed -- you ARE the primary model.

3. **Review model**: If `models.review` is `"ask"`, prompt the user:
   > **Model setup (one-time):** The cross-model review (Phase 7) works best with a *different* model than the one running the fleet, to catch blind spots.
   >
   > What model should I use for the review phase? Suggestions:
   > - A different model family (e.g., if you're on Claude, use GPT or Gemini)
   > - A different tier (e.g., if you're on Opus, use Sonnet)
   > - "skip" to skip Phase 7 entirely
   >
   > You can also set this permanently in your fleet config.

4. **Store the choice**: Remember the user's model selection for the duration of this conversation. If they want to persist it, suggest editing the config file.

5. **Touchless + `models.review` is `"ask"`**: Do **not** prompt. Use the **same model as `models.primary`** for Phase 7 (`speckit.fleet.review`) and prepend a one-line note in `review.md` that cross-model diversity was not used. Alternatively, if the product policy is to skip review when no second model is configured, skip Phase 7 with a logged warning — prefer running review with the primary model unless the user config forbids it.

### Step 2a: Resolve execution mode (if not set by CLI)

If **no** execution-mode token was present in `$ARGUMENTS` (see **User Input §0**):

1. Read `.specify/extensions/fleet/fleet-config.yml` from the repository root; merge **`execution`** from `fleet-config.local.yml` if present (local wins for `default_mode`).
2. Set **`FLEET_EXECUTION_MODE`** from `execution.default_mode`: **`human`** or **`touchless`**. If absent or invalid, default to **`human`**.

### Step 2b: Resolve reference repository paths (Java / Adapter)

Used by Operating Rule 11 and when passing stack context to agents.

1. **Read** `.specify/extensions/fleet/fleet-config.yml` from the **repository root** (same directory layout as `config-template.yml`).
2. **Override (optional)**: If `.specify/extensions/fleet/fleet-config.local.yml` exists, merge **`reference_repos`**, **`execution`**, **`default_workflow`**, **`workflow_aliases`**, **`workflows`**, **`jira`** (including **`jira.field_updates`** and nested keys), **`pull_requests`**, and **`superpowers`** — values in the local file **win** on key collision (same as `reference_repos` / `execution`).
3. **Missing config**: If `reference_repos` is absent or `local_path` is empty, use `config-template.yml` as a guide and ask the user once to set paths, or proceed with **repo_name** labels only.

Pass resolved **`reference_repos.*.local_path`** and **`repo_name`** for each sibling (`java_service`, `adapter`) into Phases 1–8 delegations alongside Jira/feature text.

### Step 2c: Jira status automation (Atlassian MCP)

1. If the merged config has **no `jira` section** or **`jira.enabled`** is **`false`**, skip all Jira transition steps for this Fleet run.
2. If **`jira.enabled`** is **`true`**, Fleet **must** run **§ Jira status transitions (Atlassian MCP)** after Phase **1** and after Phase **8** when **`JIRA_ISSUE_KEY`** is set (or a Jira key is resolvable from `spec.md`), unless the corresponding **idempotency marker** already exists (see Step 3).

### Step 2d: Bitbucket pull requests (Zycus Bitbucket MCP)

1. If the merged config has **no `pull_requests` section** or **`pull_requests.enabled`** is **`false`**, skip all PR automation for this Fleet run.
2. If **`pull_requests.enabled`** is **`true`**, Fleet **must** follow **§ Bitbucket pull requests** when advancing **Phase 5 → 6** (PR1 — design through **tasks**) and **Phase 8 → 9** (PR2 — **implementation** / full code), unless the corresponding **marker** exists (see Step 3). Implementation detail: **`.cursor/commands/speckit.bitbucket-pr.md`**.
3. If **`pull_requests.final_cumulative_fallback`** is **`true`**, Fleet **must** run the **cumulative PR** hook (Operating Rule **14**) after **Phase 10** / **Completion Summary** when PR1 and/or PR2 markers are still missing — **one** attempt to open a full-scope PR so the branch is not left without a reviewable PR.

### Step 2e: Superpowers skill hints (Cursor)

1. **Read** merged `fleet-config.yml` / `fleet-config.local.yml`. If **`superpowers`** is missing or **`superpowers.enabled`** is not **`true`**, skip this step.
2. **Resolve current phase** — use the workflow phase **`id`** from **`workflows.<FLEET_WORKFLOW>.phases`** for the phase you are about to run (e.g. `brainstorm`, `specify`, `implement`, `review`; bug workflow uses `reproduce`, `rca`, `fix-plan`, etc.).
3. **Look up** **`superpowers.skills_by_phase_id.<phase_id>`** (list of Superpowers skill names). If the key is missing or the list is empty, skip.
4. **When delegating** to the corresponding `speckit_command` for that phase, **prepend** to the delegation instructions:

   > **Superpowers (mandatory for this phase):** Invoke these Cursor Superpowers skills before executing the phase body: *{comma-separated list}*. Announce which skills you are applying. Short reference: `.specify/memory/superpowers-fleet.md`.

5. **Optional subagents:** If **`superpowers.optional_subagents.review`** lists **`code-reviewer`**, after Phase 7 (`speckit.fleet.review`) completes you **may** suggest running the **code-reviewer** subagent for very large design or implementation deltas — it **complements** the read-only Fleet review; it does not replace **`review.md`**.

Fleet remains the orchestrator; Superpowers defines *how* the model behaves inside each phase.

### Step 3: Probe artifacts in FEATURE_DIR

Check these paths **in order** using the `read` tool. Each check is a file/directory existence AND basic integrity test:

| Check | Path | Existence | Integrity |
|-------|------|-----------|-----------|
| Brainstorm | `{FEATURE_DIR}/brainstorm.md` | Optional — see Step 4 | Structured sections (Context, Options, Recommendation); file > 80 bytes? |
| Brainstorm skip | `{FEATURE_DIR}/.brainstorm-skip` | Empty marker file if user skipped Phase 0 | -- |
| spec.md | `{FEATURE_DIR}/spec.md` | File exists? | Has `## User Stories` or `## Requirements` **or** `## User Scenarios` section? File > 100 bytes? **Not** still a template: first line must **not** contain literal `[FEATURE NAME]` (see Step 4) |
| Clarifications | `{FEATURE_DIR}/spec.md` | Contains `## Clarifications` heading? | At least one Q&A pair present? |
| plan.md | `{FEATURE_DIR}/plan.md` | File exists? | Has `## Architecture` or `## Tech Stack` section? File > 200 bytes? |
| checklists/ | `{FEATURE_DIR}/checklists/` | Directory exists and has >=1 file? | Each file > 50 bytes? |
| tasks.md | `{FEATURE_DIR}/tasks.md` | File exists? | Contains at least one `- [ ]` or `- [x]` item? Has `### Phase` heading? |
| .analyze-done | `{FEATURE_DIR}/.analyze-done` | Marker file exists? | -- |
| review.md | `{FEATURE_DIR}/review.md` | File exists? | Contains `## Summary` and verdict table? |
| Implementation | `{FEATURE_DIR}/tasks.md` | All `- [x]`, zero `- [ ]` remaining? | -- |
| Verify extension | `.specify/extensions/verify/extension.yml` | File exists? | -- |
| Verification | `{FEATURE_DIR}/.verify-done` | Marker file exists? | -- |
| Jira → Under Development | `{FEATURE_DIR}/.jira-status-under-development` | Marker exists? | Written by `speckit.jira-status` / Fleet after successful transition |
| Jira → Under Testing | `{FEATURE_DIR}/.jira-status-under-testing` | Marker exists? | Written after Implement complete |
| Bitbucket PR1 (design) | `{FEATURE_DIR}/.pr-design.json` | File exists? | Written after Tasks — design/spec/tasks PR |
| Bitbucket PR2 (implementation) | `{FEATURE_DIR}/.pr-implementation.json` | File exists? | Written after Implement — code PR or “same PR” note |
| Bitbucket PR cumulative (fallback) | `{FEATURE_DIR}/.pr-cumulative.json` | File exists? | Written at Fleet end if PR1/PR2 missing and fallback runs |

**Integrity failures are advisory, not blocking.** If a file exists but fails integrity checks, warn the user:
> WARNING: `plan.md` exists but appears incomplete (missing expected sections). It may have been partially generated. Re-run Phase 3 (Plan), or continue with the current file?

### Step 4: Determine the resume phase

Walk the artifact signals **top-down**. The first phase whose artifact is **missing** is where work resumes.

**Workflows without Phase 0 brainstorm (`feature-touchless`, `bug-fix`, …):** If **`FLEET_WORKFLOW`** is **not** **`feature-development`**, **skip** the **Phase 0 (Brainstorm)** subsection below. Instead, walk **`workflows.<FLEET_WORKFLOW>.phases`** in order and use the artifact rules from **§0a D** (e.g. **`feature-touchless`** starts at **Specify** if `spec.md` is missing or still a template).

**Phase 0 (Brainstorm)** — **`feature-development` only** — required unless explicitly skipped:
- If **`brainstorm.md`** is missing **and** **`.brainstorm-skip`** is missing → resume at **Phase 0 (Brainstorm)**.
- If the user chose to skip brainstorming, create **`.brainstorm-skip`** (empty file) at the human gate and proceed to Phase 1.

**Phase 1 (Specify) — “filled” spec** — `spec.md` from `create-new-feature` is a **template** until `/speckit.specify` runs. Treat as **not yet complete** for Phase 1 if **any** of:
- `spec.md` is missing, **or**
- The first line of `spec.md` still contains the literal placeholder **`[FEATURE NAME]`** (template), **or**
- `spec.md` is clearly unchanged boilerplate (no meaningful user-story titles beyond `[Brief Title]` placeholders).

When those conditions hold → resume at **Phase 1 (Specify)** (even if `spec.md` file exists).

**Then** (brainstorm and specify done):

```
if no ## Clarifications       -> resume at Phase 2 (Clarify)
if plan.md missing           -> resume at Phase 3 (Plan)
if checklists/ empty/missing -> resume at Phase 4 (Checklist)
if tasks.md missing          -> resume at Phase 5 (Tasks)
if .analyze-done missing     -> resume at Phase 6 (Analyze)
if review.md missing         -> resume at Phase 7 (Review)
if tasks.md has `- [ ]`     -> resume at Phase 8 (Implement)
if .verify-done missing      -> resume at Phase 9 (Verify)
if all done                  -> resume at Phase 10 (Tests)
```

### Step 5: Present status and confirm

Show the user a status table and the detected resume point:

```
Execution mode: {FLEET_EXECUTION_MODE — human | touchless}
Jira: {JIRA_ISSUE_KEY or "—"}
Linked stories (if Epic): {count or "—"}
Feature: {branch name}
Directory: {FEATURE_DIR}

Phase 0 Brainstorm   [x] brainstorm.md or .brainstorm-skip
Phase 1 Specify      [x] spec filled (no [FEATURE NAME] placeholder)
Phase 2 Clarify      [x] ## Clarifications present
Phase 3 Plan         [x] plan.md found
Phase 4 Checklist    [x] checklists/ has 2 files
Phase 5 Tasks        [x] tasks.md found
Phase 6 Analyze      [ ] .analyze-done not found
Phase 7 Review       [ ] --
Phase 8 Implement    [ ] --
Phase 9 Verify       [ ] --
Phase 10 Tests       [ ] --

> Resuming at Phase 6: Analyze
```

Then ask: *"Detected progress above. Resume at Phase {N} ({name}), or override to a different phase?"*

- If user confirms -> create the todo list with completed phases marked as `completed` and resume from Phase N.
- If user provides a phase number or name -> start from that phase instead.
- If FEATURE_DIR doesn't exist -> start from **Phase 0 (Brainstorm)** unless the user explicitly skips brainstorming (then create `.brainstorm-skip` and begin Phase 1); ask for **`JIRA_ISSUE_KEY`** (if not already parsed) and/or feature description per **User Input** rules above.

### Edge Cases

- **Jira provisioning only**: If `$ARGUMENTS` is **only** `JIRA_ISSUE_KEY` and the script does not yield `FEATURE_DIR`, resolve issue text via MCP or user paste, then run **Phase 0** (`speckit.brainstorm`) unless skipped, then Phase 1 so `spec.md` carries the Jira metadata. Do **not** require a separate prose feature paragraph if Jira content is available.
- **Epic without fetchable children**: If the issue is an Epic but linked Stories cannot be retrieved, still populate **`Jira linked stories`** with *Not fetched* or *None* and continue; optionally ask the user once for a manual list.
- **Implementation partially complete**: If `tasks.md` exists and has a mix of `[x]` and `[ ]`, resume at Phase 8 (Implement). Tell the user how many tasks remain: *"tasks.md: {done}/{total} tasks complete. {remaining} tasks remaining."*
- **Analyze completion marker**: After Phase 6 (Analyze) completes -- whether it produces `remediation.md` or not -- create a marker file `{FEATURE_DIR}/.analyze-done` containing the timestamp. This distinguishes "analyze ran clean" from "analyze never ran." The `.analyze-done` file is the artifact signal for Phase 6, not `remediation.md`.
- **Review can be skipped**: If user opts to skip cross-model review, treat Phase 7 as skipped and proceed to Phase 8.
- **Review found NO failures**: If `review.md` exists and overall verdict is "READY", Phase 7 is complete -- proceed to Phase 8.
- **Review found FAIL items**: If `review.md` has FAIL verdicts, present them and ask user whether to (a) fix the issues by re-running the relevant earlier phase, (b) proceed anyway, or (c) abort.
- **Verify extension not installed**: If `.specify/extensions/verify/extension.yml` doesn't exist, prompt to install. If user declines, skip Phase 9.
- **Verify completion marker**: After Phase 9 (Verify) completes, create `{FEATURE_DIR}/.verify-done` with timestamp. This distinguishes "verify ran" from "verify never ran."
- **Checklists may be skipped**: Some features don't use checklists. If `tasks.md` exists but `checklists/` doesn't, treat Phase 4 as skipped.
- **Fresh branch, no specs dir**: Start from **Phase 0** (or Phase 1 if brainstorming is skipped via `.brainstorm-skip`). Use **`JIRA_ISSUE_KEY`** and/or `FEATURE_DESCRIPTION` from `$ARGUMENTS` per **User Input** rules; otherwise ask the user.
- **User says "start over"**: Re-run from **Phase 0** (or Phase 1 if they want to skip brainstorm) regardless of existing artifacts. Warn that this will overwrite existing artifacts and get confirmation.

### Stale Artifact Detection

After determining the resume phase, check for **stale downstream artifacts** -- files generated by an earlier phase that may be outdated because an upstream artifact was modified later.

Compare file modification timestamps in this dependency chain:

```
brainstorm.md -> spec.md -> plan.md -> tasks.md -> .analyze-done -> review.md -> [implementation] -> .verify-done
```

(If `.brainstorm-skip` was used instead of `brainstorm.md`, use `spec.md` as the upstream start for staleness checks involving exploration.)

If a file is **newer** than a downstream file that depends on it (e.g., `spec.md` was modified after `plan.md`), warn the user:

> WARNING: **Stale artifact detected**: `plan.md` (modified {date}) was generated before the latest `spec.md` change ({date}). Plan may not reflect current requirements. Re-run Phase 3 (Plan) to update, or proceed with the current plan?

This is advisory only -- the user decides whether to rerun. Do not block the workflow.

## Phase Execution Template

For each phase:
```
1. Mark the phase as in-progress in the todo list
2. Announce: "**Phase N: {Name}** -- delegating to {agent}..."
3. Delegate to the agent with relevant arguments:
   - Phase 0 (Brainstorm): pass **`JIRA_ISSUE_KEY`** (if set), **`JIRA_LINKED_STORIES`** when Epic, resolved Jira content, **`FEATURE_DESCRIPTION`**, and **reference repo paths** (Java service + Adapter — read-only). Prepend Operating Rule 6 (suppress sub-agent handoffs).
   - Phase 1 (Specify): pass **`JIRA_ISSUE_KEY`** (if set), **`JIRA_LINKED_STORIES`** when Epic, resolved Jira content, and **`FEATURE_DESCRIPTION`** (verbatim supplemental text or full narrative after resolution—not only the raw key unless no other text exists), plus **reference repo paths** (Java service + Adapter) from Operating Rule 11. **If `brainstorm.md` exists:** prepend *"Branch and template spec.md already exist from Phase 0 — do NOT run create-new-feature.sh; read `brainstorm.md` and fill `spec.md`."*
   - Phase 2 (Clarify): pass **`JIRA_ISSUE_KEY`**, **`JIRA_LINKED_STORIES`** when Epic, the feature description, reference repo paths, and any user feedback. If **`touchless`**, append the single-pass instruction from Operating Rule 3.
   - Phases 3–7: pass **`JIRA_ISSUE_KEY`** (if set), **`JIRA_LINKED_STORIES`** when Epic, the feature description, reference repo paths, and any user-provided refinements
   - Phase 8 (Implement): pass the same context **and** explicit instruction: *"Execute tasks only in the merlin-assist-zycuschat workspace also do not sibling Java/adapter checkouts"* (use **`repo_name`** from `reference_repos` in fleet-config, e.g. `merlinassist-zycuschat-service-app`, `merlin-assist-adapter`).
   - Phases 9–10: **merlin-assist-zycuschat** (this UI workspace) only for verification and test commands — do not run Java/Adapter builds from sibling checkouts unless the user explicitly asks
4. Summarize the agent's output concisely
5. **If `FLEET_EXECUTION_MODE=human`:** Ask: *"Ready to proceed to Phase N+1 ({next name}), or would you like to revise?"* — wait for user response — mark phase complete when approved.
6. **If `touchless`:** Mark phase complete and **immediately** continue (no wait). On unrecoverable error or review FAIL, **stop** and report.
7. **Jira status (after the phase gate — Operating Rule 12):**
   - **Advancing Phase 1 → 2:** After the user **approves** Phase 1 (**human**) or **immediately after** Phase 1 succeeds (**touchless**): if **`jira.enabled`**, a Jira key is present (`JIRA_ISSUE_KEY` or `spec.md`), and **`{FEATURE_DIR}/.jira-status-under-development`** is **missing**, execute **§ Jira status transitions** with mode **`start`** (**step 4** field updates when **`jira.field_updates.enabled`**), then create the marker.
   - **Advancing Phase 8 → 9:** After the user **approves** Phase 8 (**human**) or **immediately after** all implement tasks are `[x]` (**touchless**): if **`jira.enabled`** and **`{FEATURE_DIR}/.jira-status-under-testing`** is **missing**, execute **§ Jira status transitions** with mode **`testing`**, then create the marker.
8. **Bitbucket PRs (after the phase gate — Operating Rules 13–14):**
   - **Advancing Phase 5 → 6:** After Phase **5 (Tasks)** is accepted (**human**) or **immediately after** tasks succeed (**touchless**): if **`pull_requests.enabled`** and **`{FEATURE_DIR}/.pr-design.json`** is **missing**, execute **§ Bitbucket pull requests** with mode **`design`** (PR1 — through tasks).
   - **Advancing Phase 8 → 9:** After Phase **8** is accepted or implement completes (**touchless**): if **`pull_requests.enabled`** and **`{FEATURE_DIR}/.pr-implementation.json`** is **missing**, execute **§ Bitbucket pull requests** with mode **`implementation`** (PR2 — full code).
   - **After Phase 10 / Completion Summary:** If **`pull_requests.final_cumulative_fallback`** and Operating Rule **14** apply, run **cumulative** PR once if needed.
```

## Phase 7: Cross-Model Review

Ideally this phase uses a **different model** than the one that generated plan.md and tasks.md. If **`FLEET_EXECUTION_MODE=touchless`** and `models.review` was `"ask"`, Step 2 allows using the **primary** model — blind-spot detection is reduced; document that in `review.md`.

1. Delegate to `speckit.fleet.review` -- it runs on the **review model** configured in Step 2 and is **read-only**
2. The review agent reads spec.md, plan.md, tasks.md, checklists/, and remediation.md
3. It evaluates 7 dimensions: spec-plan alignment, plan-tasks completeness, dependency ordering, parallelization correctness, feasibility & risk, standards compliance, implementation readiness
4. It outputs a structured review report with PASS/WARN/FAIL verdicts per dimension
5. **Save the review output** to `{FEATURE_DIR}/review.md`
6. Present the summary table to the user:
   - **All PASS / READY**: If **`human`**, *"Cross-model review passed. Ready to implement?"* If **`touchless`**, proceed to Phase 8.
   - **WARN items**: If **`human`**, *"Review found {N} warnings. Proceed to implementation, or address them first?"* If **`touchless`**, proceed to Phase 8 with warnings logged.
   - **FAIL items**: List them. If **`touchless`**, **stop** — mandatory checkpoint; do not auto-implement. If **`human`**, ask which earlier phase to re-run (plan, tasks, or analyze).
7. If **`human`** and user chooses to fix: loop back to the appropriate phase, then re-run review after fixes
8. If **`human`** and user approves, or **`touchless`** with no FAIL: mark Phase 7 complete and proceed to Phase 8 (Implement)

**Note**: Phase 7 (Review) validates design artifacts *before* implementation. Phase 9 (Verify) validates actual code *after* implementation. Both are read-only.

## Phase 9: Post-Implementation Verification

This phase validates that the implemented code matches the specification artifacts. It requires the **verify extension**.

### Extension Installation Check

Before delegating to `speckit.verify`, check if the extension is installed:

1. Check if `.specify/extensions/verify/extension.yml` exists using the `read` tool
2. If **`FLEET_EXECUTION_MODE=touchless`** and the extension is **missing**: **skip** Phase 9, log a clear warning, **do not** create `.verify-done`, **do not** prompt to install.
3. If **`human`** mode and extension is **missing**, ask the user:
   > The verify extension is not installed. Install it now?
   > ```
   > specify extension add verify --from https://github.com/ismaelJimenez/spec-kit-verify/archive/refs/tags/v1.0.0.zip
   > ```
4. If user approves, run the install command in the terminal
5. If user declines, skip Phase 9 and proceed to Phase 10 (CI)

### Verification Execution

1. Delegate to `speckit.verify` -- it reads spec.md, plan.md, tasks.md, constitution.md and the implemented source files
2. It runs 7 verification checks: task completion, file existence, requirement coverage, scenario & test coverage, spec intent alignment, constitution alignment, design & structure consistency
3. It outputs a verification report with findings, metrics, and next actions
4. Present the summary to the user:
   - **No findings**: *"Verification passed. Ready to run CI?"* -- proceed to Phase 10
   - **Findings exist**: Show the findings grouped by severity (CRITICAL, WARNING, INFO) and enter the **Implement-Verify loop** below

### Implement-Verify Loop

When verification produces findings, run a remediation loop:

```
repeat:
  1. Present findings to user
  2. Ask: "Re-run implementation to address these findings? (yes / skip / abort)"
     - yes   -> delegate to speckit.implement with findings as context, then re-run speckit.verify
     - skip  -> exit loop, proceed to Phase 10 with current state
     - abort -> stop the workflow entirely
  3. After re-verify, check findings again
until: no findings remain OR user says skip/abort
```

Rules for the loop:
- **Pass findings as context**: When delegating to `speckit.implement`, include the verification findings so it knows exactly what to fix. Prepend: *"Address the following verification findings: {findings list}"*
- **Suppress sub-agent handoffs** (Operating Rule 6 still applies)
- **Track iterations**: Show the loop count each time -- *"Implement-Verify iteration {N}: {findings_count} findings remaining"*
- **`human` mode**: **Cap at 3 iterations**: After 3 rounds, if findings persist, warn the user: *"3 remediation iterations completed with {N} findings still remaining. These may require manual intervention. Proceed to CI, or continue?"* **Human gate every iteration** — never auto-loop without asking.
- **`touchless` mode**: Run **at most 1** remediation (`speckit.implement` then `speckit.verify`). If findings remain after that, **stop** and report — do not loop further without a human turn.
- **Delta reporting**: After each re-verify, show what changed -- *"Fixed: {N}, New: {N}, Remaining: {N}"*

After the loop exits (no findings or user skips):
1. Create a marker file `{FEATURE_DIR}/.verify-done` containing the timestamp and final findings count
2. Mark Phase 9 complete and proceed to Phase 10 (Tests)

## Phase 10: Tests

After verification, detect and run the project's test suite.

### Test Runner Detection

Detect test runner(s) by checking for these files at the repo root, in order:

| Check | Runner | Command |
|-------|--------|---------|
| `package.json` with `"test"` script | npm/yarn/pnpm | `npm test` (or `yarn test` / `pnpm test` based on lockfile) |
| `*.sln` or `*.slnx` or `*.csproj` | dotnet | `dotnet test` |
| `Makefile` with `test` target | make | `make test` |
| `pytest.ini` or `pyproject.toml` with `[tool.pytest]` | pytest | `pytest` |
| `Cargo.toml` | cargo | `cargo test` |
| `go.mod` | go | `go test ./...` |

If **multiple** runners are detected (e.g., a monorepo with both `package.json` and `*.slnx`), run all of them and report results per runner.

If **no** runner is detected, ask the user: *"No test runner detected. What command runs your tests?"*

### Test Execution

1. Run the detected test command(s) from the repo root
2. Report pass/fail summary with failure details

### CI Remediation Loop

If CI fails, run a remediation loop (same pattern as the Implement-Verify loop):

```
repeat:
  1. Parse test failures -- group by type (compile error, test failure, lint error)
  2. Present failures to user with file locations and error messages
  3. Ask: "Fix these CI failures? (yes / skip / abort)"
     - yes   -> delegate to speckit.implement with failure details as context, then re-run CI
     - skip  -> exit loop, leave failures for manual fixing
     - abort -> stop the workflow entirely
  4. After re-run, check CI result again
until: CI passes OR user says skip/abort
```

Rules:
- **Pass failure context**: Include exact error messages, file paths, and test names when delegating to implement
- **`human` mode**: **Cap at 3 iterations**; **human gate every iteration** — never auto-loop without asking
- **`touchless` mode**: **At most 1** implement + re-test cycle; if tests still fail, **stop** and report
- **Delta reporting**: *"Fixed: {N} failures, New: {N}, Remaining: {N}"*
- **Distinguish failure types**: Compile errors should be fixed before test failures (they may cause cascading test failures)

### Tests Pass

When all tests pass, proceed to the Completion Summary.

## Error Recovery

### Parallel Task Failure

When a task within a parallel group fails during Phase 8 (Implement):
1. **Let the other in-flight tasks finish** -- don't abort tasks that are already running
2. Report which task(s) failed with error details
3. Offer three options:
   - **Retry failed only** -- re-dispatch only the failed task(s), skip completed ones
   - **Retry entire group** -- re-run all tasks in the parallel group (useful if failure cascaded)
   - **Skip and continue** -- mark the failed task(s) and move on (user can fix manually later)
4. Never auto-retry -- always ask the user

### Sub-Agent Timeout or Crash

If a delegated sub-agent doesn't return (timeout) or returns an error:
1. Report the phase and agent that failed
2. Offer to retry the same phase or skip it
3. If the same agent fails twice in a row, suggest the user run it manually (`/speckit.{agent}`) and then resume the fleet

## Phase Rollback

At any human gate, the user may say "go back to Phase N" or "rollback to plan." The fleet supports this:

1. **Identify the target phase**: Parse the user's request to determine which phase to roll back to.
2. **Warn about downstream invalidation**: All artifacts generated by phases *after* the target phase are now potentially stale. Show:
   > Rolling back to Phase {N} ({name}). The following artifacts may be invalidated:
   > - brainstorm.md (Phase 0)
   > - spec.md / plan.md (Phases 1–3)
   > - tasks.md (Phase 5)
   > - Implementation (Phase 8)
   >
   > These will be regenerated as the workflow proceeds. Continue?
3. **Delete marker files only**: Remove `.analyze-done`, `.verify-done`, and `review.md` for invalidated phases. **Rollback to Phase 0:** remove `brainstorm.md` and `.brainstorm-skip` when restarting exploration from scratch. Do NOT delete spec.md, plan.md, or tasks.md -- they'll be overwritten when the phase re-runs.
4. **Update the todo list**: Reset all phases from the target phase onward to `not-started`.
5. **Resume from the target phase**: Follow the normal phase execution flow from that point.

**Constraints**:
- Cannot rollback during an active sub-agent delegation -- wait for it to complete first
- Rollback to Phase 0 (Brainstorm) or Phase 1 (Specify) with "start over" requires explicit confirmation since it regenerates everything

## Completion Summary

After Phase 10 completes (CI passes or user skips CI), **first** run the **Bitbucket cumulative fallback** (Operating Rule **14** / **Step 2d §3**) if **`pull_requests.final_cumulative_fallback`** is **`true`**, **`pull_requests.enabled`** is **`true`**, **`{FEATURE_DIR}/.pr-cumulative.json`** is **missing**, and **either** **`.pr-design.json`** **or** **`.pr-implementation.json`** is **missing** — then present a structured summary:

```
## Fleet Complete

Execution mode: {human | touchless}
Jira: {JIRA_ISSUE_KEY or "—"}
Linked stories (Epic): {count or "n/a"}
Feature: {feature name}
Branch: {branch name}
Duration: Phases 0-10 ({phases completed}/{phases total}, {phases skipped} skipped)

### Artifacts Generated
- brainstorm.md -- exploration & options (skipped if `.brainstorm-skip` or user skipped Phase 0)
- spec.md -- feature specification ({word count} words, {user stories count} user stories)
- plan.md -- technical plan ({components count} components)
- tasks.md -- {total tasks} tasks ({completed} completed, {remaining} remaining)
- review.md -- cross-model review (verdict: {verdict})

### Implementation
- Files created: {count}
- Files modified: {count}
- Tests added: {count}

### Quality Gates
- Analyze: {pass/findings count}
- Cross-model review: {verdict}
- Verify: {pass/findings count} ({iterations} iterations)
- CI: {pass/fail}

### Git
- Commits: {list of WIP commits if any}
- Ready to push: {yes/no}

### Pull requests
- Design PR1: {.pr-design.json url or "—"}
- Implementation PR2: {.pr-implementation.json url or same PR / "—"}
- Cumulative fallback: {.pr-cumulative.json url or "skipped / not needed"}
```

After the summary, offer:
1. *"Push to remote and create a PR?"* (if the user wants)
2. *"View any artifact? (brainstorm, spec, plan, tasks, review)"*
