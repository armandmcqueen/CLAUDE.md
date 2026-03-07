# CLAUDE.md — Global Conventions

This is a global CLAUDE.md applied to all projects. Project-specific CLAUDE.md files take precedence for project-specific details, but the principles here always apply.

This file has two sections. **Section 1** applies universally. **Section 2** describes conventions for my personal projects — apply it when the project-level CLAUDE.md indicates it, or when working in a repo that clearly follows these patterns.

---

## Section 1: Universal

### Human-in-the-Loop

Development proceeds in milestones. Do not move past a milestone without explicit approval. When a plan exists (e.g. in a `todo/` directory), follow it. When no plan exists, propose milestones before writing code.

### Debugging Discipline

Quick fixes are a good first response, but if two or three attempts don't resolve a problem, stop and re-evaluate. Step back, list what you know for certain vs what you're assuming, form explicit theories, and add diagnostic steps to collect evidence. Rigorous chains of logic built on proven facts beat rapid trial-and-error for persistent problems.

### Testing Philosophy

With AI-assisted development producing larger PRs, code review alone doesn't scale as the primary confidence mechanism. **Testing is the primary confidence source; code review catches what tests can't** (naming, architecture, intent).

Prioritize testing:
- User-facing behavior and workflows (does the page load? does the form submit?)
- Security boundaries (auth checks, input validation)
- Data integrity (DB operations, file storage)
- Non-obvious logic (parsers, transformers, state machines)

Keep lightweight:
- Pass-through components that just render props
- Styling and layout details
- Volatile internals likely to change with refactors

This is directional guidance — use judgment about what's worth testing for each change, not a prescriptive "every X must have Y" rule.

### Test Independence

Tests that run via the standard test command should never hit real infrastructure. External services should be mocked. If tests against real infrastructure are needed, they belong in a separate command with clear prerequisites documented.

### Scratch Notes

Every session uses scratch notes in `claude/scratch/` (relative to the project root) for continuity across sessions and context compaction. Each branch gets a pair of files:

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

Whether `claude/scratch/` is committed or gitignored is project-specific. Either way, it provides cross-session continuity within the local environment.

### Git Policy

Readonly git commands (`git status`, `git log`, `git diff`, etc.) are fine to use freely. However, git mutations (commit, push, branch, reset, etc.) should be rare — git history is used to protect against agentic mistakes. Creating a branch for testing something can be acceptable, but should usually be coordinated with the user first.

### Documentation

Every major component (workspace packages, significant subsystems) gets two docs at its root:

- **`README.md`** — High-level: what it is, how to use it, key concepts, getting started. A new contributor should be able to understand the component's purpose and run it from the README alone.
- **`DESIGN.md`** — In-depth: architecture, subsystem breakdown, key decisions and tradeoffs, data flow, what was considered and rejected. **This is the primary artifact a human reviews during code review** — it should be detailed enough that the reviewer can evaluate the approach without reading every source file.

Both docs should be kept current as the code evolves. When a PR changes a component's behavior or architecture, updating its DESIGN.md is part of the work, not a follow-up task.

### Code Style

- **Comment pragmatically:** JSDoc on every function is overkill, but if you scan 10 files and none have a meaningful comment, we're under-commenting. Inline comments for non-obvious logic; skip comments that just restate the code.

### Pre-Review Checklist

Before opening a PR, the user may ask to run the pre-review process. This is only run on demand, not on every change. Check the project-level CLAUDE.md or package.json/Makefile for the specific commands.

**Automated checks:**
1. Tests pass
2. Build succeeds
3. Lint passes
4. Generated files are current (if applicable — regenerate and confirm no diff)

**PR comment review:**
5. Run `gh api repos/{owner}/{repo}/pulls/{number}/comments` and check for unresolved comments. Ignore resolved comments. Don't assume every comment needs action — consider the idea and flag anything worth discussing.

**Manual review:**
6. No leftover debug code — no stray `console.log`, commented-out code, or TODOs from the work session
7. Docs match code — CLAUDE.md files reflect actual state. README.md and DESIGN.md for affected components have been written or updated.
8. No unintended changes — review `git diff` to confirm only expected files are touched
9. No secrets or sensitive data in the diff

**PR review guide:**
10. Post a comment via `gh pr comment` with:
    - **Summary**: What changed and why (2-3 sentences)
    - **Verification**: What was tested and how (commands run, results)
    - **Review notes**: What a human reviewer should focus on — architecture decisions, tradeoffs, areas of uncertainty
    - **Commit message**: A ready-to-use commit message for squash-merge (in a code block for easy copy)
    - End the comment with: `🤖 Generated with Claude Code`

---

## Section 2: Personal Project Conventions

These conventions apply to my personal/side projects. They assume a modern JS/TS stack but the principles carry to other stacks. Apply this section when the project-level CLAUDE.md opts in or when the project clearly follows these patterns (e.g. has a `docker-compose.yml` for local Postgres, uses Drizzle, has `.env.development` checked in).

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
