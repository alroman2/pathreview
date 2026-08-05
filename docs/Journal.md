# Journal

## Week 7 — Issue selection

**Issue link:** [\[Issue-68\]](https://github.com/ascherj/pathreview/issues/68)

**Issue title:** Add a safety event count to the health check endpoint #68

**Tier:** [ x ] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The /health endpoint return service status but no safety metrics. The safety events last hour field. At this time the value is hardcoded to 0 instead of grabbing the actual event count from redis. This will need to be updated, which will then return the correct metric.

**Branch name:** fix/68-health-check-safety-event

**Setup confirmation:** [ x ] App runs locally at localhost:5173

**Cohort ledger:** [ x ] Issue added to cohort ledger

## Is This Issue Right for Me?

Use this checklist before you claim an issue on the pathreview tracker. Work through every question. If you're unsure about something, investigate before committing — a few minutes of research now saves several hours of being stuck in Week 9.

### Part 1 — Understanding the Issue

**Can I explain what this issue is asking for in my own words?**

Paraphrase the issue without looking at it. If you can't, you don't understand it well enough yet. Read the full issue body, look at any linked PRs or comments, and try again.

- [x] I can explain the problem and the expected behavior in 2–3 sentences without reading the issue.

**Do I understand which part of the app is affected?**

Check the labels on the issue — they often indicate the area (api, rag, ingestion, frontend, etc.). Look at the referenced files if any are mentioned. Find those files in the repo.

- [x] I've located the relevant files and confirmed they exist in the codebase.

**Do I understand what "done" looks like?**

Can you describe what the app should do (or not do) once the issue is fixed? If the issue has acceptance criteria, read them carefully. If it doesn't, try writing your own — that forces you to understand the scope.

- [x] I can describe a concrete before-and-after: what the user sees before the fix and what they see after.

### Part 2 — Tier Fit

Issues in the tracker are tagged with a tier level. Here's what each one means:

| Tier | Description | Typical scope |
| --- | --- | --- |
| Tier 1 | Self-contained, localized fix. The change lives in one or two files and doesn't require understanding how the whole system fits together. | Bug fix, missing validation, broken test, documentation update |
| Tier 2 | Requires understanding how two or more modules interact. May involve a service layer, database model, or API endpoint. | Feature addition, refactor, data flow bug |
| Tier 3 | Requires understanding the full system — multiple modules, possibly infrastructure or AI pipeline changes. | Architecture change, cross-cutting behavior, RAG or agent modification |

**Is the tier a realistic match for where I am right now?**

If this is my first open source contribution: I'm choosing Tier 1.
If I've contributed to large codebases before: Tier 2 or 3 is fair game.
I'm not choosing a Tier 3 issue to "challenge myself" if I haven't completed a Tier 1 or 2 first — scope surprises in Week 9 don't have a safety net.

- [x] I've chosen a tier that matches my experience level and I'm not overreaching.

### Part 3 — Codebase Readiness

**Can I find the relevant code?**

Before claiming the issue, locate the specific function, route, or module it describes. Don't rely on grep alone — open the file, read the surrounding context, and confirm you're in the right place.

- [x] I've found and read the specific code the issue references (not just the file — the function or section).

**Do I understand the surrounding code well enough to change it safely?**

You don't need to understand the whole codebase. But you need to understand the file you're about to edit well enough to predict what a change will break. Read the function signatures, docstrings, and any callers.

- [x] I've read enough surrounding context that I can write a rough plan for the fix without looking anything up.

**Have I read the relevant test file?**

Find the test file for the module your issue touches (tests/unit/ is the right place to start). Look at how existing tests are structured — fixtures, assertions, mock patterns. You'll need to write at least one new test.

- [x] I've found the test file for my module and read at least one test end-to-end.

### Part 4 — Scope and Time

**How many others are already working on this issue?**

Claims are non-exclusive — more than one student may work on the same issue, and your grade comes from your own artifacts, never from being first. Still, check the issue comments and the Claims column in the Issue Catalog tab of the cohort ledger: a less-crowded issue of the same tier can mean smoother coaching and peer review.

- [x] I've checked the issue comments and the ledger's Claims count, and I'm fine with how many others are on this issue.

**Is the scope realistic for Weeks 8–9?**

You have roughly two weeks to implement, test, and submit a PR. Tier 1 issues should take 3–6 hours of focused work. Tier 2 issues may take 8–12 hours. Tier 3 issues can take significantly longer.

Think about your week — other classes, work, other commitments. Is this achievable?

- [x] I've estimated the time this will take and I'm confident I can complete it before the Week 9 deadline.

**Are there any blockers or dependencies?**

Some issues say "blocked by #X" or reference another issue that needs to be resolved first. Check the issue for any such dependencies.

- [x] This issue has no open blockers or dependencies on other unresolved issues.

## Week 8 - Reproduction & solution planning

**Reproduction commit link:** <https://github.com/alroman2/pathreview/commit/afbd64f681446d1868e72e756bc48b9f5c88e1b9>

**Reproduction summary:**
Added a failing unit test (`tests/unit/test_health.py`) that stubs `SafetyMonitor.get_event_count` to report 7 recent events and asserts `/health` surfaces them. The endpoint hardcodes `safety_events_last_hour` to `0` (`api/routes/health.py:78`) instead of consulting `SafetyMonitor`, so the test fails with `assert 0 == 7`, confirming the issue.

**PLAN.md link:** <https://github.com/alroman2/pathreview/blob/fix/68-health-check-safety-event/docs/PLAN.md>

**Walkthrough video (recommended):** _(not recorded)_

**Blockers or open questions:**
`SafetyMonitor.get_event_count` does not enforce a time window (counts rely on a 24h Redis TTL), so "last hour" will be approximate unless time-bucketed keys are added later. `Settings` lacks `redis_host`/`redis_port`, so the fix should construct the Redis client from `settings.redis_url`.

## Week 9 — Implementation & testing

**What I implemented:**
Followed the PLAN.md steps. First I added a `get_total_event_count(window_hours=1)` helper to `SafetyMonitor` (`safety/monitoring.py`) that sums `get_event_count` over every `VALID_EVENT_TYPES` entry and returns `0` on Redis errors. Then I wired `health_check` (`api/routes/health.py`) to build a Redis client from `settings.redis_url` (avoiding the nonexistent `redis_host`/`redis_port`) and populate `safety_events_last_hour` from that helper. The safety block is wrapped in its own try/except so a Redis or monitor failure degrades the field to `0` with a logged error instead of crashing `/health`, and the field is still present in the 503 payload when dependencies are down.

**Commit links:**
- `b415d7e` feat(safety): add get_total_event_count to SafetyMonitor (Issue #68)
- `027a227` fix(api): surface real safety_events_last_hour in /health (Issue #68)

**Tests:**
Converted the failing repro into a passing test and added coverage. `tests/unit/test_monitoring.py` (new, 6 tests) covers the helper: summing across event types, missing keys, Redis-error fallback to `0`, non-integer values, iteration bounded by `VALID_EVENT_TYPES`, and forwarding `window_hours`. `tests/unit/test_health.py` (3 tests) asserts the endpoint surfaces the monitor total (`7`), falls back to `0` when the monitor raises, and still returns the field with `redis: unhealthy` in the 503 body when Redis is down. All 9 pass.

**Verification:**
`make test-unit` on my files: 9/9 pass. The full unit suite still shows 53 pre-existing failures, but they are all in unrelated modules (parsers, scorers, review_service, security) and were present before my change — stashing my work raises the count to 54 (my repro test failing again), confirming I introduced no regressions and fixed the one repro. `make typecheck` (mypy) passes clean on `api/routes/health.py` and `safety/monitoring.py`. The only ruff finding on my files is the `B008` `Depends()`-in-default pattern that every route file already uses and predates this change.

**Remaining open question:**
The "last hour" semantics are still approximate because `get_event_count` does not enforce a time window (24h Redis TTL). True windowed counts would need time-bucketed keys and are out of scope for #68, as noted in PLAN.md.

