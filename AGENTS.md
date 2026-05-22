# AGENTS.md

> **If you discover something that conflicts with this file, do not silently override it. Ask the user to clarify, then update this file together. When changing any convention documented here, consult the user and update this file accordingly.**

> **New to this repo?** See [`README.md`](README.md) for setup instructions, dependencies, and how to run the dev server.

## Working relationship

- No sycophancy.
- Be direct, matter-of-fact, and concise.
- Be critical; challenge my reasoning.

## Tech Debt

Tech debt compounds and slows every future decision. Treat it as a first-class cost.

- **Cut debt when you touch the code.** If you're editing a file and see unnecessary complexity, dead code, or a confusing abstraction — clean it up now. Don't create a ticket.
- **Never add debt intentionally** without an explicit, time-bounded plan to remove it.
- **Debt includes**: comments that substitute for clear naming, abstractions used only once, duplicated logic, overly generic code written for hypothetical future cases, and anything that slows onboarding.
- **TODOs do not belong in code.** If something needs doing, open a GitHub issue — that's where work is tracked, prioritized, and visible to the team. A `// TODO` in code is invisible to planning and never gets done. Delete it and open an issue instead.

## Fix Bugs When Found

If you encounter a bug while working on something else, fix it now — don't defer, don't say "out of scope," don't create a follow-up task. The only exception is if the fix is genuinely blocked by missing infrastructure.

**Test failures are bugs.** When you run tests and see failures, investigate and fix them — even if they look "pre-existing." Do not dismiss failures as "not related to my changes" or "pre-existing." If the tests fail, the suite is broken and needs fixing before moving on. The only acceptable response to a failing test is to either fix the code or fix the test.

## Development Workflow

**Safety is the first priority. Speed is the second.** Efficiency = value ÷ time.

Every feature or bugfix follows this sequence — do not skip or reorder steps:

### 1. Design for value
Before writing any code, define what success looks like:
- What problem does this solve and for whom?
- What is the expected behavior (inputs, outputs, edge cases)?
- What is explicitly out of scope?

For significant features, capture this in an ADR (why) and/or spec (how) before proceeding. For smaller changes, a clear written description in the task or PR is sufficient — but the thinking must happen first.

### 2. Safety & risk review
Before writing tests or code, explicitly consider safety. This is not optional — even small changes can have safety implications.

**User safety**
- What data does this touch? Is collection minimized? Is PII protected?
- Could this cause data loss, corruption, or unexpected state for users?
- Does it fail safe (deny by default) or fail open?
- Are there UX patterns that could mislead or harm users?

**Organizational safety**
- Does this affect auth, authorization, billing, or compliance-sensitive flows?
- Could this expose the organization to legal or financial risk?
- Are new dependencies being introduced? (Flag for review — supply chain risk)

**Societal safety**
- Could this feature be abused or weaponized?
- Does it have unintended consequences for third parties or the broader world?

**Threat model (for any security-relevant change)**
- Who are the actors (authenticated user, anonymous user, admin, external system)?
- What can each actor do that they shouldn't be able to?
- What's the blast radius if this is exploited?

If any significant risk is identified, stop and resolve it in the design — not in a follow-up ticket.

### 3. Write failing tests
Translate the design into tests before writing any implementation:
- Tests must fail when first run — if they pass immediately, either the behavior already exists or the test is wrong
- Tests define the contract: they should read like a specification of the expected behavior
- Cover the happy path, edge cases, and failure modes identified in the design step
- **Safety requirements become test cases**: unauthorized access must be tested, invalid inputs must be tested, failure modes must be tested

### 4. Implement until tests pass
Write the minimum code needed to make the tests pass:
- Do not add behavior that isn't covered by a test
- Do not gold-plate or over-engineer — solve what the tests specify
- Honor every safety constraint identified in step 2 — if a constraint can't be met, raise it before committing

### 5. Refactor for clarity and speed
After tests are green, simplify. Run `/simplify` to assist with this step.

