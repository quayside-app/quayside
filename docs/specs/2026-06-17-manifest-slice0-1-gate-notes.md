# Manifest Slices 0-1: Security + Pre-Catch Gate Notes

Status: gate complete, implementation not started. Companion to
[2026-06-04-manifest-task-hub.md](2026-06-04-manifest-task-hub.md) and ADR
[2026-06-04-quayside-as-personal-task-hub.md](../decisions/2026-06-04-quayside-as-personal-task-hub.md).

These are the step-3 (security) and step-4 (pre-catch) outputs of the dev
workflow, recorded so execution starts from a contract instead of re-deriving.

## Slice 0: token mechanism (verified by code reading, live check deferred)

The headless-token question is answered at the code level. Live confirmation
against production was intentionally deferred (requires explicit prod
authorization; see "Live check recipe" below).

- The quayside `apiToken` is a JWT with payload `{"userID": ...}` signed HS256
  with `API_SECRET` (`api/utils.py:createEncodedApiKey`). It carries **no `exp`
  and no `iat`**, so it never expires and is **deterministic**: for a fixed
  `API_SECRET` + `userID`, `createEncodedApiKey(userID)` always returns the same
  string. This is exactly the stable, long-lived headless credential Slice 0
  needs. Slice 0 is retrieval, not a build.
- The stored `User.apiKey` is that JWT, Fernet-encrypted with `API_SECRET + "="`
  as the key (`encryptApiKey`/`decryptApiKey`). The `@apiKeyRequired` decorator
  passes only when the presented token equals `decryptApiKey(user.apiKey)`
  (`api/decorators.py:44`). So a token works only if the user has a stored
  `apiKey` created under the current `API_SECRET`.
- `API_SECRET` and the prod Mongo creds live in `~/repos/quayside/.env`, which
  points at production Atlas (`quayside-cluster.ry3otj1.mongodb.net`, db
  `quayside`, per `api/apps.py`).

### Live check recipe (run before the Slice-1 integration test)

Read-only confirmation that the token authenticates against real data:

1. Load `~/repos/quayside/.env`; connect to prod Atlas.
2. Find Erik's `User` (`email__icontains="erik"`); read `id` + `apiKey`.
3. `token = decryptApiKey(user.apiKey)`; assert it decodes to that `userID` and
   that `createEncodedApiKey(userID) == token` (proves deterministic/long-lived).
4. `GET https://quayside.app/api/v1/projects/` with `Authorization: <token>`;
   expect 200 and his real projects.
5. Never print the token or `API_SECRET`; report only project count/names.

This needs **explicit prod authorization** in the session prompt — the safety
classifier blocks unauthorized prod DB + live-secret reads, correctly. If the
token path is broken, the whole skill-driven approach changes, so do this before
building Slice 2.

## Security gate (step 3)

Trust boundary: auth = JWT `apiToken` (authentication), authorization = project
membership (`Project.objects.filter(userIDs=userID)`), applied by every existing
v1 view. whatsnext sits behind the same boundary; sync adds an outbound GitHub
trust edge.

Findings:

1. **CRITICAL design requirement — whatsnext must scope to project membership.**
   The JWT carries only `userID`, no scopes. The only thing between user A and
   user B's tasks is the `userIDs=userID` project filter (`tasks.py:172-176`).
   whatsnext must replicate it or it leaks every user's task graph to any valid
   token (OWASP A01). -> Slice-1 test: user A's token sees zero of user B's tasks.
2. **HIGH, informational — apiToken is non-expiring and full-account.** Good for
   Slice 0 (stable headless token). Flip side: the token is full task CRUD across
   all the user's projects. Store it in an env var / secret store on the skill
   side, never committed, never logged.
3. **MEDIUM, pre-existing, not introduced here — `API_SECRET` reuse.** Same
   secret signs JWTs and is the Fernet key (`utils.py:32,67-69`). One compromise
   both forges tokens and decrypts stored keys. Out of scope for Manifest;
   ticket-worthy.
