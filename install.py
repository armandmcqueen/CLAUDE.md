# /// script
# requires-python = ">=3.11"
# dependencies = ["typer"]
# ///
"""Install the shared global agent conventions, skills, and commands.

The instruction file (AGENTS.md) is the canonical source and is distributed by
SYMLINK — edit it and every agent sees the change live; the only "sync" is
committing this repo.

Skills and commands are distributed by COPY (agents such as Codex don't follow
symlinks for skill dirs), so re-run this after editing them.

Run:  uv run install.py            # set up / refresh everything
      uv run install.py --dry-run  # show what would change
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import typer

HOME = Path.home()
REPO = Path(__file__).resolve().parent
CANONICAL = REPO / "AGENTS.md"

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

# Skills -> the portable user skills dir (read by Codex/Grok/Gemini/opencode/pi)
# plus Claude's own. Commands are Claude-specific slash commands.
SKILL_TARGETS = [HOME / ".agents" / "skills", HOME / ".claude" / "skills"]
COMMAND_TARGETS = [HOME / ".claude" / "commands"]


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
            shutil.copy2(target, target.with_name(f"{target.name}.bak-{_stamp()}"))
            target.unlink()
    else:
        action = "create"

    if not dry_run:
        target.symlink_to(CANONICAL)
    return f"link   {name:9} -> {target}  ({action})"


def install_dir(src: Path, targets: list[Path], dry_run: bool) -> list[str]:
    """Copy each top-level entry of src into every target dir (per-item overwrite,
    so unrelated items already in the target are left untouched)."""
    if not src.is_dir():
        return [f"skip   {src.name}/ — no source dir"]
    items = sorted(p for p in src.iterdir() if not p.name.startswith("."))
    names = ", ".join(p.name for p in items)
    out = []
    for dst in targets:
        if not dry_run:
            dst.mkdir(parents=True, exist_ok=True)
            for item in items:
                dest = dst / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
        out.append(f"copy   {src.name}/ -> {dst}  ({names})")
    return out


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

    typer.echo("instructions (symlink):")
    for name, target in LINKS.items():
        typer.echo("  " + link_agent(name, target, dry_run))
    typer.echo("  " + wire_gemini(dry_run))

    typer.echo("skills + commands (copy):")
    for line in install_dir(REPO / "skills", SKILL_TARGETS, dry_run):
        typer.echo("  " + line)
    for line in install_dir(REPO / "commands", COMMAND_TARGETS, dry_run):
        typer.echo("  " + line)


if __name__ == "__main__":
    typer.run(main)
