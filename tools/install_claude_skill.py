#!/usr/bin/env python3
"""One-command installer for using health-skill with Claude Code."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


OWNER = "RTX2080"
REPO = "Health-skill"
DEFAULT_REF = "main"


def claude_home() -> Path:
    return Path(os.environ.get("CLAUDE_HOME", Path.home() / ".claude")).expanduser()


def default_install_dir() -> Path:
    return claude_home() / "skills" / "health-skill"


def download_repo(ref: str, tmp_dir: Path) -> Path:
    zip_url = f"https://codeload.github.com/{OWNER}/{REPO}/zip/{ref}"
    zip_path = tmp_dir / "repo.zip"
    urllib.request.urlretrieve(zip_url, zip_path)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(tmp_dir)
        roots = {name.split("/")[0] for name in archive.namelist() if name}
    if len(roots) != 1:
        raise RuntimeError("Unexpected GitHub archive layout.")
    return tmp_dir / next(iter(roots))


def copy_skill(repo_root: Path, install_dir: Path) -> None:
    if install_dir.exists():
        shutil.rmtree(install_dir)
    ignore = shutil.ignore_patterns(".git", "__pycache__", "*.pyc")
    shutil.copytree(repo_root, install_dir, ignore=ignore)


def memory_import_line(home: Path, install_dir: Path) -> str:
    if install_dir.expanduser() == default_install_dir().expanduser():
        return "@~/.claude/skills/health-skill/CLAUDE.md"
    return f"@{install_dir.expanduser().resolve() / 'CLAUDE.md'}"


def ensure_memory_import(memory_file: Path, import_line: str) -> None:
    memory_file.parent.mkdir(parents=True, exist_ok=True)
    existing = memory_file.read_text() if memory_file.exists() else ""
    if import_line in existing:
        return
    prefix = "" if not existing or existing.endswith("\n") else "\n"
    memory_file.write_text(f"{existing}{prefix}\n{import_line}\n")


def quoted_command(python_exe: Path, checker: Path) -> str:
    return f'"{python_exe}" "{checker}"'


def ensure_hook_runner(runner_file: Path, install_dir: Path) -> None:
    runner_file.parent.mkdir(parents=True, exist_ok=True)
    checker = install_dir.expanduser().resolve() / "scripts" / "health_check.py"
    runner_file.write_text(
        f"""#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

checker = Path({str(checker)!r})
if not checker.exists():
    raise SystemExit(0)

try:
    result = subprocess.run(
        [sys.executable, str(checker), "--quiet"],
        capture_output=True,
        text=True,
        timeout=5,
    )
except Exception:
    raise SystemExit(0)

if result.stdout:
    sys.stdout.write(result.stdout)

raise SystemExit(0)
"""
    )


def ensure_user_prompt_hook(settings_file: Path, command: str) -> None:
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    if settings_file.exists():
        content = settings_file.read_text().strip()
        settings = json.loads(content) if content else {}
    else:
        settings = {}

    hooks = settings.setdefault("hooks", {})
    submit_hooks = hooks.setdefault("UserPromptSubmit", [])
    cleaned_submit_hooks = []
    for entry in submit_hooks:
        cleaned_hooks = [
            hook
            for hook in entry.get("hooks", [])
            if "health-skill/scripts/health_check.py" not in hook.get("command", "")
        ]
        if cleaned_hooks:
            new_entry = dict(entry)
            new_entry["hooks"] = cleaned_hooks
            cleaned_submit_hooks.append(new_entry)
    submit_hooks[:] = cleaned_submit_hooks

    hook_entry = {"hooks": [{"type": "command", "command": command}]}

    for entry in submit_hooks:
        for hook in entry.get("hooks", []):
            if hook.get("type") == "command" and hook.get("command") == command:
                settings_file.write_text(json.dumps(settings, indent=2) + "\n")
                return

    submit_hooks.append(hook_entry)
    settings_file.write_text(json.dumps(settings, indent=2) + "\n")


def ensure_slash_command(command_file: Path, install_dir: Path) -> None:
    command_file.parent.mkdir(parents=True, exist_ok=True)
    skill_path = install_dir.expanduser().resolve() / "SKILL.md"
    command_file.write_text(
        "\n".join(
            [
                "---",
                "description: Activate health-skill wellness reminders",
                "---",
                "",
                f"Use @{skill_path}.",
                "",
                "The user explicitly invoked health-skill without another task.",
                "Reply only with the activation sentence in the user's language.",
                "",
            ]
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install health-skill for Claude Code.")
    parser.add_argument("--ref", default=DEFAULT_REF, help="Git ref to install. Defaults to main.")
    parser.add_argument(
        "--install-dir",
        default=str(default_install_dir()),
        help="Where to install the skill. Defaults to ~/.claude/skills/health-skill.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing installation. Currently accepted for compatibility.",
    )
    parser.add_argument(
        "--no-hook",
        action="store_true",
        help="Install files and memory import only; do not modify Claude Code hooks.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    home = claude_home()
    install_dir = Path(args.install_dir).expanduser()
    memory_file = home / "CLAUDE.md"
    settings_file = home / "settings.json"
    command_file = home / "commands" / "health-skill.md"
    runner_file = home / "health-skill-hook.py"

    with tempfile.TemporaryDirectory(prefix="health-skill-install-") as tmp:
        repo_root = download_repo(args.ref, Path(tmp))
        copy_skill(repo_root, install_dir)

    ensure_memory_import(memory_file, memory_import_line(home, install_dir))
    ensure_slash_command(command_file, install_dir)
    ensure_hook_runner(runner_file, install_dir)

    if not args.no_hook:
        ensure_user_prompt_hook(settings_file, quoted_command(Path(sys.executable), runner_file))

    print(f"Installed health-skill to {install_dir}")
    print(f"Updated Claude memory: {memory_file}")
    print(f"Updated Claude slash command: {command_file}")
    print(f"Updated Claude hook runner: {runner_file}")
    if args.no_hook:
        print("Skipped Claude hook setup.")
    else:
        print(f"Updated Claude hooks: {settings_file}")
    print("Restart Claude Code to load the updated memory and hook settings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
