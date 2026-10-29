#!/usr/bin/env python3
"""教案要素与质量规则检查 → Markdown 报告。

用法: python3 jiaoan_check.py 教学设计.json -o 预检报告.md
检查: 要素齐全 / 目标可测量（弱动词点名）/ 过程时间分配合计 / 环节齐备 / 作业存在。
"""
import argparse
import json
import re

from lls_jiaoan_utils import WEAK_VERBS, die, ensure_parent

ap = argparse.ArgumentParser()
ap.add_argument("json")
ap.add_argument("-o", "--output", required=True)
args = ap.parse_args()

try:
    with open(args.json, encoding="utf-8") as f:
        e = json.load(f)
except (OSError, ValueError) as exc:
    die(f"无法读取教学设计 JSON: {exc}")
if not isinstance(e, dict):
    die("教学设计 JSON 顶层须为对象")
problems, passed = [], []

for k in ("topic", "grade", "subject", "goals", "key_points", "difficult_points", "process"):
    if not e.get(k):
        problems.append(f"❌ 要素缺失: {k}")
if not problems:
    passed.append("✅ 基础要素齐全（课题/年级/学科/目标/重难点/过程）")

goals = e.get("goals") if isinstance(e.get("goals"), dict) else {}
process = e.get("process") if isinstance(e.get("process"), list) else []
weak_found = []
for key in ("knowledge", "skill", "attitude"):
    for g in (goals.get(key) or []):
        if not isinstance(g, str):
            continue
        for w in WEAK_VERBS:
            if g.startswith(w) and not any(h in g for h in ("能够", "会", "说出", "写出", "演示")):
                weak_found.append(g)
if weak_found:
    problems.append(f"⚠️ {len(weak_found)} 条目标以弱动词开头，建议改为可测量行为动词（说出/列举/演示/计算…）：")
    for g in weak_found[:5]:
        problems.append(f"    {g[:40]}")
else:
    passed.append("✅ 教学目标均为可测量表述")

minutes = []
for step in process:
    if not isinstance(step, dict):
        continue
    m = re.search(r"(\d+)", str(step.get("time", "") or ""))
    if m:
        minutes.append(int(m.group(1)))
total = sum(minutes)
# 课时按 duration 的分钟数解析（如“40 分钟”/“40分钟”/纯数字）；无分钟数时不作合计判定
dur_text = str(e.get("duration", "") or "")
dur_match = re.search(r"(\d+)", dur_text) if ("分" in dur_text or dur_text.strip().isdigit()) else None
dur = int(dur_match.group(1)) if dur_match else None
if minutes and dur is not None and total != dur:
    problems.append(f"⚠️ 过程时间合计 {total} 分钟 ≠ 课时 {dur} 分钟")
elif minutes:
    passed.append(f"✅ 过程时间合计 {total} 分钟")

if len(process) < 3:
    problems.append("⚠️ 教学过程少于 3 个环节")
else:
    passed.append(f"✅ 教学过程 {len(process)} 个环节")

if not e.get("homework"):
    problems.append("⚠️ 缺作业布置")
else:
    passed.append(f"✅ 作业 {len(e['homework'])} 项")

lines = ["# 教案要素检查报告", ""]
lines += [f"- {p}" for p in passed] + [f"- {p}" for p in problems]
lines += ["", "> 弱动词改为可测量表述由 AI 协助完成；教案格式以学校教研组要求为准。"]
ensure_parent(args.output)
open(args.output, "w", encoding="utf-8").write("\n".join(lines))
print(f"[lls-jiaoan] 检查完成：通过 {len(passed)}，问题 {len(problems)} → {args.output}")
for p in problems:
    print("  " + p)
