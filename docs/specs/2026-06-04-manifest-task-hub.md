# Manifest: Personal Task Hub Specification

Status: Draft v1

Purpose: Turn quayside into Erik's single AI-queryable task hub, computing what to do next across all his work and keeping tasks bidirectionally consistent with GitHub issues.

## 1. Problem Statement

Manifest is the set of quayside-core additions and one Claude Code skill that let Erik manage his entire workload (circumpolar.ai, beadedcloud.com, quayside, personal) from the terminal. Quayside holds the tasks, their dependencies, and their groupings; Manifest adds the computation and the ingestion that make the pile actionable.

Operational problems it solves:

- "What can I start right now?" (the unblocked set across all projects).
- "What is blocked, and by what?" (the dependency chain).
- "What can AI do without me?" (the AI-doable, unblocked subset).
- "How big is the remaining pile?" (coarse size rollup).
- "Keep my GitHub issues and my task hub in agreement" (two-way sync).

Important boundary: Manifest is NOT a replacement for GitHub issues as the team's canonical per-repo dev tracker, NOT a time-tracking or billing system, and NOT a forecasting/burndown tool. It does not predict completion dates.

## 2. Goals and Non-Goals

### Goals

- A `/api/v1/whatsnext/` endpoint returns, for a user across one or more projects: the unblocked task set, the critical path, and rollup counts including how many are AI-doable.
- Every `Task` carries a `capability` (`ai-doable` | `ai-assisted` | `human-only` | `unknown`) and an optional `githubRef` linking it to a GitHub issue.
- Coarse sizing: a task's size is expressed S/M/L and stored as representative `durationMinutes`.
- Two-way GitHub sync under field-level ownership, idempotent and loop-safe.
- One-way create-only ingestion from email, pasted notes, and `Keep/*.md`.
- A Claude Code skill (`/manifest`) that reads what's-next, lets Erik focus on one task, edit tasks in plain language, and trigger a sync.

### Non-Goals

- No webhooks in v1 (sync is pull-on-demand from the skill). Webhook transport is a later slice.
- No two-way sync for email/notes/Keep sources (create-only).
- No completion-date forecasting, velocity, or burndown.
- No new quayside frontend. The terminal skill is the interface.
- No resource leveling or multi-assignee scheduling.

## 3. System Overview

### Main Components

1. `whatsnext-endpoint` (quayside-core)
   - Computes unblocked set and critical path from the task graph.
   - Returns rollups (counts, total size, AI-doable count).
   - Read-only; no mutation.

2. `github-sync` (quayside-core)
   - Pulls issues into tasks and pushes task changes to issues.
   - Enforces field-level ownership and loop prevention.
   - Pull-on-demand (no webhook in v1).

3. `ingest` (Claude Code skill side)
   - Converts email threads, pasted notes, and `Keep/*.md` entries into quayside tasks via the existing task API.
   - Create-only; sets `source` provenance.

4. `manifest-skill` (Claude Code skill)
   - Thin client: calls `whatsnext`, renders focus/epics/blocked views, edits tasks in plain language, triggers sync.

### Abstraction Levels

- Graph layer: the dependency DAG over `Task` nodes (`parentTaskID` tree edges + `otherTaskDependencies` constraint edges). Concern: correctness of unblocked/critical-path computation.
- Sync layer: reconciliation between quayside tasks and GitHub issues. Concern: identity, conflict resolution, idempotency.
- Interface layer: the skill. Concern: presentation and plain-language editing.

### External Dependencies

- GitHub REST API (issues read/write), authenticated with a GitHub token held by the skill/server.
- Quayside REST API v1 (existing), authenticated with Erik's quayside `apiToken`.
- Gmail MCP (already connected) for email ingestion, invoked from the skill side.
- Local filesystem for `Keep/*.md` ingestion, read from the skill side.

## 4. Core Domain Model

### Task (additions to existing model)

Represents a unit of work. Existing fields unchanged (`projectID`, `parentTaskID`, `name`, `description`, `otherTaskDependencies`, `contributorIDs`, `statusId`, `durationMinutes`, `priority`, dates). New fields:

Fields:

- `capability` (StringField)
  - One of `ai-doable`, `ai-assisted`, `human-only`, `unknown`. Default `unknown`. Whether an AI agent can complete the task alone, needs a human in the loop, or must be done by a human.
- `githubRef` (StringField, nullable)
  - Canonical form `owner/repo#number` (e.g. `beadedcloud/circumpolar-ai#187`). Null for quayside-native tasks. Durable link used for sync idempotency. Unique per task.
- `source` (StringField)
  - Provenance of the task: `quayside`, `github`, `email`, `notes`, `keep`. Default `quayside`. Set at creation, never overwritten by sync.
- `syncHash` (StringField, nullable)
  - Hash of the GitHub-owned fields (title, body, state, assignee) as of the last successful sync. Used to detect whether the GitHub side changed since last sync. Null for non-synced tasks.
- `lastSyncedAt` (DateTimeField, nullable)
  - UTC timestamp of last successful sync for this task.

