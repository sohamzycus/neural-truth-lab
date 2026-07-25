---
description: "Jira field updates (AI Categorization, ETA Dev Done, sprint) and status transitions for Fleet — used by /speckit.fleet and standalone /speckit.jira-status."
user-invocable: true
disable-model-invocation: true
---

# speckit.jira-status

Use **Atlassian MCP** (`getJiraIssue`, `editJiraIssue`, `getTransitionsForJiraIssue`, `transitionJiraIssue`, `getAccessibleAtlassianResources`). Read merged **`.specify/extensions/fleet/fleet-config.yml`** + **`fleet-config.local.yml`** (local wins on collision).

## When to run

- **Fleet:** Before **Under Development** (mode `start`) and optionally align fields again before **Under Testing** (`testing`) if your process requires it — Fleet runs field updates **only** with the same idempotency gate as transitions: if **`{FEATURE_DIR}/.jira-status-under-development`** already exists, skip (see Fleet orchestrator).
- **Standalone:** User invokes **`/speckit.jira-status start|testing`** with **`JIRA_ISSUE_KEY`** and **`FEATURE_DIR`** context.

## 1. Preconditions

- **`jira.enabled`** is **`true`** in merged config.
- Resolve **`cloudId`**: **`jira.cloud_id`** if set, else **`getAccessibleAtlassianResources`**.
- Resolve issue keys: **`JIRA_ISSUE_KEY`**, plus linked Story keys when **`jira.transition_epic_and_stories`** is true (same as Fleet).

## 2. Field updates (before transition — mode `start` only)

Skip if **`jira.field_updates.enabled`** is not **`true`**.

For **each** issue key:

1. **`getJiraIssue`** (`cloudId`, `issueIdOrKey`) — inspect fields.
2. Build **`fields`** for **`editJiraIssue`** only when config provides **`field_id`** (non-empty) for that item:

### 2a. AI Categorization

- If **`jira.field_updates.ai_categorization.field_id`** is set: set that field to **`jira.field_updates.ai_categorization.value`** (default **`AI Assisted Epic`**).
- Jira custom fields often use ADF or string; use the shape required by your site (see **`getJiraIssueTypeMetaWithFields`** if validation fails).

### 2b. ETA Dev Done

- If **`jira.field_updates.eta_dev_done.field_id`** is set: set date to **run date + `offset_days_from_run`** (default **3**).
- Use **ISO 8601 date** string (`YYYY-MM-DD`) if the field is a date; use site-specific format if the API requires it.

### 2c. Sprint (only if issue has no active sprint)

- If **`jira.field_updates.sprint.assign_if_empty`** is not **`true`**, skip sprint logic.
- If **`getJiraIssue`** shows the Sprint field already populated (non-empty array or sprint object), **skip** sprint assignment.
- Else compute **`schedule_key`** from **today’s date** (UTC or team convention — document in Fleet run):

**Sprint schedule resolution**

- Read **`jira.field_updates.sprint.sprints`** (ordered list with **`start`**, **`end`**, **`key`** as `YYYY-MM-DD`).
- Let **`today`** be the calendar date for the run.
- If **`today`** is **on or after** `start` **and** **on or before** `end` for exactly one row → use that row’s **`key`**.
- If **`today`** is **before** the first `start` → use the **first** row’s **`key`** (upcoming sprint).
- If **`today`** is **after** the last `end` → use the **last** row’s **`key`**.
- Look up **`jira.field_updates.sprint.sprint_ids_by_schedule_key`** for the **`key`** (e.g. `"303"`, `"304"`). The value must be the **Jira Agile sprint id** (integer as string) for **`editJiraIssue`**.
- If **`sprint.field_id`** or the resolved **sprint id** is empty → **warn** and **skip** sprint (do not fail the Fleet run unless **`jira.fail_on_error`**).

**Sprint field shape (Jira Cloud — common)**

- Often **`customfield_…`**: `{ id: <sprintId> }` or array form for multiple sprints — match your **`getJiraIssue`** payload.

3. If **`fields`** is non-empty: **`editJiraIssue`** (`cloudId`, `issueIdOrKey`, `fields`).

## 3. Status transition

Same as Fleet **§ Jira status transitions**:

1. **`getTransitionsForJiraIssue`**
2. Pick transition name matching **`jira.under_development.name_matches`** (mode **`start`**) or **`jira.under_testing.name_matches`** (mode **`testing`**)
3. **`transitionJiraIssue`** with `transition.id`

If required fields block the transition, some teams use **`transitionJiraIssue`** with **`fields`** on the transition screen — use MCP schema for your site.

## 4. Local configuration (required for custom fields)

Copy field ids from **`getJiraIssue`** → **`fields`** keys, into **`fleet-config.local.yml`** (gitignored), for example:

```yaml
jira:
  cloud_id: "your-site.atlassian.net"
  field_updates:
    ai_categorization:
      field_id: "customfield_12345"
    eta_dev_done:
      field_id: "customfield_12346"
    sprint:
      field_id: "customfield_10020"
      sprint_ids_by_schedule_key:
        "303": "12345"
        "304": "12346"
```

## 5. Failure handling

- If **`jira.fail_on_error`** is **`true`**, stop on first error.
- If **`false`**, log warning and continue Fleet (default).
