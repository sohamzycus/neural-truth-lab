---
description: Perform Root Cause Analysis (RCA) of an issue using Code Oracle MCP and optionally attach the RCA report to a JIRA ticket.
tools: ['user-Code-oracle/codeoracle_query', 'user-Code-oracle/codeoracle_graph', 'user-Atlassian-MCP-Server/mcp_auth']
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Parsing User Input

1. **Issue description** (required): Extract the issue, bug, or symptom to analyze (e.g. "NullPointerException in SupplierPaymentTerm", "invoice approval workflow stuck", "tax calculation mismatch").
2. **JIRA ticket** (optional): If the user mentions a JIRA issue key (e.g. `PROJ-123`, `EINV-456`, `JIRA-789` or "ticket PROJ-123"), capture it for attaching the RCA. Common patterns: standalone key, "JIRA: PROJ-123", "ticket PROJ-123", "issue EINV-456".

## Outline

### 1. Authenticate Atlassian MCP (if JIRA key is present)

If a JIRA issue key was parsed from the user input:

- Call the `mcp_auth` tool for server **user-Atlassian-MCP-Server** with arguments `{}` so the user can authenticate and all Atlassian/JIRA tools are available for the attach step later.

### 2. Gather context with Code Oracle

Use the **Code Oracle MCP** to understand the codebase around the issue:

- **codeoracle_query**: Ask natural-language questions to find root cause. Examples:
  - "Where is [component/exception/feature from issue] implemented or used?"
  - "What could cause [symptom from issue]? Trace code paths and error handling."
  - "Where is [class/method from issue] called and how is it validated?"
- Use multiple focused queries if needed (e.g. locate code, then trace callers, then check configuration or error paths).
- Optionally use **codeoracle_graph** (e.g. `call`, `dependency`, or `api`) for the relevant repo to visualize call chains or dependencies that might explain the issue.

Restrict queries to the current repository when appropriate (use `repo_filter` if the Code Oracle index includes multiple repos and the issue is repo-specific).

### 3. Produce RCA report

Synthesize a **Root Cause Analysis** report in Markdown with:

- **Summary**: One-line description of the issue and likely root cause.
- **Symptom**: What was observed (from user input).
- **Root cause**: Technical explanation (code paths, missing checks, config, data, or integration).
- **Evidence**: File paths, class/method names, and code or graph references from Code Oracle answers.
- **Contributing factors**: Optional (e.g. config, environment, race conditions).
- **Recommendations**: Suggested code or process changes to fix or mitigate.

Keep the report concise and actionable.

### 4. Attach RCA to JIRA (if ticket key was provided)

If a JIRA issue key was parsed in step "Parsing User Input":

- Use the **Atlassian MCP server** (user-Atlassian-MCP-Server) to add the RCA report as a comment on that issue.
- Prefer a tool that adds a comment to an issue (commonly named like `jira_add_comment` or similar). If the tool schema differs, use the equivalent that accepts:
  - **issue_key** (or **issueIdOrKey**): The parsed JIRA key (e.g. `PROJ-123`).
  - **comment** (or **body**): The full RCA report text (Markdown is acceptable; JIRA often supports Markdown or stored format).
- If no "add comment" tool is available after authentication, list the available tools and use the appropriate one, or report to the user that the RCA was generated but could not be attached and paste the report in the chat.

### 5. Confirm to user

- If attached to JIRA: "RCA completed and attached to [JIRA_KEY]. Summary: [one-line summary]."
- If no JIRA key: "RCA completed. [One-line summary]. Paste the report above into the ticket if needed."

## Operating Principles

- **Code Oracle first**: Base the RCA on Code Oracle query (and optionally graph) results; do not invent code paths.
- **One repo by default**: Prefer scoping Code Oracle queries to the current repository unless the issue clearly spans repos.
- **JIRA optional**: Attach to JIRA only when the user provided a JIRA issue key; otherwise output the report in chat only.
- **No file writes**: This command does not create or edit files; it only uses MCP tools and outputs the RCA in the conversation (and into JIRA when requested).

## Context

$ARGUMENTS