### Size mapping (not a stored enum; a convention over `durationMinutes`)

- S = 60 minutes
- M = 240 minutes
- L = 960 minutes

The skill presents S/M/L; the API stores `durationMinutes`. A task whose `durationMinutes` does not match a bucket is reported by the skill at its nearest bucket for display, value preserved.

### Normalization Rules

- `githubRef`: lowercased `owner/repo`, literal `#`, decimal issue number. No URL forms stored; the skill resolves URLs to this form before writing.
- Capability values are a closed set; any other value is rejected at the API boundary and treated as `unknown` on read.

## 5. whatsnext Endpoint

### Discovery / Resolution

`GET /api/v1/whatsnext/` with `@apiKeyRequired`. Query params:

- `projectID` (optional, repeatable): restrict to one or more projects. Absent means all projects the user belongs to.
- `capability` (optional): filter the unblocked set (e.g. `ai-doable`).

### Response Schema

```json
{
  "unblocked": [
    {"id": "...", "name": "...", "projectID": "...", "capability": "ai-doable",
     "size": "M", "durationMinutes": 240, "githubRef": "owner/repo#12"}
  ],
  "blocked": [
    {"id": "...", "name": "...", "blockedBy": ["taskId", "taskId"]}
  ],
  "criticalPath": ["taskIdA", "taskIdB", "taskIdC"],
  "rollup": {
    "totalTasks": 0, "unblockedCount": 0, "aiDoableUnblocked": 0,
    "totalDurationMinutes": 0, "byCapability": {"ai-doable": 0, "ai-assisted": 0, "human-only": 0, "unknown": 0}
  }
}
```

### Validation and Error Surface

- `Unauthorized`: missing/invalid `apiToken` (existing decorator behavior).
- `CycleDetected`: the dependency graph contains a cycle. The endpoint returns 409 with the offending task ids rather than looping. A task list must be a DAG.
- A task referencing a non-existent dependency id is treated as having no such edge and logged, not fatal.

### Behavioral Contract

A task is "unblocked" when every id in its `otherTaskDependencies` resolves to a task whose status is in a terminal/done column, and it has no incomplete child tasks (a parent is not actionable until its children are done). A task is "blocked" otherwise, and `blockedBy` lists the unfinished dependency and child ids. "Done" is determined by the project's terminal `Status` (the highest-`order` status, or a status flagged done; see Configuration).

### Critical Path

Longest duration-weighted path through the DAG, summing `durationMinutes` along dependency edges. Computed by topological order then longest-path relaxation. Reported as an ordered list of task ids. Ties broken by higher `priority`, then earlier `endDate`.

## 6. github-sync Subsystem

### Discovery / Resolution

Sync operates over the set of tasks with `source` in {`github`, `quayside`} that either have a `githubRef` or are tagged for export. Triggered on demand by the skill (`POST /api/v1/sync/github/` with optional `projectID` and `repo` scope). v1 has no webhook.

### Field Ownership

| Field | Owner | Direction |
|---|---|---|
| title (`name`) | GitHub | GitHub to quayside |
| body (`description`) | GitHub | GitHub to quayside |
| open/closed state | GitHub | GitHub to quayside (closed issue moves task to terminal status) |
| assignee (`contributorIDs`) | GitHub | GitHub to quayside |
| `otherTaskDependencies` | quayside | quayside to GitHub (rendered as a task-list/footer in the issue body region quayside owns) |
| epic grouping (`parentTaskID`) | quayside | quayside to GitHub (as a label or footer reference) |
| size (`durationMinutes`) | quayside | quayside to GitHub (label `size:M`) |
| `capability` | quayside | quayside to GitHub (label `ai-doable` etc.) |

GitHub-owned fields flow into quayside; quayside-owned fields flow out as labels and a delimited footer block in the issue body. Each side writes only its own fields, so there is no field that both sides author.

### Loop Prevention

Quayside-authored content in an issue lives between explicit delimiters (`<!-- quayside:start -->` ... `<!-- quayside:end -->`). When computing `syncHash`, the quayside-owned region is stripped first, so quayside's own writes never look like a GitHub-side change. A sync that would write identical content is skipped.

### Reconciliation (per task with a `githubRef`)

1. Fetch the issue. Compute `currentHash` over GitHub-owned fields with the quayside region stripped.
2. If `currentHash != syncHash`, GitHub changed: copy GitHub-owned fields into the task. Update `syncHash`.
3. Recompute quayside-owned labels + footer. If they differ from what is on the issue, write them.
4. Set `lastSyncedAt`. Persist.

### New issues and new tasks

- A GitHub issue with no matching `githubRef` in the target project: create a task with `source=github`, `githubRef` set, `capability=unknown`, default size M.
- A quayside-native task flagged for export: create an issue, set `githubRef`, write quayside-owned region.

### Validation and Error Surface

- `GitHubAuthError`: token missing or rejected. Aborts the run, reports which repo.
- `RepoNotFound` / `IssueNotFound`: skip that item, continue, report.
- Rate limiting: respect GitHub `Retry-After`; the run is resumable because each task carries its own `syncHash`/`lastSyncedAt`.

