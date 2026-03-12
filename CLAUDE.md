# CLAUDE.md — Shared Development Conventions

This file has two sections. **Section 1** applies to any project. **Section 2** describes conventions specific to my personal projects but not all of them — include it when it applies.

---

## Section 1: Universal Development Philosophy

### Human-in-the-Loop

Development proceeds in milestones. Do not move past a milestone without explicit approval. Milestones should be designed to be testable. Writing code whose only purpose is to make it easy for the human to understand the code that has been written can be a good idea. Feel free to write HTML pages or CLIs to enable this.

### Debugging Discipline

Quick fixes are a good first response, but if two or three attempts don't resolve a problem, stop and re-evaluate. Step back, list what you know for certain vs what you're assuming, form explicit theories, and add diagnostic steps to collect evidence. Rigorous chains of logic built on proven facts beat rapid trial-and-error for persistent problems.

### Testing Philosophy

With AI-assisted development producing larger PRs, code review alone doesn't scale as the primary confidence mechanism. **Testing is the primary confidence source; code review catches what tests can't** (naming, architecture, intent).

**The goal is confidence that features work, not test count.** A mocked unit test that passes regardless of whether the real feature works is worse than no test — it creates false confidence.

**Test categories:**

| Command | What it runs | Speed | Infra needed | CI |
|---------|-------------|-------|-------------|-----|
| `pnpm test` | Unit + integration (Vitest) | Fast | None (all mocked) | Yes |
| `pnpm test:e2e` | Browser tests (Playwright) | Slow (builds prod server) | Postgres (via GH Actions service) | Yes |
| `pnpm test:live` | Real-infra tests (`*.live.test.ts`) | Medium | Postgres (via Docker or GH Actions service) | Yes |

E2E tests run with `AI_MOCK=true` and `BYPASS_ADMIN_AUTH=true` set via `playwright.config.ts` webServer env.

### Testing Rules

**Choose the right test tier:**
- **DB operations → `.live.test.ts`** (real Postgres). Do not mock Drizzle query builders — mocked DB tests pass even when the real query is wrong.
- **Critical user journeys → E2E** (Playwright). See `claude/guidance/CRITICAL_USER_JOURNEYS.md` for the list of journeys that must have E2E coverage.
- **Pure logic (parsers, transformers, calculators) → unit tests** with mocks where appropriate.
- **API routes → test the business logic with a real DB**, not the route handler with mocked imports. Middleware and routing are handled by Next.js — mocking them tests nothing.
- **Components → only test if they have complex state or interaction logic.** Do not write render-without-crash tests.

**When building a feature:**
1. Check if the feature is part of a critical user journey (`claude/guidance/CRITICAL_USER_JOURNEYS.md`)
2. If yes: the feature must have E2E test coverage for its journey's happy path
3. If the feature touches DB operations: write `.live.test.ts` tests, not mocked unit tests
4. If the feature is short-lived or experimental: build + type-check is sufficient (CI already does this)

**What NOT to write:**
- Mocked Drizzle query chain tests (false confidence)
- Render-without-crash component tests (no value)
- API route tests that import the handler and mock all dependencies (tests the mocks, not the route)
- Snapshot tests for UI (too brittle, never catch real bugs)

### Critical User Journeys

The file `claude/guidance/CRITICAL_USER_JOURNEYS.md` defines user journeys that must always work. Each journey maps to E2E test coverage.

When building or modifying a feature, check if it touches a critical journey. If a new feature is important enough to be critical, add its journey to the file.

### Human Understanding

When the human isn't writing the code, it is difficult to develop understanding of what is being written. We want to try different ways to enable the human to understand the code that has been written in the milestone. Some possible ideas

- Generate a web ui or CLI that lets you interact with the milestone deliverables
- A UI that shows test inputs and conditions from some component to enable understanding the code as a black box.
- Alternative ideas! Suggest new ideas that make sense for the milestone. We need to try stuff to see what works.

Spending 50% of the effort writing the main code and 50% of the time writing tools to help the user understand the code that has been written is perfectly valid.

### Test Independence

