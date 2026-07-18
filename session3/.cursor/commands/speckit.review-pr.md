---
description: Review a Bitbucket pull request’s code changes (Cloud or Data Center) using Code Oracle MCP; output prioritized recommendations (P0–P3).
tools: ['user-Code-oracle/codeoracle_query', 'user-Code-oracle/codeoracle_graph', 'user-Code-oracle/codeoracle_list_repos']
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Parsing User Input

1. **PR reference** (required unless user pasted a full diff): One of:
   - **Bitbucket Cloud**: Pull request URL, e.g. `https://bitbucket.org/<workspace>/<repo>/pull-requests/<id>` (or `/pull-requests/<id>` with query params). Also: workspace + repo + id (e.g. `myworkspace/myrepo 42`, PR `42`).
   - **Bitbucket Data Center / Server**: URL like `https://<host>/projects/<PROJECT_KEY>/repos/<repo>/pull-requests/<id>`, or project key + repo slug + PR id from user.
   - **Local**: Branch vs default branch (e.g. `feature/foo` vs `main` / `develop`) if user says “review my branch” or checked-out PR source.
2. **Optional scope**: User may ask to focus on security, performance, tests, or a specific area—honor that in depth of review.

If no PR identifier is given but the user pasted a **patch or diff**, treat that pasted content as the change set and skip remote fetch.

## Outline

### 1. Obtain the change set (diff + file list)

**Primary: Bitbucket + Git (works for Cloud and most Server setups)**

1. Ensure `origin` points at the Bitbucket repo (Cloud: `git@bitbucket.org:workspace/repo.git` or HTTPS).
2. Fetch the PR source branch ref (Bitbucket exposes pull-request refs on `origin`):

   - **Bitbucket Cloud** (typical):

     ```bash
     git fetch origin pull-requests/<PR_ID>/from:bb-pr-<PR_ID>
     ```

   - **Bitbucket Data Center / Server** (if the above fails, try):

     ```bash
     git fetch origin refs/pull-requests/<PR_ID>/from:bb-pr-<PR_ID>
     ```

3. Diff against the **destination branch** of the PR (ask user if unknown; common: `main`, `master`, `develop`):

   ```bash
   git diff origin/<destination-branch>...bb-pr-<PR_ID>
   ```

   If you need the merge result instead of three-dot vs destination, after a successful fetch check whether `pull-requests/<PR_ID>/merge` exists and compare appropriately, or use the Bitbucket API diff below.

4. **Metadata / file list**: From Bitbucket UI (title, description, reviewers) or API:

   - **Cloud REST** (app password or OAuth):  
     `GET https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{id}`  
     Diff patch: same base URL + `/diff` (accept `text/plain` or per [Bitbucket API](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-pullrequests/)).
   - **Server REST**:  
     `GET /rest/api/1.0/projects/{projectKey}/repos/{repositorySlug}/pull-requests/{id}` and diff endpoint per instance docs.

**Optional: Atlassian Bitbucket CLI (`bb`)** — if installed and authenticated to the workspace:

- Use `bb pr view` / `bb pr diff` (or equivalent for your `bb` version) for the PR id and workspace/repo context—prefer this when it returns a full diff without manual fetch.

**Fallback:**

- User pastes **“View raw diff”** or exported diff from the Bitbucket PR page.
- **Local only**: `git diff origin/develop...HEAD` (or named branches) when the user is on the PR branch and names the base.

**If only pasted diff:** Use that as the sole diff; still list inferred paths from the patch headers.

Build a concise **inventory**: list of changed files, rough size (lines), languages (TypeScript, TSX, CSS, etc.).

### 2. Enrich with Code Oracle (mandatory for recommendations)

Use **Code Oracle MCP** so review is grounded in how this codebase actually works—not generic advice only.

**Before querying:** If the indexed repo name is unclear, call **codeoracle_list_repos** and pick the repo that matches this workspace (e.g. `merlin-assist-zycuschat` or org/repo name).

**codeoracle_query** — run several focused questions, e.g.:

- For each major changed area: “How is [changed class or package] used elsewhere? What invariants or tenant/config rules apply?”
- “What are the established patterns for [DAO/service/endpoint] in this repo for tenant_id, transactions, and audit trail?”
- “Are there known risks (RLS, workflow, matching) around [feature touched by this PR]?”
- If diff adds new APIs: “Who calls similar endpoints and what error handling is expected?”

Use **repo_filter** to restrict to this repository when the index is multi-repo.

**codeoracle_graph** (optional but valuable for non-trivial changes):

- For a key changed symbol or module, use `graph_type` **call** or **dependency** with a sensible **max_nodes** to see blast radius of the change.

Synthesize Oracle answers into the review: cite file/class names Oracle surfaced, not invented paths.

### 3. Read critical hunks locally (when files exist in workspace)

For high-risk files (auth, SQL, workflow, invoice status, multi-tenancy), open or grep the **current** versions of changed files in the workspace to validate:

- Tenant scoping, parameterized queries, `@Transactional`, audit logging, status transitions (per project rules / `.cursorrules` if applicable).

Cross-check diff against Oracle + local read.

### 4. Produce the PR review report (priority order)

Output a single Markdown report with sections in **strict priority order** so reviewers can act top-down.

#### P0 — Blockers (must fix before merge)

Security (injection, authz bypass, cross-tenant data), data corruption, broken compile/deploy, illegal state transitions, production outage risk.

#### P1 — High (should fix before merge)

Logic bugs, missing error handling on critical paths, RLS/tenant gaps, missing audit where required, breaking API contracts without versioning.

#### P2 — Medium (strongly recommended)

Test gaps for changed behavior, performance (N+1, unbounded queries), maintainability, duplication, incomplete config/feature flags.

#### P3 — Low (nice to have)

Naming, comments, minor style, optional refactors.

**Within each priority band**, number items **P0-1, P0-2**, … so order is explicit.

For **every** item include where possible:

- **Finding**: What’s wrong or risky.
- **Evidence**: File path + line or hunk reference from diff or workspace; optional Oracle quote (short).
- **Recommendation**: Concrete fix or follow-up.

End with a **Summary**: 2–4 sentences and **Merge recommendation**: *Approve / Approve with comments / Request changes* (one line, justified).

### 5. Confirm to user

- State PR (or branch) reviewed and that recommendations are ordered P0 → P3.
- If diff could not be fetched (e.g. private Bitbucket repo, fetch ref denied, wrong `origin`), say so and ask for pasted diff from Bitbucket, **workspace/repo + PR id** for API, or local branch + base branch name.

## Operating Principles

- **Bitbucket-first**: Assume PRs live in Bitbucket; use `git fetch … pull-requests/<id>/from` and/or Bitbucket REST API—not GitHub `gh` or `pull/N/head` refspecs unless the remote is explicitly GitHub.
- **Code Oracle is required** for non-trivial PRs: use it to align feedback with real callers, patterns, and risks in this repo.
- **Prioritize**: Never bury a P0 under style nits; P0/P1 first, always.
- **No file writes**: This command does not modify the codebase; output is the review in chat (user may paste into PR).
- **Honest scope**: If Oracle returns nothing useful for a file, say “limited index coverage” and rely on diff + local read.

## Context

$ARGUMENTS
