# ADR: Quayside as Erik's Personal Task Hub (Manifest)

## ADR Author/s

Erik Williams (with Claude)

## Update Date

2026-06-04

## Status

Proposed

## Who should be notified of ADR changes?

@quayside-app maintainers

## Context

Erik runs three concurrent efforts (circumpolar.ai, beadedcloud.com, quayside) and cannot hold the combined workload in his head. Tasks are scattered across GitHub issues (canonical per-repo dev work), email, customer calls, and `Keep/*.md` idea files. There is no single surface that answers: what can I start now, what is blocked and by what, what can AI do unattended, and roughly how big is the remaining pile.

He wants one AI-queryable system to manage work over time: see dependencies, see epics (collections of tasks), focus on a single task, make changes in plain language, and ingest tasks from multiple sources. It must work natively with Claude Code.

What changed to make this urgent now: quayside's own MVP definition (`quayside_personal/MVP.md`) requires a working "What's Next card" plus a one-week dogfood. Erik's personal workload is the dogfood. Building his task hub and proving quayside's core value are the same work.

Constraints and forces:

- Quayside already models the hard parts: hierarchical tasks (`parentTaskID`), explicit dependency edges (`otherTaskDependencies`), estimation (`durationMinutes`), assignees (`contributorIDs`), Kanban statuses, and a fully authenticated REST API that an external process can drive.
- Quayside's stack (MongoEngine, Django server-rendered templates, GPT-3.5) is dated but does not block this use case, because the interface is a Claude Code skill calling the API, not a new frontend.
- GitHub issues remain the canonical per-repo dev tracker for the team. Any integration must not undermine that.
- Erik explicitly chose the heavier path on two forks (see Decision): compute the what's-next brain in quayside-core, and do two-way GitHub sync rather than one-way import.

## Options Considered

### Option 1: GitHub-native backend + thin Claude Code skill (no quayside changes)

Use GitHub Issues + Projects v2 (native sub-issues, issue dependencies, custom fields) as the database; a skill is the entire interface.

- **Pros:** Zero hosting, reuses canonical task source, fastest to first use, no sync problem because there is one source of truth.
- **Cons:** Does not advance quayside the product. Does not dogfood. Cross-repo unification depends on GitHub Projects setup. AI-capability is a label convention, not a first-class concept.

### Option 2: Dogfood quayside, brain in quayside-core, two-way GitHub sync (chosen)

Quayside is the hub and the graph engine. A new `/api/v1/whatsnext/` endpoint computes the unblocked set and critical path. A sync module keeps tasks and GitHub issues bidirectionally consistent under field-level ownership. Email, call notes, and `Keep/*.md` are one-way create-only sources. A Claude Code skill is the terminal interface.

- **Pros:** Builds the exact engine quayside's MVP What's Next card needs (build once, use from terminal now, graft into product later). Forces a real dogfood, surfacing product gaps Erik will feel and fix. AI-capability becomes a first-class field. Quayside genuinely becomes the hub, not a mirror.
- **Cons:** Most build cost. Two-way sync introduces identity mapping, conflict resolution, and loop-prevention concerns. Couples Erik's personal workload to quayside's production MongoDB (an Atlas outage takes down his task system).

### Option 3: Do Nothing

Keep status scattered across GitHub, email, `Keep/*.md`, and memory; rely on the existing `/whats-next` skill reading `quayside_personal` markdown.

- **Pros:** No work.
- **Cons:** The original problem persists. No dependency view, no cross-source unification, no AI-doable channel, no dogfood.

## Decision

Adopt Option 2. Quayside becomes Erik's personal task hub, dogfooding the product.

The five load-bearing decisions, all confirmed with Erik on 2026-06-04:

1. **Backend: dogfood quayside.** The personal task data lives in quayside's production database. This is deliberate dogfooding aligned with the MVP.
2. **Estimation: coarse sizing only.** Tasks carry an S/M/L size mapped to representative `durationMinutes` (60 / 240 / 960). No hand-maintained hour estimates, no burndown, no completion-date forecasting in v1. Rollups are counts and total size.
3. **Sources:** GitHub issues (two-way sync), email, pasted call/meeting notes, and `Keep/*.md` (the latter three are one-way create-only).
4. **What's-next brain: quayside-core.** A `/api/v1/whatsnext/` endpoint owns the unblocked-set and critical-path computation. The skill is a thin client. This is the same engine the MVP What's Next card consumes.
5. **Sync conflict resolution: field-level ownership.** GitHub owns title, body, open/closed state, and assignee. Quayside owns dependencies, epic grouping, sizing, and capability. Each field has exactly one authoritative side, so true conflicts are rare by construction.

Rationale: the heavier path is justified because it is not throwaway tooling. Every piece (the what's-next engine, the capability field, the sync layer) advances quayside toward its own MVP while solving Erik's problem. The lighter GitHub-native option would have solved the personal problem faster but produced nothing reusable for the product.

## Consequences

### Positive

- One AI-queryable surface across all three efforts, driven from Claude Code.
- The what's-next engine and What's Next card MVP feature get built as a byproduct.
- A real dogfood exposes quayside's gaps under genuine daily use.
- `capability` becomes a first-class, generally useful field (not a personal hack), letting any agent pick up unblocked AI-doable work unattended.
- GitHub issues stay canonical for the team; quayside aggregates without replacing them.

### Negative

- Two-way sync is the largest source of risk and ongoing maintenance: identity mapping, conflict resolution, and loop prevention must all be correct. Mitigated by field-level ownership and origin-stamping (see spec).
- Erik's personal workload depends on quayside production uptime (Atlas). Accepted as part of dogfooding.
- Adds two `Task` fields and a sync subsystem to a codebase that currently has no external integrations.
- The skill needs a stable, long-lived quayside API token for headless use. Slice 0 verifies this exists before anything else is built.

## Spec

- Spec: [docs/specs/2026-06-04-manifest-task-hub.md](../specs/2026-06-04-manifest-task-hub.md)

## References

- Related docs: `quayside_personal/MVP.md`, `quayside_personal/STATUS.md`
- Related work: `whats-next-card` branch (What's Next card UI), `/whats-next` and `/checkout` Claude Code skills
- Data model: `api/models.py` (Task, Project)
- API: `api/urls.py`, `api/views/v1/`

## Consensus

Erik Williams: agreed on all five decisions (2026-06-04).
