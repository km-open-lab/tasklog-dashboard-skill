# Tasklog Dashboard Skill

`tasklog-dashboard` 是一个 Codex Skill，用来把项目进度记录写得更稳定，并把 `TASKLOG.md` / `项目进度记录.md` 转成静态驾驶舱可以读取的数据。

它适合这些场景：

- 让 Codex 按固定格式更新项目进度记录
- 把 `本次完成` 提取成最近进展时间线
- 把 `后续待办/风险` 提取成待办、风险、未决策卡片
- 给静态 HTML 驾驶舱生成 JavaScript 数据文件
- 把一个项目的工作流沉淀成可分享、可复用的 Codex Skill

## 仓库结构

推荐保持这个结构：

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

真正的 Skill 是 `tasklog-dashboard/` 这个子目录。仓库根目录的 `README.md`、`LICENSE` 和 `.gitignore` 是给 GitHub 用户看的发布文件。

## 安装

克隆仓库：

```bash
git clone https://github.com/km-open-lab/tasklog-dashboard-skill.git
cd tasklog-dashboard-skill
```

把 Skill 复制到 Codex 的技能目录：

```bash
mkdir -p ~/.codex/skills
cp -R tasklog-dashboard ~/.codex/skills/
```

如果 Codex 没有立刻识别新 Skill，重启 Codex。

## 在 Codex 里怎么用

直接点名调用：

```text
使用 $tasklog-dashboard，帮我更新本项目 TASKLOG.md，并刷新驾驶舱数据。
```

也可以这样说：

```text
Use $tasklog-dashboard to update this project's TASKLOG.md and refresh the dashboard.
```

常见用法：

```text
使用 $tasklog-dashboard，把我们刚完成的工作写成一条适合驾驶舱抽取的 Tasklog。
```

```text
使用 $tasklog-dashboard，检查这个项目现有的进度记录格式，并告诉我怎么接入静态驾驶舱。
```

```text
使用 $tasklog-dashboard，从 TASKLOG.md 生成驾驶舱数据。
```

## Tasklog 推荐格式

脚本最适合解析下面这种结构：

```markdown
## YYYY-MM-DD HH:mm CST — 简短任务标题

- 任务类型：功能 / 修复 / UI / 部署 / 决策 / 验证。
- 用户原话/需求摘要：「用户原话或简短摘要」。
- 本次完成：
  1. 已完成的具体改动或已确认的结论。
  2. 第二条完成内容。
- 涉及文件：
  - `path/to/file`
- 验证结果：
  - 运行过的命令、构建结果、健康检查、截图验证，或 `未运行：原因`。
- 后续待办/风险：
  1. 一个可执行的后续事项或风险。
  2. 另一个可执行的后续事项或风险。
- 修改者：Codex。

---
```

抽取规则：

- `本次完成` 会进入最近进展时间线。
- `后续待办/风险` 会进入驾驶舱卡片。
- 如果优先级重要，在待办里写明 `P0`、`P1` 或 `P2`。
- 如果是未决策事项，写明 `未决策`、`待拍板`、`是否`、`选择` 或 `确认`。
- 如果希望领域分类更准确，把领域写进标题或 `任务类型`，例如 `发布`、`安全`、`成本风控`、`Apple Watch`、`教练页`、`训练`、`体测`、`文档`。

更完整的格式说明在：

```text
tasklog-dashboard/references/tasklog-format.md
```

## 生成驾驶舱数据

在你的项目根目录运行：

```bash
python3 ~/.codex/skills/tasklog-dashboard/scripts/build_tasklog_dashboard_data.py \
  TASKLOG.md \
  --output docs/publish/tasklog-dashboard-data.js \
  --global-var TASKLOG_DASHBOARD_DATA
```

脚本只依赖 Python 标准库，不需要安装第三方包。

生成结果类似：

```js
window.TASKLOG_DASHBOARD_DATA = {
  metadata: {
    generatedAt: "2026-06-29 10:06 CST",
    tasklogPath: "TASKLOG.md",
    tasklogLatest: "2026-06-29 10:06 CST",
    tasklogEntries: 223
  },
  timeline: [],
  tasklogTasks: []
};
```

## 接入静态 HTML 驾驶舱

先加载生成的数据文件，再读取全局变量：

```html
<script src="./tasklog-dashboard-data.js"></script>
<script>
  const dashboardData = window.TASKLOG_DASHBOARD_DATA || {};
  const timeline = dashboardData.timeline || [];
  const tasks = dashboardData.tasklogTasks || [];
</script>
```

推荐做法是：关键路线板卡片继续人工维护，Tasklog 生成的待办作为补充数据并入同一个看板。

```js
const allTasks = curatedTasks.concat(dashboardData.tasklogTasks || []);
```

这样既保留人工判断，也不会漏掉最近对话里写进 Tasklog 的待办和风险。

## 校验

基础校验：

```bash
python3 -m py_compile ~/.codex/skills/tasklog-dashboard/scripts/build_tasklog_dashboard_data.py
python3 ~/.codex/skills/tasklog-dashboard/scripts/build_tasklog_dashboard_data.py TASKLOG.md --output /tmp/tasklog-dashboard-data.js
node --check /tmp/tasklog-dashboard-data.js
```

如果你有官方 Skill 校验脚本，并且当前 Python 环境安装了 PyYAML，可以继续跑：

```bash
python3 path/to/quick_validate.py ~/.codex/skills/tasklog-dashboard
```

## 发布注意事项

- 不要提交 `.DS_Store`、`__pycache__/`、`*.pyc`。
- 脚本对优先级、领域、未决策状态的判断是启发式的，关键路线板仍建议人工复核。
- 这个 Skill 不会自动修改你的 HTML 页面。它负责指导 Codex 写好 Tasklog，并提供一个可复用的数据生成脚本。

## English Quick Start

`tasklog-dashboard` is a Codex Skill for maintaining structured project task logs and generating dashboard data from them.

Install:

```bash
git clone https://github.com/km-open-lab/tasklog-dashboard-skill.git
cd tasklog-dashboard-skill
mkdir -p ~/.codex/skills
cp -R tasklog-dashboard ~/.codex/skills/
```

Use in Codex:

```text
Use $tasklog-dashboard to update this project's TASKLOG.md and refresh the dashboard.
```

Generate dashboard data:

```bash
python3 ~/.codex/skills/tasklog-dashboard/scripts/build_tasklog_dashboard_data.py \
  TASKLOG.md \
  --output docs/publish/tasklog-dashboard-data.js \
  --global-var TASKLOG_DASHBOARD_DATA
```
