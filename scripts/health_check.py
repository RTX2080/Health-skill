#!/usr/bin/env python3
"""Decision helper for health-skill reminders."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ReminderDecision:
    now: str
    hour: int
    minute: int
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
    elapsed_minutes: Optional[float],
    unfocused_minutes: Optional[float],
) -> str:
    if elapsed_minutes is None or elapsed_minutes < 60:
        return "none"
    if unfocused_minutes is None:
        return "long_session_focus_unknown"
    if unfocused_minutes < 5:
        return "long_focused_session"
    return "long_session_with_break"


def compute_elapsed_minutes(
    now: datetime,
    elapsed_arg: Optional[float],
    session_start_arg: Optional[str],
) -> Optional[float]:
    if elapsed_arg is not None:
        return elapsed_arg
    if not session_start_arg:
        return None
    started = parse_iso_datetime(session_start_arg)
    if started.tzinfo and not now.tzinfo:
        now = now.astimezone()
    if now.tzinfo and not started.tzinfo:
        started = started.replace(tzinfo=now.tzinfo)
    return max(0.0, (now - started).total_seconds() / 60)


def make_decision(
    now: datetime,
    elapsed_minutes: Optional[float],
    unfocused_minutes: Optional[float],
) -> ReminderDecision:
    night_level = determine_night_level(now.hour, now.minute)
    session_level = determine_session_level(elapsed_minutes, unfocused_minutes)

    reasons: list[str] = []
    if night_level != "none":
        reasons.append(night_level)
    if session_level in {"long_focused_session", "long_session_focus_unknown"}:
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
    parser.add_argument("--session-start", help="Optional ISO timestamp for session start.")
    parser.add_argument("--elapsed-minutes", type=float, help="Known active session length.")
    parser.add_argument(
        "--unfocused-minutes",
        type=float,
        help="Known time away from the app. Omit if no reliable focus signal exists.",
    )
    args = parser.parse_args()

    now = local_now(args.now)
    elapsed_minutes = compute_elapsed_minutes(now, args.elapsed_minutes, args.session_start)
    decision = make_decision(now, elapsed_minutes, args.unfocused_minutes)
    print(json.dumps(asdict(decision), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
