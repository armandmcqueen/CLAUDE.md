---
name: prepr
description: Run the pre-PR review checklist defined in AGENTS.md. Use when the user is ready to open a PR or asks to "prepr".
disable-model-invocation: true
---

Read the repository's `AGENTS.md` and execute the pre-PR review checklist defined there.

- Run every automated check the checklist names (tests, lint, build, regenerating generated files and confirming no diff).
- Run every manual check (docs current, no leftover debug code, no unintended changes, no secrets, critical journeys covered if the repo defines them).
- If anything fails, report it with a suggested fix.
- If everything passes, summarize the verification and provide a ready-to-use commit message and PR description in the format the checklist specifies.
