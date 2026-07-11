---
description: "Open Bitbucket pull requests for Fleet (design PR1, implementation PR2, optional cumulative fallback) — Zycus Bitbucket MCP."
user-invocable: true
disable-model-invocation: true
---

# speckit.bitbucket-pr

Read merged **`.specify/extensions/fleet/fleet-config.yml`** + **`fleet-config.local.yml`**. Use **Zycus Bitbucket MCP** (`bitbucket_create_pull_request`, `bitbucket_list_pull_requests`, `bitbucket_get_pull_request`, …).

## Modes

| Mode | When | Marker file |
|------|------|----------------|
| **`design`** | After Phase 5 (Tasks) → advancing to Analyze | `{FEATURE_DIR}/.pr-design.json` |
| **`implementation`** | After Phase 8 (Implement) → advancing to Verify | `{FEATURE_DIR}/.pr-implementation.json` |
| **`cumulative`** | End of Fleet — fallback when PR1/PR2 missing or failed | `{FEATURE_DIR}/.pr-cumulative.json` |

## Common steps

1. If **`pull_requests.enabled`** is not **`true`**, skip.
2. Resolve **`workspace`** / **`repo_slug`** from config or **`git remote get-url origin`** (Bitbucket URL).
3. **`source_branch`** = `git branch --show-current`.
4. If **`pull_requests.require_push`** is **`true`**, ensure the branch exists on the remote before **create** (or warn and skip).
5. Substitute **`{jira_key}`**, **`{branch}`** in title templates from **`JIRA_ISSUE_KEY`** and **`source_branch`**.

## Design — PR1

- **`destination_branch`** = `pull_requests.destination_branch`.
- Title: **`pull_requests.title_template_design`**.
- Description: scope = spec, plan, tasks, checklists (no implementation requirement yet).
- On success: write **`.pr-design.json`** with **`id`**, **`url`**, **`timestamp`**.

## Implementation — PR2

1. **`bitbucket_list_pull_requests`** (`state`: `OPEN`).
2. If a PR already exists for the same **source** → **destination** and **`destination_branch_pr2`** is empty → **do not** create a second PR; write **`.pr-implementation.json`** with **`strategy`**: `same_pull_request` and the **existing PR url**.
3. Else **`bitbucket_create_pull_request`** with title **`title_template_implementation`**; destination = **`destination_branch_pr2`** if set, else **`destination_branch`**.

## Cumulative — Fleet end fallback

When **`pull_requests.final_cumulative_fallback`** is **`true`** and Fleet completion hook runs (see **speckit.fleet** Operating Rule 14):

1. If **`{FEATURE_DIR}/.pr-cumulative.json`** already exists → skip.
2. If **both** **`.pr-design.json`** **and** **`.pr-implementation.json`** exist **and** PR2 is **not** missing (or `same_pull_request` recorded) → **optional skip** (work already has a PR). If either marker is **missing** or earlier PR creation **failed**, proceed.
3. **`bitbucket_create_pull_request`** with **`destination_branch`**, same **`source_branch`**, title **`pull_requests.title_template_cumulative`** (default **`[Fleet cumulative] {jira_key} — {branch}`**).
4. Description: **full scope** — design artifacts (spec, plan, tasks) + implementation summary + branch name.
5. On success: write **`.pr-cumulative.json`** with **`id`**, **`url`**.

If **`fail_on_error`** is **`false`**, log and continue; otherwise stop on failure.
