# AGENTS.md — Shared Development Conventions

These are my conventions for working with coding agents — they apply on **every** repo I work on, regardless of project. A repo's own `AGENTS.md` adds its project-specific facts (stack, commands, structure, the actual test tiers and critical journeys this file refers to generically); where a repo documents its own specifics, use those.

## Code Philosophy

**Simplicity is inherently good.** Prefer the simplest solution that works. When in doubt, choose the option that's easier to read, easier to delete, and easier to explain.

- **Comment pragmatically:** JSDoc on every function is overkill, but if you scan 10 files and none have a meaningful comment, we're under-commenting. Inline comments for non-obvious logic; skip comments that just restate the code.

## Development Process

### Human-in-the-Loop

Development proceeds in milestones. Do not move past a milestone without explicit approval. Milestones should be designed to be testable. Writing code whose only purpose is to make it easy for the human to understand the code that has been written can be a good idea. Feel free to write HTML pages or CLIs to enable this.

### Human Understanding

When the human isn't writing the code, it is difficult to develop understanding of what is being written. We want to try different ways to enable the human to understand the code that has been written in the milestone. Some possible ideas

- Generate a web ui or CLI that lets you interact with the milestone deliverables
- A UI that shows test inputs and conditions from some component to enable understanding the code as a black box.
- Alternative ideas! Suggest new ideas that make sense for the milestone. We need to try stuff to see what works.

Spending 50% of the effort writing the main code and 50% of the time writing tools to help the user understand the code that has been written is perfectly valid.

### Debugging Discipline

Quick fixes are a good first response, but if two or three attempts don't resolve a problem, stop and re-evaluate. Step back, list what you know for certain vs what you're assuming, form explicit theories, and add diagnostic steps to collect evidence. Rigorous chains of logic built on proven facts beat rapid trial-and-error for persistent problems.

### Proving Your Work

Never claim something is done, fixed, or working without evidence. "I updated the code" is not evidence that a bug is fixed. "The test passes" or "I ran the server and verified the response" is evidence. If you can't demonstrate it works, say so — don't assert it.

This applies to:
- Bug fixes — show the failing case now passes
- New features — show the feature working (test output, CLI output, server response)
- Refactors — show existing tests still pass and behavior is unchanged

If there's no practical way to verify (e.g. a docs-only change), say that explicitly rather than implying you verified something you didn't.

### Planning

Most work doesn't need a master plan — propose milestones, get approval, and start building. Even small tasks should be broken into milestones with demo points so the human can verify progress and course-correct.

For larger efforts that span many milestones, a **master plan** scopes the full project first. Each milestone is then detailed in a separate **milestone plan** before implementation begins.

Plans are stored in `agents/memory/<branch>/plans/` with timestamped filenames:

