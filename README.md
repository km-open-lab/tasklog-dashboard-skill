# Tasklog Dashboard Skill

`tasklog-dashboard` is a Codex Skill for keeping project progress logs structured and turning them into dashboard data.

It helps Codex:

- find and update a project's canonical progress log, such as `TASKLOG.md` or `项目进度记录.md`
- write tasklog entries in a consistent, dashboard-friendly format
- extract recent progress from `本次完成`
- extract follow-up items, risks, and open decisions from `后续待办/风险`
- generate a JavaScript data file that a static HTML dashboard can load

## Repository Layout

Recommended GitHub layout:

```text
tasklog-dashboard-skill/
  README.md
  LICENSE
  .gitignore
  tasklog-dashboard/
    SKILL.md
    agents/openai.yaml
    references/tasklog-format.md
    scripts/build_tasklog_dashboard_data.py
```

If you publish this directory directly as the repository root, keep the same files and make sure `SKILL.md` stays at the root.

## Install

Clone or download the repository, then copy the Skill folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R tasklog-dashboard ~/.codex/skills/
```

If your repository root is the Skill folder itself:

```bash
mkdir -p ~/.codex/skills
cp -R /path/to/tasklog-dashboard ~/.codex/skills/
```

Restart Codex if the Skill does not appear immediately.

## Use In Codex

Mention the Skill explicitly:

```text
Use $tasklog-dashboard to update this project's TASKLOG.md and refresh the dashboard.
```

Chinese example:

```text
使用 $tasklog-dashboard，帮我更新项目 TASKLOG，并刷新驾驶舱数据。
```

Other useful prompts:

```text
Use $tasklog-dashboard to create a dashboard-friendly tasklog entry for the work we just finished.
```

```text
Use $tasklog-dashboard to inspect this repo's progress log format and tell me how to connect it to a static dashboard.
```

```text
Use $tasklog-dashboard to generate dashboard data from TASKLOG.md.
```

## Tasklog Format

The extractor works best with entries shaped like this:

```markdown
## YYYY-MM-DD HH:mm CST — Short task title

- 任务类型：Feature / bug fix / UI / deployment / decision / validation.
- 用户原话/需求摘要：「User request or concise summary」。
- 本次完成：
  1. Concrete completed change or confirmed conclusion.
  2. Another concrete item.
- 涉及文件：
  - `path/to/file`
- 验证结果：
  - Command, build, health check, screenshot, or `未运行：reason`.
- 后续待办/风险：
  1. One actionable follow-up or risk.
  2. Another actionable follow-up or risk.
- 修改者：Codex。

---
```

Dashboard extraction rules:

- `本次完成` feeds the recent-progress timeline.
- `后续待办/风险` feeds dashboard cards.
- Add `P0`, `P1`, or `P2` to follow-up bullets when priority matters.
- Add words like `未决策`, `待拍板`, `是否`, `选择`, or `确认` when an item should be classified as an open decision.

More detail lives in:

```text
references/tasklog-format.md
```

## Generate Dashboard Data

Run the bundled script from your project root:

```bash
python3 ~/.codex/skills/tasklog-dashboard/scripts/build_tasklog_dashboard_data.py \
  TASKLOG.md \
  --output docs/publish/tasklog-dashboard-data.js \
  --global-var TASKLOG_DASHBOARD_DATA
```

The script has no third-party Python dependencies.

Output shape:

```js
window.TASKLOG_DASHBOARD_DATA = {
  metadata: {
    generatedAt: "2026-06-26 09:35 CST",
    tasklogPath: "TASKLOG.md",
    tasklogLatest: "2026-06-26 09:35 CST",
    tasklogEntries: 174
  },
  timeline: [],
  tasklogTasks: []
};
```

## Connect A Static HTML Dashboard

Load the generated data before your dashboard script:

```html
<script src="./tasklog-dashboard-data.js"></script>
<script>
  const dashboardData = window.TASKLOG_DASHBOARD_DATA || {};
  const timeline = dashboardData.timeline || [];
  const tasks = dashboardData.tasklogTasks || [];
</script>
```

A practical pattern is to keep important roadmap cards curated by hand, then merge generated tasklog follow-ups into the same board:

```js
const allTasks = curatedTasks.concat(dashboardData.tasklogTasks || []);
```

## Validate

Basic checks:

```bash
python3 -m py_compile ~/.codex/skills/tasklog-dashboard/scripts/build_tasklog_dashboard_data.py
python3 ~/.codex/skills/tasklog-dashboard/scripts/build_tasklog_dashboard_data.py TASKLOG.md --output /tmp/tasklog-dashboard-data.js
node --check /tmp/tasklog-dashboard-data.js
```

If you have the official Skill validator and PyYAML installed:

```bash
python3 path/to/quick_validate.py ~/.codex/skills/tasklog-dashboard
```

## Notes

- Do not commit `.DS_Store`, `__pycache__/`, or `*.pyc`.
- The script uses heuristics for priority, area, and decision classification. Critical roadmap cards should still be reviewed by a human.
- The Skill does not automatically modify dashboards. It guides Codex and provides a reusable extractor script.
