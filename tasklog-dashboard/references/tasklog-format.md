# Tasklog Format Reference

Use this reference when a project needs a durable progress log that can also feed a dashboard.

## Canonical Shape

Prefer this shape unless the project already has a different fixed format:

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

## Dashboard Extraction Contract

The bundled extractor expects:

- Heading: `## YYYY-MM-DD HH:mm CST — Title`
- Timeline text: first useful item under `本次完成`
- Dashboard follow-up cards: each bullet under `后续待办/风险`
- Priority hints: include `P0`, `P1`, or `P2` inside a follow-up when automatic inference would be ambiguous
- Decision hints: include `未决策`, `待拍板`, `是否`, `选择`, or `确认` for items that should appear as decision cards
- Area hints: put the area in `任务类型` or title, for example `发布`, `教练页`, `安全`, `成本风控`, `Apple Watch`, `训练`, `体测`, or `文档`

## Writing Quality Rules

- Write newest-first unless the existing file uses another chronology.
- Prefer confirmed facts and outcomes over chat transcripts.
- Keep follow-up bullets atomic; split combined risks into separate bullets.
- Mention validation honestly. If none was run, say why.
- Include affected files so future agents can jump straight to the right surface.
- Do not create a new `TASKLOG.md` or `项目进度记录.md` in projects that do not already keep one unless the user asks.

## Good Follow-Up Bullets

- `P0 正式上架前必须移除 App 内置 provider key，并确认 IPA 中不再包含 Secrets.swift 回退。`
- `未决策：海外首发是否排除欧盟区，需要结合 provider 数据驻留和隐私披露再拍板。`
- `P2 需要用户手测历史展开后的滚动落点，如仍跳动再改成顶部抽屉。`

## Weak Follow-Up Bullets

- `继续优化。`
- `还有一些问题。`
- `后面再看。`

These are weak because the dashboard cannot infer owner, severity, domain, or next action.
