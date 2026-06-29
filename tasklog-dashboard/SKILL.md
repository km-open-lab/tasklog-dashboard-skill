---
name: tasklog-dashboard
description: Create, update, and operationalize project task logs and dashboard links. Use when the user wants to write or standardize TASKLOG.md / 项目进度记录.md entries, connect a progress log to a static dashboard, generate dashboard data from task logs, or package a reusable progress-log/dashboard workflow as a Codex skill.
---

# Tasklog Dashboard

## Overview

Use this skill to keep project progress logs useful as both human memory and dashboard data. The core loop is: write structured tasklog entries, extract recent progress and follow-up risks, then refresh a dashboard data file.

## Workflow

1. Find the canonical progress file before editing.
   Prefer the file named by the user, then existing files such as `项目进度记录.md`, `TASKLOG.md`, `tasklog.md`, `CHANGELOG.md`, or `.codex/tasklog.md`.
2. Read the top of the file and preserve its format.
   Newest entries usually belong near the top. Do not invent a new progress file if none exists unless the user asks.
3. Write tasklog entries with dashboard extraction in mind.
   For the full field contract and examples, read `references/tasklog-format.md`.
4. Refresh dashboard data when the project has a dashboard.
   If the project has its own script, prefer it. Otherwise run `scripts/build_tasklog_dashboard_data.py` with explicit paths.
5. Validate the result.
   Check generated JSON/JS syntax, parse the HTML if relevant, and confirm the dashboard still has fallback content if generated data is missing.

## Dashboard Refresh

Generic command:

```bash
python3 /path/to/tasklog-dashboard/scripts/build_tasklog_dashboard_data.py \
  TASKLOG.md \
  --output docs/publish/tasklog-dashboard-data.js \
  --global-var TASKLOG_DASHBOARD_DATA
```

The script reads headings like `## YYYY-MM-DD HH:mm CST — Title`, creates a recent timeline from `本次完成`, and creates dashboard cards from `后续待办/风险`.

## Writing Rules

- Preserve existing project conventions over this skill's defaults.
- Record confirmed facts, touched files, validation, and remaining risks.
- Keep each `后续待办/风险` bullet as one actionable item; include `P0`, `P1`, or `P2` in the text when priority must be explicit.
- Mark decision items with words such as `未决策`, `待拍板`, or `是否`, so dashboard extraction can classify them.
- Do not log pure chat, read-only exploration, or simple Q&A unless the user explicitly asks for a progress entry.
- Never claim validation that was not run; write `未运行` with the reason instead.

## Resources

- `references/tasklog-format.md`: read when creating a new format, explaining tasklog writing, or improving extraction quality.
- `scripts/build_tasklog_dashboard_data.py`: generic extractor that emits a JavaScript global for static dashboards.