4. **MEDIUM, Slice 2/3 — `githubRef` SSRF/path-injection.** Validate the
   `owner/repo#number` form (spec normalization rule) before building any GitHub
   API URL from stored data.
5. **MEDIUM, Slice 2/3 — secret-in-logs discipline.** Verbose sync logging (spec
   §8) must never emit the GitHub token, the apiToken, or raw issue bodies.

Open decision (NOT one of the five locked ADR decisions; surface at Slice 2, do
not decide silently): **where the GitHub token lives.** Spec §10 leaves it open
("server-side or in the skill's environment for v1") but §6 defines
`POST /api/v1/sync/github/`, implying the server holds the PAT. Fork: a personal
GitHub PAT in quayside prod Cloud Run env, vs. keeping GitHub calls skill-side
and pushing field updates through the existing task API. Slice 1 needs no GitHub
token, so this blocks nothing now.

### Slice-1 security requirements -> test cases

- whatsnext scoped to `userIDs=userID` (A01): user A sees none of user B's tasks.
- `@apiKeyRequired` on the view: no/invalid token -> 401.
- `projectID` validated as ObjectId -> 400 not 500 on garbage; `capability`
  filter accepted only from the closed set.
- `CycleDetected` -> 409 with offending ids, never loops (DoS-safe).
- dangling dependency id -> treated as no-edge, logged, non-fatal.

## Pre-catch gate (step 4)

Blast radius:

- `TaskSerializer` uses `fields="__all__"` (`serializers.py:71-74`), so the five
  new fields auto-serialize. Adding them is additive and backward-compatible;
  existing GET/POST/PUT/DELETE keep working. MongoEngine `strict=False` means no
  migration for existing docs.
- Existing tests do not assert Task shape (`tests/test_apis.py` covers
  Project/Status; `tests/test_models.py` empty; `tests/test_views.py` covers
  Kanban auth only). Adding fields won't flip them — **unless** a new field is
  `required=True` without a default. So all new fields must default.
- Frontend (`app/static/app/js/tree.js`) reads only `statusId`; no breakage.

Care items for Slice 1:

1. **Field defaults:** `capability` default `"unknown"`; `source` default
   `"quayside"`; `githubRef`/`syncHash`/`lastSyncedAt` default null. None
   `required=True`.
2. **`source` immutability:** `updateTask` (`tasks.py:253`) uses `partial=True`,
   which would let any caller overwrite `source`. Enforce immutability (strip
   `source` from update payloads, re-apply stored value after save).
3. **`capability` validation:** reject values outside the closed set at the API
   boundary; treat unknown-on-read as `"unknown"` (spec §4).
4. **`githubRef` normalization:** lowercase `owner/repo`, literal `#`, decimal
   number; reject URL forms.
5. **Old docs missing new fields:** whatsnext treats missing `source` as
   `"quayside"`, missing `capability` as `"unknown"`; sync treats missing
   `syncHash` as null.
6. **"Done" determination:** terminal status = the project's highest-`order`
   `taskStatus` (embedded `Project.Status`, `models.py:71-77`). Add a helper to
   resolve terminal status ids per project.
7. **whatsnext authorization:** reuse the `getTasks` project-scoping
   (`tasks.py:172-174`).

Verdict: no blockers. Safe to proceed to Slice 1 (failing tests first).

## Done / stuck signals (step 4)

- **Done (Slice 1):** five fields added with defaults; `GET /api/v1/whatsnext/`
  returns the spec §5 schema (unblocked / blocked-with-reasons / criticalPath /
  rollup); all spec §12 Core Conformance tests green; existing suite still green.
- **Stuck:** any whatsnext path returns tasks outside the caller's projects; a
  cycle loops instead of 409; existing task tests flip; `source` mutable on
  update. Any of these = stop and fix before moving on.

## Worktree

Build in `~/repos/quayside-manifest` on branch `manifest` (this worktree owns it;
verified clean at the handoff commit). Target PRs at `dev`.
