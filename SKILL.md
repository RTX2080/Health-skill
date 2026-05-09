---
name: health-skill
description: Lightweight automatic wellness guard for AI work sessions. Use implicitly for silent local-time/session prechecks, especially during coding or long AI-assisted work; do not mention health unless a late-night, long-session, rest, hydration, or urgent wellbeing trigger is actually met. Also use when the user explicitly asks for health-skill or non-medical wellbeing support.
---

# Health Skill

## Core Rule

Stay silent unless a reminder trigger is met. When no trigger is met, output nothing about health and continue the user's task normally.

## Lightweight Precheck

1. Prefer the environment's current local time when it is already available.
2. Run `scripts/health_check.py --quiet` when checking reminder state. The script stores the first work timestamp in the system temp directory by default; set `HEALTH_SKILL_STATE_FILE` to override it.
3. If `now - session_started_at >= 60 minutes`, give one long-session reminder and let the script reset `session_started_at` to the current time.
4. Load `references/reminder_templates.md` only after a reminder trigger is confirmed.

## Triggers

- `22:30-23:59`: brief late-evening wrap-up reminder.
- `00:00-01:59`: clearer late-night sleep reminder.
- `02:00-04:59`: firm but kind severe-late-night reminder.
- Stored work session `>= 60` minutes: movement, water, and eye-rest reminder. After this reminder, the script resets the stored start time to now.
- Emergency-like symptoms: advise urgent medical help.

Avoid repeating a reminder more than once per natural work session unless the user asks for continuing reminders.

## Output Style

If the user explicitly invokes this skill without another task, reply only in the user's language:

- Chinese: `Health skill 已激活，会在适当的时候提醒你。`
- English: `Health skill is active. I will remind you when appropriate.`

If triggered, write 1-2 short sentences, then immediately continue the user's main task. Prefer Chinese when the user is speaking Chinese.

If not triggered, say nothing about health.

This skill provides general wellbeing nudges, not medical diagnosis or treatment.
