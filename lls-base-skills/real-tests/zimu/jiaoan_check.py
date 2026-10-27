#!/usr/bin/env python3
"""教案要素与质量规则检查 → Markdown 报告。

用法: python3 jiaoan_check.py 教学设计.json
检查: 要素齐全 / 目标可测量（弱动词点名）/ 过程时间分配合计 / 环节齐备 / 作业存在。
"""
import json
import re
import sys

from lls_jiaoan_utils import WEAK_VERBS

if len(sys.argv) < 2:
    print("[lls-jiaoan] 用法: jiaoan_check.py 教学设计.json")
    sys.exit(1)
e = json.load(open(sys.argv[1], encoding="utf-8"))
problems, passed = [], []

for k in ("topic", "grade", "subject", "goals", "key_points", "difficult_points", "process"):
    if not e.get(k):
        problems.append(f"❌ 要素缺失: {k}")
if problems:
    print("\n".join(problems))
    sys.exit(1)

passed.append("✅ 基础要素齐全（课题/年级/学科/目标/重难点/过程）")

# 目标可测量
weak_found = []
for key in ("knowledge", "skill", "attitude"):
    for g in (e["goals"].get(key) or []):
        for w in WEAK_VERBS:
            if g.startswith(w) and not any(h in g for h in ("能够", "会", "说出", "写出", "演示")):
                weak_found.append(g)
if weak_found:
    problems.append(f"⚠️ {len(weak_found)} 条目标以弱动词开头（{'、'.join(WEAK_VERBS[:5])}），建议改为可测量行为动词（说出/列举/演示/计算…）：")
    for g in weak_found[:5]:
        problems.append(f"    {g[:40]}")
else:
    passed.append("✅ 教学目标均为可测量表述")

# 过程时间合计
minutes = []
for step in e["process"]:
    m = re.search(r"(\d+)", step.get("time", ""))
    if m:
        minutes.append(int(m.group(1)))
total = sum(minutes)
if minutes and total != 45 and e.get("duration", "").find("45") >= 0:
    problems.append(f"⚠️ 过程时间合计 {total} 分钟 ≠ 课时 45 分钟")
elif minutes:
    passed.append(f"✅ 过程时间合计 {total} 分钟")

# 环节齐备
phases = [s.get("phase", "") for s in e["process"]]
if len(e["process"]) < 3:
    problems.append("⚠️ 教学过程少于 3 个环节")
else:
    passed.append(f"✅ 教学过程 {len(e['process'])} 个环节")

# 作业
if not e.get("homework"):
    problems.append("⚠️ 缺作业布置")
else:
    passed.append(f"✅ 作业 {len(e['homework'])} 项")

lines = ["# 教案要素检查报告", ""]
lines += [f"- {p}" for p in passed] + [f"- {p}" for p in problems]
lines += ["", "> 弱动词改为可测量表述由 AI 协助完成；教案格式以学校教研组要求为准。"]
ensure_parent = None
import os
os.makedirs(os.path.dirname(os.path.abspath(sys.argv[2])) or ".", exist_ok=True)
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(lines))
print(f"[lls-jiaoan] 检查完成：通过 {len(passed)}，问题 {len(problems)} → {sys.argv[2]}")
for p in problems:
    print("  " + p)