Tests that run via the standard test command should never hit real infrastructure. External services should be mocked. If tests against real infrastructure are needed, they belong in a separate command with clear prerequisites documented.

### Scratch Notes

Every session uses scratch notes in `claude/scratch/` for continuity across sessions and context compaction. Each branch gets a pair of files:

- **`<branch>_state.md`** — Current snapshot: what exists, key files, current status, known issues. Updated in-place as things change — always reflects the present state.
- **`<branch>_log.md`** — Append-only chronological record of what was done. Each session gets a timestamped entry (use `date -u '+%Y-%m-%dT%H:%M:%SZ'` for the timestamp) listing changes made.

**Session start behavior:**
- **On a branch**: Check if `claude/scratch/<branch>_state.md` and `<branch>_log.md` exist. If they do, read both to load context. If they don't, create them.
- **On main**: Ask the user whether they want to set up a branch, or if this is a non-writing task (research, review, etc.) that doesn't need scratch notes.

**During a session:**
- Update the log with significant changes as you go (not every micro-step, but enough to reconstruct what happened).
- Update the state file when the current status meaningfully changes (new features complete, status shifts, new issues discovered).
- On resumption after context compaction, re-read both files to reconstruct context. Between the scratch notes, git history, and the code itself, you should have enough to continue without the original conversation.

Keep entries concise — these are working notes for yourself, not documentation for humans.

Note: `claude/scratch/` does not need to be committed. In projects that use the branch+state+log pattern natively, commit them. In other projects, `.gitignore` the directory — it still provides cross-session continuity within the local environment.

### Git Policy

Readonly git commands (`git status`, `git log`, `git diff`, etc.) are fine to use freely. However, git mutations (commit, push, branch, reset, etc.) should be rare — git history is used to protect against agentic mistakes. Creating a branch for testing something can be acceptable, but should usually be coordinated with the user first.

### Documentation

Every major component (workspace packages, significant subsystems) gets two docs at its root:

- **`README.md`** — High-level: what it is, how to use it, key concepts, getting started. A new contributor should be able to understand the component's purpose and run it from the README alone.
- **`DESIGN.md`** — In-depth: architecture, subsystem breakdown, key decisions and tradeoffs, data flow, what was considered and rejected. **This is the primary artifact a human reviews during code review** — it should be detailed enough that the reviewer can evaluate the approach without reading every source file.

Both docs should be kept current as the code evolves. When a PR changes a component's behavior or architecture, updating its DESIGN.md is part of the work, not a follow-up task.

### Code Style

- **Comment pragmatically:** JSDoc on every function is overkill, but if you scan 10 files and none have a meaningful comment, we're under-commenting. Inline comments for non-obvious logic; skip comments that just restate the code.

### Planning

When doing plan mode, always save the plan to claude/plans once approved and we start working on the plan.

### Pre-Review Checklist

Before opening a PR, the user may ask Claude to run the pre-review process. This is only run on demand, not on every change.

