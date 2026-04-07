# CLAUDE.md

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

- **Remove all comments.** If a comment explains *what* the code does, the code should be rewritten to be self-evident. If it explains *why* a decision was made, it belongs in an ADR — not inline. Comments are a maintenance liability and bloat the context window for AI tools.
- **Rename until names are obvious.** A future developer (or AI) should understand a function or variable without any surrounding context.
- **Cut dead code.** Unused variables, unreachable branches, and obsolete abstractions slow onboarding and obscure intent.
- **Flatten unnecessary complexity.** Prefer simple, direct code over clever indirection. Three readable lines beat one cryptic expression.
- **Ask: would a new developer understand this in 30 seconds?** If not, simplify further — don't add a comment.
- **Re-run all tests after refactoring.** Refactoring can break things. Green before refactor does not guarantee green after.

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

Wait for the user to confirm before proceeding. Creating a worktree up front is the preferred workflow — it avoids having to juggle branch creation later.

If the user declines the worktree, continue on `dev` but create a new branch before committing. Do not commit directly to `dev`.

**At the start of every task**, check the current worktree name (`git worktree list`) and compare it to the work being requested. If they don't match — e.g., you're in `fix-auth-loop` but the task is about billing — stop and say so:

> You're in worktree `fix-auth-loop` but this looks like billing work. Want to create a new worktree first?

Don't silently proceed in the wrong tree.

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
