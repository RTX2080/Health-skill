---
name: health-skill
description: Gentle, time-aware wellness reminders for AI work sessions. Use when Codex should check local time, notice late-night work, remind the user to drink water, move, rest their eyes, or wrap up without interrupting the user's main task; also use when the user explicitly asks for health-skill, late-night reminders, long-session reminders, hydration reminders, movement breaks, sleep hygiene nudges, or non-medical wellbeing support during AI-assisted work.
---

# Health Skill

## Core Rule

Help the user stay healthy while continuing the requested task. Keep reminders brief, kind, and non-disruptive. Never turn the response into a lecture unless the user asks for detail.

## Quick Workflow

1. Check the current local time before giving a health reminder. Prefer running `scripts/health_check.py`; if tools are unavailable, use the environment's current date/time.
2. Pass known session context to the script when reliable data exists:
   - `--elapsed-minutes`: elapsed active conversation/work-session time.
   - `--unfocused-minutes`: time away from the app, but only if a reliable app/browser signal is available.
   - `--session-start`: ISO timestamp, when elapsed time is easier to compute from a start time.
3. Do not invent focus state. If focus-away time is unavailable, omit it and use a softer long-session reminder only when the conversation itself has clearly lasted about an hour.
4. If a reminder is needed, write 1-2 short sentences and immediately continue the user's task.
5. If the user asks not to receive health reminders, respect that preference for the current task unless there is an urgent safety concern.

## Reminder Triggers

Use these default thresholds unless the user configures different ones:

- `22:30-23:59`: late evening. Suggest wrapping up, drinking water, and relaxing eyes/neck.
- `00:00-01:59`: late night. More clearly encourage sleep soon and mention reduced attention.
- `02:00-04:59`: severe late night. Strongly recommend stopping soon and resting.
- Active session `>= 60` minutes with `unfocused-minutes < 5`: remind the user to stand up, drink water, and rest eyes.
- Active session `>= 60` minutes with unknown focus data: use a gentler "if you have been here continuously" reminder.

Avoid repeating the same reminder more than once per natural work session unless the user explicitly asks for continuing reminders.

## Non-Disruptive Style

Place the reminder as a small aside before a status update or before continuing the answer:

`现在已经有点晚了，先喝口水、活动一下肩颈。我继续帮你把这个问题处理完。`

Keep the main answer focused on the user's task. Do not delay tool use, code edits, debugging, or requested explanations just to expand the health advice.

## Safety Boundary

This skill provides general wellbeing nudges, not medical diagnosis or treatment. If the user mentions chest pain, trouble breathing, fainting, severe pain, acute neurological symptoms, or any emergency-like condition, advise them to seek urgent medical help immediately and continue only if appropriate.

## Resources

- `scripts/health_check.py`: deterministic local-time and long-session decision helper.
- `references/reminder_templates.md`: short reminder templates and tone guidance. Load it when writing reminders or customizing copy.
