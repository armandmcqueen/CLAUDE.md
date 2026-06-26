# /// script
# requires-python = ">=3.11"
# dependencies = ["typer"]
# ///
"""Install the shared global agent conventions.

Canonical source is AGENTS.md in this repo. Each installed agent's global
instruction file is a SYMLINK to it — so editing AGENTS.md updates every agent
at once, and the only "sync" is committing this repo. No copying, no drift.

Run:  uv run install.py            # set up / refresh the links
      uv run install.py --dry-run  # show what would change
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import typer

HOME = Path.home()
CANONICAL = HOME / "code" / "CLAUDE.md" / "AGENTS.md"

# Each agent's GLOBAL instruction file -> a symlink to CANONICAL.
# Skipped automatically when the agent isn't installed (its dir is absent).
LINKS: dict[str, Path] = {
    "claude": HOME / ".claude" / "CLAUDE.md",
    "codex": HOME / ".codex" / "AGENTS.md",
    "grok": HOME / ".grok" / "AGENTS.md",
    "opencode": HOME / ".config" / "opencode" / "AGENTS.md",
    "pi": HOME / ".pi" / "agent" / "AGENTS.md",
}

# Gemini CLI doesn't follow symlinks; it reads files named in settings.json.
GEMINI_SETTINGS = HOME / ".gemini" / "settings.json"


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def link_agent(name: str, target: Path, dry_run: bool) -> str:
    if not target.parent.exists():
        return f"skip   {name:9} ({target}) — agent not installed"

    if target.is_symlink():
        if target.resolve() == CANONICAL.resolve():
            return f"ok     {name:9} -> already linked"
        action = "relink"
        if not dry_run:
            target.unlink()
    elif target.exists():
        action = "replace file"
        if not dry_run:
            backup = target.with_name(f"{target.name}.bak-{_stamp()}")
            shutil.copy2(target, backup)
            target.unlink()
    else:
        action = "create"

    if not dry_run:
        target.symlink_to(CANONICAL)
    return f"link   {name:9} -> {target}  ({action})"


def wire_gemini(dry_run: bool) -> str:
    if not GEMINI_SETTINGS.exists():
        return "skip   gemini    — no settings.json"
    data = json.loads(GEMINI_SETTINGS.read_text())
    names = data.setdefault("context", {}).setdefault("fileNames", [])
    if "AGENTS.md" in names:
        return "ok     gemini    -> AGENTS.md already in context.fileNames"
    names.insert(0, "AGENTS.md")
    if not dry_run:
        GEMINI_SETTINGS.write_text(json.dumps(data, indent=2) + "\n")
    return "wire   gemini    -> added AGENTS.md to context.fileNames"


def main(dry_run: bool = typer.Option(False, help="Show changes without applying them.")):
    if not CANONICAL.exists():
        typer.secho(f"Canonical file missing: {CANONICAL}", fg="red")
        raise typer.Exit(1)
    typer.echo(f"canonical: {CANONICAL}{'  (dry run)' if dry_run else ''}")
    for name, target in LINKS.items():
        typer.echo("  " + link_agent(name, target, dry_run))
    typer.echo("  " + wire_gemini(dry_run))


if __name__ == "__main__":
    typer.run(main)
