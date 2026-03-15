# CLAUDE.md — Shared Development Conventions

## Code Philosophy

### Directional Guidance

**Simplicity is inherently good.** Prefer the simplest solution that works. When in doubt, choose the option that's easier to read, easier to delete, and easier to explain.

### Human-in-the-Loop

Development proceeds in milestones. Do not move past a milestone without explicit approval. Milestones should be designed to be testable. Writing code whose only purpose is to make it easy for the human to understand the code that has been written can be a good idea. Feel free to write HTML pages or CLIs to enable this.

### Debugging Discipline

Quick fixes are a good first response, but if two or three attempts don't resolve a problem, stop and re-evaluate. Step back, list what you know for certain vs what you're assuming, form explicit theories, and add diagnostic steps to collect evidence. Rigorous chains of logic built on proven facts beat rapid trial-and-error for persistent problems.

### Testing Philosophy

With AI-assisted development producing larger PRs, code review alone doesn't scale as the primary confidence mechanism. **Testing is the primary confidence source; code review catches what tests can't** (naming, architecture, intent).

**The goal is confidence that features work, not test count.** A mocked unit test that passes regardless of whether the real feature works is worse than no test — it creates false confidence.

**Prioritize testing:**
- User-facing behavior and workflows (does the page load? does the form submit?)
- Security boundaries (auth checks, input validation)
- Data integrity (DB operations, file storage)
- Non-obvious logic (parsers, transformers, state machines)

**Keep lightweight:**
- Pass-through components that just render props
- Styling and layout details
- Volatile internals likely to change with refactors

This is directional guidance — use judgment about what's worth testing for each change, not a prescriptive "every X must have Y" rule.

**Test categories** (projects should support up to three tiers):

| Tier | What it covers | Speed | Infra needed |
|------|---------------|-------|-------------|
| Unit/integration | Logic, components, mocked services | Fast | None |
| E2E | Browser smoke tests (prod build) | Slow | May need DB via CI service |
| Live | Real infrastructure (DB, APIs) | Medium | Real services running |

The standard test command must never hit real infrastructure. External services should be mocked. Real-infrastructure tests belong in a separate command. E2E tests should use mock modes for AI/external APIs and bypass auth gates where needed.

### Testing Rules

**Choose the right test tier:**
- **DB operations → live tests** (real DB). Do not mock ORM query builders — mocked DB tests pass even when the real query is wrong.
- **Critical user journeys → E2E**. See `claude/guidance/CRITICAL_USER_JOURNEYS.md` for the list of journeys that must have E2E coverage.
- **Pure logic (parsers, transformers, calculators) → unit tests** with mocks where appropriate.
- **API routes → test the business logic with a real DB**, not the route handler with mocked imports. Don't mock the framework's routing/middleware layer.
- **Components → only test if they have complex state or interaction logic.** Do not write render-without-crash tests.

**When building a feature:**
1. Check if the feature is part of a critical user journey (`claude/guidance/CRITICAL_USER_JOURNEYS.md`)
2. If yes: the feature must have E2E test coverage for its journey's happy path
3. If the feature touches DB operations: write live tests, not mocked unit tests
4. If the feature is short-lived or experimental: build + type-check is sufficient (CI already does this)

**What NOT to write:**
- Mocked ORM query chain tests (false confidence)
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

### Branch Memory

Every session uses branch memory in `claude/memory/<branch>/` for continuity across sessions and context compaction. Each branch gets a directory with two files:

- **`state.md`** — Current snapshot: what exists, key files, current status, known issues. Updated in-place as things change — always reflects the present state.
- **`log.md`** — Append-only chronological record of what was done. Each session gets a timestamped entry (use `date -u '+%Y-%m-%dT%H:%M:%SZ'` for the timestamp) listing changes made.

**Session start behavior:**
- **On a branch**: Check if `claude/memory/<branch>/state.md` and `log.md` exist. If they do, read both to load context. If they don't, create them.
- **On main**: Ask the user whether they want to set up a branch, or if this is a non-writing task (research, review, etc.) that doesn't need branch memory.

**During a session:**
- Update the log with significant changes as you go (not every micro-step, but enough to reconstruct what happened).
- Update the state file when the current status meaningfully changes (new features complete, status shifts, new issues discovered).
- On resumption after context compaction, re-read both files to reconstruct context. Between the branch memory, git history, and the code itself, you should have enough to continue without the original conversation.

