#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path


CST = timezone(timedelta(hours=8))
HEADING_RE = re.compile(
    r"^## (?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2})(?::\d{2})? CST [—-] (?P<title>.+)$",
    re.MULTILINE,
)

AREA_RULES = [
    ("发布", ("上架", "发布", "TestFlight", "Apple Developer", "签名", "审核", "Archive")),
    ("安全", ("key", "Secrets", "ATS", "隐私", "权限", "合规", "App Attest")),
    ("成本风控", ("成本", "限流", "防刷", "usage", "token", "Gateway", "网关", "AI")),
    ("Apple Watch", ("Watch", "手表", "睡眠", "心率", "HKWorkoutSession")),
    ("教练页", ("教练", "聊天", "历史", "ChatView", "推荐问题")),
    ("训练", ("训练", "Workout", "动作", "计划")),
    ("体测", ("体测", "体重", "身体", "OCR")),
    ("文档", ("文档", "说明", "报告", "TASKLOG", "驾驶舱")),
]

P0_WORDS = ("P0", "阻断", "必须", "上架前", "正式上架前", "签名", "ATS", "内置 key", "Secrets", "订阅", "隐私", "防刷", "限流")
DECISION_WORDS = ("未决策", "决策", "拍板", "是否", "选择", "确认", "定价", "路线")
SOFT_WORDS = ("手测", "如仍", "如需要", "可考虑", "后续增强", "体验", "优化")


@dataclass
class TasklogEntry:
    date: str
    time: str
    title: str
    body: str
    task_type: str
    user_summary: str
    completed: list[str]
    risks: list[str]


def strip_markdown(value: str) -> str:
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" -。")


def truncate(value: str, limit: int) -> str:
    value = strip_markdown(value)
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def collect_field(body: str, label: str) -> str:
    lines = body.splitlines()
    for index, line in enumerate(lines):
        match = re.match(rf"^- {re.escape(label)}[：:](.*)$", line)
        if not match:
            continue
        block = [match.group(1).strip()]
        for next_line in lines[index + 1 :]:
            if next_line.startswith("- ") or next_line.startswith("## "):
                break
            if next_line.strip() == "---":
                break
            block.append(next_line)
        return "\n".join(block).strip("\n")
    return ""


def list_items(block: str) -> list[str]:
    items: list[str] = []
    for line in block.splitlines():
        match = re.match(r"^\s*(?:[-*]|\d+\.)\s+(.+)$", line)
        if match:
            items.append(strip_markdown(match.group(1)))
    lines = block.splitlines()
    first_line = strip_markdown(lines[0]) if lines else ""
    if first_line and not items:
        items.append(first_line)
    return [item for item in items if item and item != "无"]


def parse_tasklog(text: str) -> list[TasklogEntry]:
    matches = list(HEADING_RE.finditer(text))
    entries: list[TasklogEntry] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        entries.append(
            TasklogEntry(
                date=match.group("date"),
                time=match.group("time"),
                title=strip_markdown(match.group("title")),
                body=body,
                task_type=strip_markdown(collect_field(body, "任务类型")),
                user_summary=strip_markdown(collect_field(body, "用户原话/需求摘要")),
                completed=list_items(collect_field(body, "本次完成")),
                risks=list_items(collect_field(body, "后续待办/风险")),
            )
        )
    return entries


def infer_area(text: str) -> str:
    lower = text.lower()
    for area, keywords in AREA_RULES:
        if any(keyword.lower() in lower for keyword in keywords):
            return area
    return "项目管理"


def infer_priority(text: str) -> str:
    if any(word in text for word in P0_WORDS):
        return "P0"
    if any(word in text for word in SOFT_WORDS):
        return "P2"
    return "P1"


def infer_status(text: str) -> str:
    if any(word in text for word in DECISION_WORDS):
        return "未决策"
    return "待办"


def build_timeline(entries: list[TasklogEntry], limit: int) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for entry in entries[:limit]:
        first_done = entry.completed[0] if entry.completed else entry.user_summary
        text_parts = [part for part in (entry.task_type, first_done) if part]
        output.append(
            {
                "time": f"{entry.date[5:]} {entry.time}",
                "title": truncate(entry.title, 34),
                "text": truncate("；".join(text_parts), 92),
            }
        )
    return output


def build_risk_cards(entries: list[TasklogEntry], limit: int) -> list[dict[str, object]]:
    cards: list[dict[str, object]] = []
    seen: set[str] = set()
    for entry in entries:
        context = " ".join([entry.title, entry.task_type, entry.user_summary])
        for offset, risk in enumerate(entry.risks, start=1):
            normalized = truncate(risk, 120)
            if normalized in seen:
                continue
            seen.add(normalized)
            text = " ".join([context, risk])
            cards.append(
                {
                    "id": f"tasklog-{entry.date.replace('-', '')}-{entry.time.replace(':', '')}-{offset}",
                    "title": truncate(f"待跟进：{risk}", 30),
                    "status": infer_status(text),
                    "priority": infer_priority(text),
                    "area": infer_area(text),
                    "type": "TASKLOG 待跟进",
                    "source": f"TASKLOG {entry.date} {entry.time}",
                    "summary": normalized,
                    "checklist": [],
                }
            )
            if len(cards) >= limit:
                return cards
    return cards


def build_payload(tasklog_path: Path, timeline_limit: int, risk_limit: int) -> dict[str, object]:
    entries = parse_tasklog(tasklog_path.read_text(encoding="utf-8"))
    latest = f"{entries[0].date} {entries[0].time} CST" if entries else ""
    return {
        "metadata": {
            "generatedAt": datetime.now(CST).strftime("%Y-%m-%d %H:%M CST"),
            "tasklogPath": str(tasklog_path),
            "tasklogLatest": latest,
            "tasklogEntries": len(entries),
        },
        "timeline": build_timeline(entries, timeline_limit),
        "tasklogTasks": build_risk_cards(entries, risk_limit),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build dashboard data from a Codex-style tasklog.")
    parser.add_argument("tasklog", type=Path)
    parser.add_argument("--output", type=Path, default=Path("tasklog-dashboard-data.js"))
    parser.add_argument("--global-var", default="TASKLOG_DASHBOARD_DATA")
    parser.add_argument("--timeline-limit", type=int, default=10)
    parser.add_argument("--risk-limit", type=int, default=30)
    args = parser.parse_args()

    payload = build_payload(args.tasklog, args.timeline_limit, args.risk_limit)
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "// Generated by tasklog-dashboard/scripts/build_tasklog_dashboard_data.py. Do not edit by hand.\n"
        f"window.{args.global_var} = {body};\n",
        encoding="utf-8",
    )
    print(f"wrote {args.output}")
    print(
        f"entries={payload['metadata']['tasklogEntries']} "
        f"timeline={len(payload['timeline'])} tasklogTasks={len(payload['tasklogTasks'])}"
    )


if __name__ == "__main__":
    main()
