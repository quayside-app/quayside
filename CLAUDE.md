# CLAUDE.md

> **If you discover something that conflicts with this file, do not silently override it. Ask the user to clarify, then update this file together. When changing any convention documented here, consult the user and update this file accordingly.**

## Working relationship

- No sycophancy.
- Be direct, matter-of-fact, and concise.
- Be critical; challenge my reasoning.
- Don't include timeline estimates in plans.

## Fix Bugs When Found

If you encounter a bug while working on something else, fix it now — don't defer, don't say "out of scope," don't create a follow-up task. The only exception is if the fix is genuinely blocked by missing infrastructure.

**Test failures are bugs.** When you run tests and see failures, investigate and fix them — even if they look "pre-existing." Do not dismiss failures as "not related to my changes" or "pre-existing." If the tests fail, the suite is broken and needs fixing before moving on. The only acceptable response to a failing test is to either fix the code or fix the test.

## Test-First Development

Write a failing test before implementing a feature or bugfix. The test should demonstrate the expected behavior or reproduce the bug, then write the code that makes it pass.

## Finding Files

If you can't locate a file within 3 search attempts, stop and ask the user for the path instead of continuing to guess.

## Project Structure

This is a Django project. Review the top-level directory structure and any existing apps before making changes.

The default branch is `dev` (not `main`). Target PRs against `dev`.

## Git Worktrees

This repo uses git worktrees. Always verify which worktree you're in before making changes.

**Never push directly to `dev`.** All changes go through pull requests.

If the current branch is `dev`, ask the user **before doing any work**:

> You're on the `dev` branch. Want to create a worktree first?

Wait for the user to confirm before proceeding. Creating a worktree up front is the preferred workflow — it avoids having to juggle branch creation later.

If the user declines the worktree, continue on `dev` but create a new branch before committing. Do not commit directly to `dev`.

## Labels

When creating a PR or issue, check the repo's labels (`gh label list`) and assign any that are relevant.

## PR Review Comments

When addressing PR review comments:

- After fixing a comment, resolve it on GitHub (`gh api` to mark as resolved).
- If a comment is intentionally not addressed, reply to the comment explaining why, then resolve it.

## Commits

Proactively propose commits in blocks aligned to logical groupings of tasks or features. When a coherent unit of work is complete, ask the user if they'd like to commit rather than waiting for them to bring it up.

**Never use `--no-verify` when committing.** Pre-commit hooks exist for a reason. If a hook fails, fix the underlying issue — don't bypass the hooks.

### Adversarial Review Before Commit

Before committing, run an adversarial review of the staged changes:

1. **Summarize the diff** — Describe what changed and why.
2. **Adversarial review** — Run a separate Claude Code agent (`model: "sonnet"`) with the same review prompt. Ask it to find bugs, inconsistencies, security issues, and missed edge cases. Classify issues as CRITICAL/IMPORTANT/MINOR.
3. **Address concerns** — Fix legitimate issues before committing.
4. **Second review round** — Repeat steps 2-3. The second round catches inconsistencies introduced by fixes.

## Tooling

- Use your Edit tool for changes; Search tool for searching.
- Use Mermaid diagrams for complex systems.

## MCP Tools

When Pare MCP tools are available (prefixed with mcp\_\_pare-\*), prefer them over running raw CLI commands via Bash. Pare tools return structured JSON with ~85% fewer tokens than CLI output.

- Git: mcp**pare-git**status, log, diff, branch, show, add, commit, push, pull, checkout
- Tests: mcp**pare-test**run, mcp**pare-test**coverage (pytest, jest, vitest, mocha)
- Builds: mcp**pare-build**tsc, build, esbuild, vite-build, webpack
- Linting: mcp**pare-lint**lint, format-check, prettier-format, biome-check, biome-format
- npm: mcp**pare-npm**install, audit, outdated, list, run, test, init

## Spec Writing

When planning a new system, service, or significant feature, write a formal specification document before implementation. Follow the guidelines in [`docs/specs/spec-writing-guidelines.md`](docs/specs/spec-writing-guidelines.md). Key requirements:

- **Structure**: Problem Statement, Goals/Non-Goals, System Overview, Domain Model, per-subsystem specs, Observability, Failure Model, Security, Reference Algorithms, Test Matrix, Implementation Checklist
- **Every config field** gets type + default + dynamic reload behavior
- **Every operation that can fail** gets a named error class and explicit recovery behavior
- **Required vs optional** is always explicit — use validation profiles (Core, Extension, Real Integration)
- **Reference pseudocode** for complex algorithms — language-agnostic
- **Test matrix** as specific testable behaviors, not vague categories
- **State what you don't prescribe** — "implementation-defined" for things that vary by deployment

## Code Review Checklist

When reviewing or writing code, check against these criteria.

### Security

- No hardcoded secrets, API keys, tokens, or credentials in source or tests
- No `print()` / logger calls printing sensitive headers, tokens, or PII
- Auth middleware/decorators on all protected views; authorization checked, not just authentication
- All request bodies, query params, and path params validated before use
- No raw SQL with user-supplied string interpolation — use parameterized queries or ORM
- Error responses do not leak stack traces, file paths, or internal schema details
- No `eval()` or unsafe deserialization of user input
- If any new dependencies were added, flag them for human review

### Python / Django

- Avoid broad `except Exception` — catch specific exceptions and handle or re-raise
- No unsafe `# type: ignore` without an explanatory comment
- Use Django ORM; avoid raw SQL unless absolutely necessary and document why
- Migrations committed alongside model changes
- No blocking I/O in request handlers — offload to background tasks (Celery, etc.)
- `select_related` / `prefetch_related` used to avoid N+1 queries
- No `DEBUG = True` or development settings leaking into production paths

### Architecture

- Business logic in service modules or model methods, not in views — views do input parsing, call services, return responses
- No direct DB queries outside the data layer
- Template context kept minimal — heavy computation belongs in the view or service layer
- Background tasks use a task queue (Celery), not threads or subprocesses
- Cross-app imports flow in one direction; avoid circular imports