- **Remove all comments.** If a comment explains *what* the code does, the code should be rewritten to be self-evident. If it explains *why* a decision was made, it belongs in an ADR — not inline.
- **Rename until names are obvious.**
- **Cut dead code.**
- **Flatten unnecessary complexity.** Prefer simple, direct code over clever indirection.
- **Re-run all tests after refactoring.**

## Finding Files

If you can't locate a file within 3 search attempts, stop and ask the user for the path instead of continuing to guess.

## Project Structure

This is a Django project. Review the top-level directory structure and any existing apps before making changes.

The default branch is `dev` (not `main`). Target PRs against `dev`.

## Naming

Names should be **short, descriptive, and memorable** — useful enough to understand at a glance, entertaining enough to stick.

- Prefer a single well-chosen word over a generic compound (`invoice` not `invoiceDataObject`)
- Branch and worktree names should hint at the feature without a dictionary (`fix-auth-loop`, `beacon-retry`, `dark-mode`)
- Function and variable names should read like plain English at the call site
- Avoid filler words: `Manager`, `Handler`, `Helper`, `Utils`, `Data`, `Info`
- If a name needs a comment to explain it, the name is wrong

## Git Worktrees

This repo uses git worktrees. Always verify which worktree you're in before making changes.

**Never push directly to `dev`.** All changes go through pull requests.

If the current branch is `dev`, ask the user **before doing any work**:

> You're on the `dev` branch. Want to create a worktree first?

**At the start of every task**, check the current worktree name (`git worktree list`) and compare it to the work being requested. If they don't match, stop and say so.

## Labels

When creating a PR or issue, check the repo's labels (`gh label list`) and assign any that are relevant.

## PR Review Comments

When addressing PR review comments:

- After fixing a comment, resolve it on GitHub (`gh api` to mark as resolved).
- If a comment is intentionally not addressed, reply to the comment explaining why, then resolve it.

## Commits

Proactively propose commits in blocks aligned to logical groupings of tasks or features.

**Never use `--no-verify` when committing.**

### Adversarial Review Before Commit

Before committing, run an adversarial review of the staged changes:

1. **Summarize the diff** — Describe what changed and why.
2. **Adversarial review** — Run a separate Claude Code agent (`model: "sonnet"`) with the same review prompt. Ask it to find bugs, inconsistencies, security issues, and missed edge cases. Classify issues as CRITICAL/IMPORTANT/MINOR.
3. **Address concerns** — Fix legitimate issues before committing.
4. **Second review round** — Repeat steps 2-3.

## Tooling

- Use your Edit tool for changes; Search tool for searching.
- Use Mermaid diagrams for complex systems.

## MCP Tools

When Pare MCP tools are available (prefixed with `mcp__pare-*`), prefer them over running raw CLI commands via Bash.

- Git: `mcp__pare-git__status`, log, diff, branch, show, add, commit, push, pull, checkout
- Tests: `mcp__pare-test__run`, `mcp__pare-test__coverage` (pytest, jest, vitest, mocha)
- Linting: `mcp__pare-lint__lint`, format-check, prettier-format, biome-check

## Spec Writing

When planning a new system, service, or significant feature, write a formal specification document before implementation. Follow the guidelines in [`docs/specs/spec-writing-guidelines.md`](docs/specs/spec-writing-guidelines.md).

## Code Review Checklist

When reviewing or writing code, check against these criteria.

### Security

- No hardcoded secrets, API keys, tokens, or credentials in source or tests
- Auth middleware/decorators on all protected views; authorization checked, not just authentication
- All request bodies, query params, and path params validated before use
- No raw SQL with user-supplied string interpolation — use parameterized queries or ORM
- Error responses do not leak stack traces, file paths, or internal schema details

### Python / Django

- Avoid broad `except Exception` — catch specific exceptions and handle or re-raise
- Use Django ORM; avoid raw SQL unless absolutely necessary and document why
- Migrations committed alongside model changes
- No blocking I/O in request handlers — offload to background tasks
- `select_related` / `prefetch_related` used to avoid N+1 queries

### Architecture

- Business logic in service modules or model methods, not in views
- No direct DB queries outside the data layer
- Background tasks use a task queue (Celery), not threads or subprocesses
- Cross-app imports flow in one direction; avoid circular imports
