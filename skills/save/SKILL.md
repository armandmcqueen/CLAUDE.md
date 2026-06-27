---
name: save
description: Save session progress to branch memory (state + log). Use when the user asks to "save" or wants to checkpoint progress.
disable-model-invocation: true
---

Read the "Branch Memory" section of `AGENTS.md` to understand how the state and log files work.

Determine the current git branch, then update the branch memory for it:

- Update the **state file** to reflect the current state of the work (what exists, key files, status, known issues).
- Append a timestamped entry to the **log file** summarizing what was done this session.

Use your knowledge of the current session to populate both files. If they don't exist yet, create them.
