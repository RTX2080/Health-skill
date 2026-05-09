# health-skill 安装说明

本项目整个 repo 就是一个 skill 目录。目标效果是：安装后，AI 在每次工作请求前静默检查健康提醒条件；没触发时完全不说话，触发时只短提醒一句。

## Claude Code（推荐）

一行安装或更新：

```bash
python3 -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/RTX2080/Health-skill/main/scripts/install_claude.py').read())"
```

安装器会自动：

- 下载 repo 到 `~/.claude/skills/health-skill`
- 在 `~/.claude/CLAUDE.md` 添加 import
- 在 `~/.claude/settings.json` 添加 `UserPromptSubmit` hook
- 创建 slash command：`~/.claude/commands/health-skill.md`

重启 Claude Code 后可用：

```text
/health-skill
```

或者直接继续正常工作；hook 会静默运行 `health_check.py --quiet`。

手动 clone 方式：

```bash
git clone https://github.com/RTX2080/Health-skill ~/.claude/skills/health-skill
```

## Codex

一行安装：

```bash
git clone https://github.com/RTX2080/Health-skill ~/.codex/skills/health-skill
```

安装后重启 Codex。Codex 会把 `health-skill` 当作本地 skill 发现。

## 验证

```bash
python3 ~/.claude/skills/health-skill/scripts/health_check.py --quiet
python3 ~/.claude/skills/health-skill/scripts/health_check.py --now 2026-05-09T22:30:00+08:00 --quiet
```

第一条没输出表示当前没有触发提醒；第二条会输出 `late_evening` 触发结果。

## 目录结构

```text
health-skill/
├── SKILL.md
├── CLAUDE.md
├── INSTALL.md
├── agents/
│   └── openai.yaml
├── references/
│   └── reminder_templates.md
└── scripts/
    ├── health_check.py
    └── install_claude.py
```
