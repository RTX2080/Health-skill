#!/usr/bin/env python3
"""Install this repo as a local Codex skill."""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install health-skill for Codex.")
    parser.add_argument(
        "--dest",
        default=str(codex_home() / "skills" / "health-skill"),
        help="Destination skill directory. Defaults to ~/.codex/skills/health-skill.",
    )
    parser.add_argument("--force", action="store_true", help="Replace existing install.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    src = Path(__file__).resolve().parents[1]
    dest = Path(args.dest).expanduser()
    if dest.exists():
        if not args.force:
            raise SystemExit(f"Destination exists: {dest}. Use --force to replace it.")
        shutil.rmtree(dest)
    ignore = shutil.ignore_patterns(".git", "__pycache__", "*.pyc")
    shutil.copytree(src, dest, ignore=ignore)
    print(f"Installed health-skill to {dest}")
    print("Restart Codex to load the skill.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
