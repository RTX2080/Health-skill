#!/usr/bin/env python3
"""Compatibility entrypoint for Claude Code installation."""

from __future__ import annotations

import runpy
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "install_claude.py"


if __name__ == "__main__":
    runpy.run_path(str(SCRIPT), run_name="__main__")
