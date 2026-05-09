# Health Skill

Use this project as a lightweight wellness guard for AI-assisted work.

At the start of a user request, silently run:

```bash
python3 scripts/health_check.py --quiet
```

If the command prints nothing, do not mention health and continue the user's task normally.

If the command prints JSON with `should_remind: true`, give a brief 1-2 sentence reminder and immediately continue the user's main task. Prefer Chinese when the user is speaking Chinese.

The script stores session state in the system temp directory by default. To choose a custom location, set `HEALTH_SKILL_STATE_FILE` to an absolute path.

This is not medical diagnosis. For emergency-like symptoms, advise urgent medical help.

Install or update this project for Claude Code with:

```bash
python3 -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/RTX2080/Health-skill/main/tools/install_claude_skill.py').read())"
```

After installation, `/health-skill` activates the skill.