Keep entries concise — these are working notes for yourself, not documentation for humans.

### Scratch Space

`claude/scratch/` is available for temporary files — test data, draft content, one-off scripts, or anything that doesn't fit elsewhere. It is not for branch session notes (use `claude/memory/` for those).

### Future Work and Tasks

`claude/future_work.md` is the index for deferred work — things that come up during a PR but are out of scope, or ideas the user wants to revisit later. When deferring work, append an entry with a timestamp (use `date -u '+%Y-%m-%dT%H:%M:%SZ'`), a description, and enough context for someone to pick it up later. A human will review and prioritize this file periodically.

For larger items that need more detail, create a file in `claude/tasks/` and reference it from `future_work.md`. Task files are informal — they can be rough notes, investigation results, or half-formed plans at any stage of maturity.

When a task is picked up for implementation, it should go through a proper planning session (plan mode) rather than being used as a plan directly. The task file captures what was known at the time; the planning session produces a current, reviewed plan.

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

Most work doesn't need a master plan — propose milestones, get approval, and start building. Even small tasks should be broken into milestones with demo points so the human can verify progress and course-correct.

For larger efforts that span many milestones, a **master plan** scopes the full project first. Each milestone is then detailed in a separate **milestone plan** before implementation begins.

Plans are stored in `claude/memory/<branch>/plans/` with timestamped filenames:

```
claude/memory/<branch>/plans/
  2026-03-15-1730-dispatch-task-runner-master.md       # Master plan
  2026-03-15-1745-dispatch-task-runner-milestone-1.md   # Milestone plan
  2026-03-15-1800-dispatch-task-runner-milestone-2.md
  2026-03-16-0900-add-qwen-model.md                    # Standalone plan (no master)
```

Naming convention: `<YYYY-MM-DD-HHMM>-<topic>-<type>.md`
- **Master plans**: `-master.md`
- **Milestone plans**: `-milestone-N.md`
- **Standalone plans** (no master): just `<timestamp>-<topic>.md`

When doing plan mode, always save the plan once approved and before starting implementation. When resuming a conversation from a summary (this is called "compaction") where the last activity was planning, check whether the plan was actually saved to disk — the save step is easily lost during compaction. If the plan file doesn't exist, save it before continuing.

### Pre-Review Checklist

Before opening a PR, the user may ask Claude to run the pre-review process. This is only run on demand, not on every change. The review covers the **entire branch/PR**, not just the most recent session.

**Context gathering:**
1. Read branch memory (`claude/memory/<branch>/state.md` and `log.md`) to understand the full history of work on this branch
2. Run `git log main..HEAD` and `git diff main` to understand the complete set of changes

**Automated checks** (commands are project-specific — check the project's CLAUDE.md or package.json):
3. Tests pass
4. Build succeeds
5. Lint passes
6. Generated files are current (if applicable — regenerate and confirm no diff)

**PR comment review:**
7. Run `gh api repos/{owner}/{repo}/pulls/{number}/comments` and check for unresolved comments. Ignore resolved comments. Don't assume every comment needs action — consider the idea and flag anything worth discussing.

**Manual review:**
8. **Critical journeys covered** — Check if the changes touch any journey in `claude/guidance/CRITICAL_USER_JOURNEYS.md`. If so, verify that E2E tests exist for the affected journey and that they pass. If no E2E test exists for an affected journey, flag this to the user — it may need to be written before the PR merges.
9. No leftover debug code — no stray `console.log`, commented-out code, or TODOs from the work session
10. Docs match code — CLAUDE.md reflects actual state. README.md and DESIGN.md for affected components have been written or updated.
11. No unintended changes — review `git diff main` to confirm only expected files are touched
12. No secrets or sensitive data in the diff

**PR review guide:**
13. Post a comment via `gh pr comment` with:
    - **Summary**: What changed and why across the entire branch (2-3 sentences)
    - **Verification**: What was tested and how (commands run, results)
    - **Review notes**: What a human reviewer should focus on — architecture decisions, tradeoffs, areas of uncertainty
    - **Commit message**: A ready-to-use commit message for squash-merge (in a code block for easy copy)
    - End the comment with: `🤖 Generated with Claude Code`

### GitHub Comments

When posting any comment on GitHub (PR comments, review replies, issue comments), always end the comment with: `🤖 Generated with Claude Code`

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