```
agents/memory/<branch>/plans/
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

### Git Policy

Readonly git commands (`git status`, `git log`, `git diff`, etc.) are fine to use freely. However, git mutations (commit, push, branch, reset, etc.) should be rare — git history is used to protect against agentic mistakes. Creating a branch for testing something can be acceptable, but should usually be coordinated with the user first.

**Never create merge commits.** To integrate upstream changes into a branch, rebase (`git rebase`) — do not merge. This applies even to `--no-commit` / `--no-ff` exploratory merges; if you need to see how main's changes interact with a branch, do it with rebase or by inspecting diffs, not by entering a merge state.

### Documentation

Two docs are **suggested** for every major component (workspace packages, significant subsystems) — create them by default, but treat this as a recommendation, not a hard rule:

- **`README.md`** — High-level: what it is, how to use it, key concepts, getting started. A new contributor should be able to understand the component's purpose and run it from the README alone.
- **`DESIGN.md`** — In-depth: architecture, subsystem breakdown, key decisions and tradeoffs, data flow, what was considered and rejected. When present, this is the primary artifact a human reviews during code review — it should be detailed enough that the reviewer can evaluate the approach without reading every source file.

Keep these current as the code evolves. When a PR changes a component's behavior or architecture, updating its DESIGN.md is part of the work, not a follow-up task.

## Testing

### Philosophy

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

### Test Tiers

Tests come in tiers, from fast checks with no external dependencies up to tests against real infrastructure. The **standard test command should never hit real infrastructure** — external services should be mocked, and real-infrastructure tests should live behind a separate command. End-to-end tests should use mock modes for AI/external APIs and bypass auth gates where needed. The specific tiers a project supports, and their commands, belong in that repo's `AGENTS.md`.

### Rules

**Choose the right test tier:**
- **Critical user journeys → E2E.** If the repo defines critical user journeys, their happy path should have E2E coverage.
- **Code that talks to real dependencies (DB, APIs, file systems) → live tests.** Don't mock the layer you're trying to test — mocked dependency tests pass even when the real interaction is broken.
- **Pure logic (parsers, transformers, calculators) → unit tests** with mocks where appropriate.
- **Trivial pass-through code → don't test.** If the code just forwards to a framework or library with no logic, testing it tests the framework, not your code.

**When building a feature:**
1. If it's part of a critical user journey, it should have E2E coverage for the journey's happy path.
2. If it talks to real dependencies, write live tests, not mocked unit tests.
3. If it's short-lived or experimental, build + type-check is sufficient.

**What NOT to write:**
- Tests that mock the dependency they're supposed to validate (false confidence)
- Tests for trivial code with no logic (no value)
- Tests that import a handler and mock all its dependencies (tests the mocks, not the code)
- Snapshot tests for UI (too brittle, never catch real bugs)

## Project Infrastructure

### Branch Memory

Every session uses branch memory in `agents/memory/<branch>/` for continuity across sessions and context compaction. Branch memory is **always tracked in git and pushed** — it is not gitignored. Include branch memory files when staging commits. Each branch gets a directory with two files:

- **`state.md`** — Current snapshot: what exists, key files, current status, known issues. Updated in-place as things change — always reflects the present state.
- **`log.md`** — Append-only chronological record of what was done. Each session gets a timestamped entry (use `date -u '+%Y-%m-%dT%H:%M:%SZ'` for the timestamp) listing changes made.

**Session start behavior:**
- **On a branch**: Check if `agents/memory/<branch>/state.md` and `log.md` exist. If they do, read both to load context. If they don't, create them.
- **On main**: Ask the user whether they want to set up a branch, or if this is a non-writing task (research, review, etc.) that doesn't need branch memory.

**During a session:**
- Update the log with significant changes as you go (not every micro-step, but enough to reconstruct what happened).
- Update the state file when the current status meaningfully changes (new features complete, status shifts, new issues discovered).
- On resumption after context compaction, re-read both files to reconstruct context. Between the branch memory, git history, and the code itself, you should have enough to continue without the original conversation.

Keep entries concise — these are working notes for yourself, not documentation for humans.

### Scratch Space

`agents/scratch/` is available for temporary files — test data, draft content, one-off scripts, or anything that doesn't fit elsewhere. It is not for branch session notes (use `agents/memory/` for those).

### Future Work and Tasks

`agents/future_work.md` is the index for deferred work — things that come up during a PR but are out of scope, or ideas the user wants to revisit later. When deferring work, append an entry with a timestamp (use `date -u '+%Y-%m-%dT%H:%M:%SZ'`), a description, and enough context for someone to pick it up later. A human will review and prioritize this file periodically.

For larger items that need more detail, create a file in `agents/tasks/` and reference it from `future_work.md`. Task files are informal — they can be rough notes, investigation results, or half-formed plans at any stage of maturity.

When a task is picked up for implementation, it should go through a proper planning session (plan mode) rather than being used as a plan directly. The task file captures what was known at the time; the planning session produces a current, reviewed plan.

## Review Process

### Pre-Review Checklist

Before opening a PR, the user may ask the agent to run the pre-review process. This is only run on demand, not on every change. The review covers the **entire branch/PR**, not just the most recent session.

**Context gathering:**
- Read branch memory (`agents/memory/<branch>/state.md` and `log.md`) to understand the full history of work on this branch
- Run `git log main..HEAD` and `git diff main` to understand the complete set of changes

**Automated checks** (commands are project-specific — read them from the repo's `AGENTS.md` or `package.json`):
- Tests pass
- Build succeeds
- Lint passes
- Generated files are current (if applicable — regenerate and confirm no diff)

**PR comment review:**
- Run `gh api repos/{owner}/{repo}/pulls/{number}/comments` and check for unresolved comments. Ignore resolved comments. Don't assume every comment needs action — consider the idea and flag anything worth discussing.

**Manual review:**
- **Critical journeys covered** — If the repo defines critical user journeys, check whether the changes touch one. If so, verify E2E tests exist for the affected journey and that they pass; if none exists, flag it — it may need to be written before the PR merges.
- No leftover debug code — no stray `console.log`, commented-out code, or TODOs from the work session
- Docs match code — the repo's `AGENTS.md` reflects actual state. `README.md` and `DESIGN.md` for affected components (where present) have been written or updated.
- No unintended changes — review `git diff main` to confirm only expected files are touched
- No secrets or sensitive data in the diff

**PR review guide:**
- Post a comment via `gh pr comment` with:
    - **Summary**: What changed and why across the entire branch (2-3 sentences)
    - **Verification**: What was tested and how (commands run, results)
    - **Review notes**: What a human reviewer should focus on — architecture decisions, tradeoffs, areas of uncertainty
    - **Commit message**: A ready-to-use commit message for squash-merge (in a code block for easy copy)
    - End the comment with: `🤖 Generated with $AGENT`

### GitHub Comments

When posting any comment on GitHub (PR comments, review replies, issue comments), always end the comment with: `🤖 Generated with $AGENT`, substituting your own agent name for `$AGENT`.

## Available tools

- `gtimeout`
- `rg`
- `jsonpeek`
- `gitro`
- `markdownpeek`
- `lsrelated`
- `textplate`

### `jsonpeek`

Use instead of writing Python to inspect, navigate, or compare JSON data.
Run `jsonpeek help` for full command reference.

### `gitro`

Use instead of raw `git` for read-only git operations. Blocks mutations (commits, pushes, resets).

### `markdownpeek`

Use instead of reading entire Markdown files when you only need structure or specific sections.
Run `markdownpeek tool-description` for full command reference.

### `lsrelated`

Use when exploring an unfamiliar codebase to find files frequently accessed together.
Run `lsrelated tool-description` for full command reference.

### `textplate`

Use when working with `.textplate.md` files or composing documents from reusable markdown snippets via `text::` links.
Run `textplate tool-description` for full command reference.
