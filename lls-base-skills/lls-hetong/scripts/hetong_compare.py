#!/usr/bin/env python3
"""两版合同条款级 diff（改了哪些条款、原文/新文对照）。

用法: python3 hetong_compare.py 旧版.txt 新版.txt -o 对比.md
"""
import argparse
import difflib

from lls_hetong_utils import ensure_parent, split_clauses

ap = argparse.ArgumentParser()
ap.add_argument("old")
ap.add_argument("new")
ap.add_argument("-o", "--output", required=True)
args = ap.parse_args()

old_c = dict(split_clauses(open(args.old, encoding="utf-8", errors="ignore").read()))
new_c = dict(split_clauses(open(args.new, encoding="utf-8", errors="ignore").read()))

lines = ["# 两版合同条款对比", ""]
for head in old_c:
    if head not in new_c:
        lines.append(f"## ❌ {head}：新版已删除")
        lines.append(f"- 旧文摘录：{old_c[head][:120]}…")
    elif old_c[head] != new_c.get(head):
        diff = list(difflib.unified_diff(old_c[head].split("\n"), new_c[head].split("\n"), lineterm=""))
        changed = [d for d in diff if d.startswith(("+", "-")) and not d.startswith(("+++", "---"))]
        lines.append(f"## ✏️ {head}：有修改（{len(changed)} 行差异）")
        for d in changed[:6]:
            lines.append(f"- {d[:120]}")
for head in new_c:
    if head not in old_c:
        lines.append(f"## ➕ {head}：新版新增")
        lines.append(f"- {new_c[head][:120]}…")
if len(lines) == 2:
    lines.append("- 两版条款无差异")
ensure_parent(args.output)
open(args.output, "w", encoding="utf-8").write("\n".join(lines))
print(f"[lls-hetong] 对比完成 → {args.output}（旧 {len(old_c)} 段 / 新 {len(new_c)} 段）")
