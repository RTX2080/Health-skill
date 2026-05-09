#!/usr/bin/env python3
"""Decision helper for health-skill reminders."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


DEFAULT_SESSION_MINUTES = 60
DEFAULT_STATE_FILE = "~/.codex/health-skill/session_state.json"


@dataclass
class ReminderDecision:
    now: str
    hour: int
    minute: int
    session_started_at: str
    session_elapsed_minutes: float
    night_level: str
    session_level: str
    should_remind: bool
    reasons: list[str]
    suggested_tone: str


def parse_iso_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def local_now(now_arg: Optional[str]) -> datetime:
    if now_arg:
        parsed = parse_iso_datetime(now_arg)
        return parsed.astimezone() if parsed.tzinfo else parsed
    return datetime.now().astimezone()


def determine_night_level(hour: int, minute: int) -> str:
    minutes = hour * 60 + minute
    if 2 * 60 <= minutes <= 4 * 60 + 59:
        return "severe_late_night"
    if minutes < 2 * 60:
        return "late_night"
    if 22 * 60 + 30 <= minutes <= 23 * 60 + 59:
        return "late_evening"
    return "none"


def determine_session_level(
    elapsed_minutes: float,
    threshold_minutes: float,
) -> str:
    if elapsed_minutes < threshold_minutes:
        return "none"
    return "long_session"


def default_state_file() -> Path:
    return Path(os.environ.get("HEALTH_SKILL_STATE_FILE", DEFAULT_STATE_FILE)).expanduser()


def read_session_start(state_file: Path, now: datetime) -> datetime:
    if not state_file.exists():
        return now
    try:
        payload = json.loads(state_file.read_text())
        started_raw = payload.get("session_started_at")
        if not started_raw:
            return now
        started = parse_iso_datetime(started_raw)
    except (OSError, ValueError, TypeError):
        return now
    if now.tzinfo and not started.tzinfo:
        started = started.replace(tzinfo=now.tzinfo)
    if started > now:
        return now
    return started


def write_session_start(state_file: Path, started: datetime, now: datetime) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "session_started_at": started.isoformat(timespec="seconds"),
        "last_checked_at": now.isoformat(timespec="seconds"),
    }
    state_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2))


def elapsed_minutes(now: datetime, started: datetime) -> float:
    if started.tzinfo and not now.tzinfo:
        now = now.astimezone()
    if now.tzinfo and not started.tzinfo:
        started = started.replace(tzinfo=now.tzinfo)
    return max(0.0, (now - started).total_seconds() / 60)


def make_decision(
    now: datetime,
    session_started_at: datetime,
    session_elapsed_minutes: float,
    threshold_minutes: float,
) -> ReminderDecision:
    night_level = determine_night_level(now.hour, now.minute)
    session_level = determine_session_level(session_elapsed_minutes, threshold_minutes)

    reasons: list[str] = []
    if night_level != "none":
        reasons.append(night_level)
    if session_level == "long_session":
        reasons.append(session_level)

    suggested_tone = "none"
    if "severe_late_night" in reasons:
        suggested_tone = "firm_but_kind"
    elif "late_night" in reasons:
        suggested_tone = "clear_and_brief"
    elif reasons:
        suggested_tone = "gentle_aside"

    return ReminderDecision(
        now=now.isoformat(timespec="minutes"),
        hour=now.hour,
        minute=now.minute,
        session_started_at=session_started_at.isoformat(timespec="minutes"),
        session_elapsed_minutes=round(session_elapsed_minutes, 1),
        night_level=night_level,
        session_level=session_level,
        should_remind=bool(reasons),
        reasons=reasons,
        suggested_tone=suggested_tone,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check whether health-skill should give a brief reminder."
    )
    parser.add_argument("--now", help="Optional ISO timestamp. Defaults to local system time.")
    parser.add_argument(
        "--state-file",
        default=str(default_state_file()),
        help="Path to session state JSON. Defaults to ~/.codex/health-skill/session_state.json.",
    )
    parser.add_argument(
        "--session-minutes",
        type=float,
        default=DEFAULT_SESSION_MINUTES,
        help="Minutes before a long-session reminder triggers. Defaults to 60.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print nothing when no reminder is needed. If triggered, print compact JSON.",
    )
    args = parser.parse_args()

    now = local_now(args.now)
    state_file = Path(args.state_file).expanduser()
    session_started_at = read_session_start(state_file, now)
    session_elapsed_minutes = elapsed_minutes(now, session_started_at)
    decision = make_decision(
        now,
        session_started_at,
        session_elapsed_minutes,
        args.session_minutes,
    )
    next_session_start = now if session_elapsed_minutes >= args.session_minutes else session_started_at
    write_session_start(state_file, next_session_start, now)
    if args.quiet and not decision.should_remind:
        return
    indent = None if args.quiet else 2
    print(json.dumps(asdict(decision), ensure_ascii=False, indent=indent))


if __name__ == "__main__":
    main()