## 7. ingest (skill-side, create-only)

- Email: skill reads a Gmail thread (via Gmail MCP), summarizes into a task `name`/`description`, sets `source=email`, posts to `/api/v1/tasks/`.
- Notes: Erik pastes call/meeting notes; skill extracts one or more tasks, `source=notes`.
- Keep: skill reads a `Keep/*.md` entry, proposes tasks, `source=keep`.

All three are one-way. They never sync back. Deduplication is best-effort by title against open tasks in the chosen project, surfaced to Erik before creation.

## 8. Observability

- Sync logging: per run, log repo scope, counts (pulled, pushed, skipped-identical, errors), and any skipped item with reason. Verbose, no comments-in-code (per quayside conventions).
- whatsnext logging: log requested scope and result counts. Log `CycleDetected` with offending ids at error level.
- No metrics dashboard in v1.

## 9. Failure Model

Failure classes:

1. Auth (quayside token or GitHub token invalid): abort the affected operation, surface clearly to the skill.
2. Graph (cycle): whatsnext returns 409 with offending ids; no partial/garbage path.
3. External (GitHub API down/rate-limited): sync degrades gracefully, processes what it can, resumes next run via per-task state.
4. Data (dangling dependency id): logged, treated as no edge, non-fatal.

Restart recovery: sync holds no in-memory state across runs; `githubRef`, `syncHash`, `lastSyncedAt` on each task are the full resumable state. A fresh run reconciles from the database.

Operator intervention: Erik can null a task's `githubRef` to detach it from GitHub, or change `capability`/size directly via the skill.

## 10. Security

- Trust boundary: the quayside API trusts a valid `apiToken`. The GitHub token is a secret held server-side (or in the skill's environment for v1) and never logged.
- Secret handling: GitHub token and quayside `apiToken` are referenced from environment/secret store, never written to logs or issue bodies.
- Sync writes only to repos Erik's token can access; no privilege escalation.
- The quayside-owned region in issue bodies is delimited and contains no secrets, only task metadata.

## 11. Reference Algorithms

```
function whatsnext(user, projectIDs, capabilityFilter):
    tasks = load_tasks(user, projectIDs)
    assert_dag(tasks)            # raise CycleDetected with ids on failure
    done = terminal_status_ids(projects_of(tasks))
    unblocked = []
    blocked = []
    for t in tasks:
        deps = resolve(t.otherTaskDependencies, tasks)
        kids = children(t, tasks)
        unfinished = [d for d in deps if d.statusId not in done]
                   + [k for k in kids if k.statusId not in done]
        if unfinished is empty and t.statusId not in done:
            unblocked.append(t)
        elif t.statusId not in done:
            blocked.append((t, ids(unfinished)))
    if capabilityFilter: unblocked = [t for t in unblocked if t.capability == capabilityFilter]
    critical = longest_weighted_path(tasks, weight = durationMinutes)
    return assemble(unblocked, blocked, critical, rollup(tasks))

function sync_task(task, gh):
    issue = gh.get(task.githubRef)
    currentHash = hash(strip_quayside_region(github_owned_fields(issue)))
    if currentHash != task.syncHash:
        apply_github_fields_to(task, issue)   # title, body, state, assignee
        task.syncHash = currentHash
    desired = render_quayside_region(task)    # deps, epic, size, capability
    if desired != current_quayside_region(issue):
        gh.update_body_region(issue, desired)
        gh.set_labels(issue, quayside_labels(task))
    task.lastSyncedAt = now_utc()
    save(task)
```

## 12. Test and Validation Matrix

Core Conformance (quayside-core, pytest, TDD per quayside CLAUDE.md):

- Model: `capability` defaults to `unknown`; invalid value rejected; `githubRef` normalization; `source` immutable across update.
- whatsnext: unblocked detection with dependency edges; parent blocked by unfinished child; capability filter; rollup counts; `CycleDetected` on a cycle; dangling dependency id ignored.
- Critical path: known small DAG returns expected ordered path; tie-break by priority then endDate.
- Sync: GitHub-only field change pulls in; quayside-only change pushes out; identical content is skipped (loop prevention); quayside region stripped from `syncHash`; new issue creates task; detached `githubRef` stops sync.

Real Integration (manual, gated on Slice 0):

- Skill authenticates to quayside with a real token and reads Erik's actual tasks.
- One real issue round-trips: edit on GitHub appears in quayside; size/capability set in quayside appears as labels on the issue.

## Build Slices (execution order)

- Slice 0: verify a stable quayside API token exists and the skill can make one authenticated read against real data. Blocks everything.
- Slice 1: `capability`, `githubRef`, `source`, `syncHash`, `lastSyncedAt` fields + `/api/v1/whatsnext/` (read-only). Skill renders what's-next/blocked/focus.
- Slice 2: `github-sync` pull (GitHub to quayside) only.
- Slice 3: `github-sync` push (quayside-owned region + labels) and loop prevention.
- Slice 4: ingest (email, notes, Keep), create-only.
- Slice 5 (later): webhook transport to replace pull-on-demand.