**Automated checks** (commands are project-specific — check the project's CLAUDE.md or package.json):
1. Tests pass
2. Build succeeds
3. Lint passes
4. Generated files are current (if applicable — regenerate and confirm no diff)

**PR comment review:**
5. Run `gh api repos/{owner}/{repo}/pulls/{number}/comments` and check for unresolved comments. Ignore resolved comments. Don't assume every comment needs action — consider the idea and flag anything worth discussing.

**Manual review:**
### Critical journey check
6. **Critical journeys covered** — Check if the changes touch any journey in `claude/guidance/CRITICAL_USER_JOURNEYS.md`. If so, verify that E2E tests exist for the affected journey and that they pass. If no E2E test exists for an affected journey, flag this to the user — it may need to be written before the PR merges.
7. No leftover debug code — no stray `console.log`, commented-out code, or TODOs from the work session
8. Docs match code — CLAUDE.md reflects actual state. README.md and DESIGN.md for affected components have been written or updated.
9. No unintended changes — review `git diff` to confirm only expected files are touched
10. No secrets or sensitive data in the diff

**PR review guide:**
11. Post a comment via `gh pr comment` with:
    - **Summary**: What changed and why (2-3 sentences)
    - **Verification**: What was tested and how (commands run, results)
    - **Review notes**: What a human reviewer should focus on — architecture decisions, tradeoffs, areas of uncertainty
    - **Commit message**: A ready-to-use commit message for squash-merge (in a code block for easy copy)
    - End the comment with: `🤖 Generated with Claude Code`

---

## Section 2: Personal Project Conventions

These conventions apply to my personal/side projects. They assume a modern JS/TS stack but the principles carry to other stacks.

### External Infra Philosophy

Content and static data should be build artifacts with no external dependencies — generated JSON, static files, etc. Apps and interactive features can use external services (databases, blob storage, APIs), but the standard test command must never require them. Real-infrastructure tests belong in a separate command.

### Test Categories

Projects should support up to three tiers of testing:

| Tier | What it covers | Speed | Infra needed |
|------|---------------|-------|-------------|
| Unit/integration | Logic, components, mocked services | Fast | None |
| E2E | Browser smoke tests (prod build) | Slow | May need DB via CI service |
| Live | Real infrastructure (DB, APIs) | Medium | Real services running |

E2E tests should use mock modes for AI/external APIs and bypass auth gates where needed, configured via the test runner's env settings.

### Environment Files

- A tracked env file (e.g. `.env.development`) for non-secret local defaults: feature flags, local DB connection strings, dev-only bypasses.
- A gitignored env file (e.g. `.env.local`) for secrets: API keys, tokens. Ideally populated by a sync script that pulls from the deployment platform.

### Database Conventions

- Local dev uses Docker (e.g. Docker Compose for Postgres). Schema is applied directly via push commands — no migration files needed locally.
- Production uses migration files, generated and committed to git, applied at deploy time.
- A reset command should drop/recreate the local DB, apply the current schema, and seed test data.

### Centralized Config

Environment-dependent behavior (is this production? should auth be bypassed? which DB driver?) should be centralized in a config module, not scattered as `process.env` checks throughout the codebase. This makes it easy to audit what varies by environment.

## Available tools

- `gtimeout`
- `rg`
- `jsonpeek`
- `pystr`

### `jsonpeek`

JSON structural explorer for agents. Use jsonpeek instead of writing Python
to inspect, navigate, or compare JSON data. One command replaces five rounds
of `python3 -c "import json..."`.

WHEN TO USE:
- You need to understand the structure of an unfamiliar JSON file
- You want to extract a value at a known path
- You need to compare structures across files or array elements
- You want to find where a key name appears in a deeply nested object

WHEN NOT TO USE:
- You need to transform/rewrite JSON (use jq or Python)
- You need to filter arrays by value predicates (use jq)
- You already know the exact structure and just need a value (use jq -r)

COMMANDS:

jsonpeek help [command]
Detailed docs for any command. Use when you need output format details or
advanced options.

jsonpeek schema <file> [path]
Structural type tree: types, string lengths, array sizes, optional key
frequency, enum detection. Start here for any unfamiliar JSON file.

jsonpeek peek <file> [path]
Sampled preview with truncation. Real values, clipped for readability.

jsonpeek get <file> <path>
Extract raw value at path. Pretty prints objects, raw strings.

jsonpeek keys <file> [path]
One-level key listing with type, size, preview. Like ls for JSON.

jsonpeek find <file> <key>
Find all paths where a key name occurs. Substring match.

jsonpeek diff <file> <path> [i] [j]
Compare array elements or files structurally. Reports key/type differences.

jsonpeek stats <file> [path]
Size, depth, key counts, largest subtrees.

jsonpeek flat <file> [path]
Flatten to path = value lines. Best for small subtrees.

GLOBAL FLAGS: --max-depth N, --full, --json, --path P (for multi-file)
STDIN: command | jsonpeek schema -
PATHS: .foo.bar[0].baz

SETUP: jsonpeek tool-description >> ~/.claude/CLAUDE.md

TYPICAL WORKFLOW:
1. jsonpeek schema file.json            — understand the structure
2. jsonpeek peek file.json .some.path   — see sample data
3. jsonpeek get file.json .the.value    — extract what you need

## `pystr`

