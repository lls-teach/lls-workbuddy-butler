#!/usr/bin/env python3
"""投标文件 × 要求清单 → 内部核对偏离表（✅响应/⚠️部分/❌未响应 + 缺要素提示）。

用法: python3 biaoshu_check.py 要求清单.json 投标文件.txt -o 偏离表.md
⚠️ 输出为内部核对工具：正式偏离表以招标方指定格式为准。
"""
import argparse
import json

from lls_biaoshu_utils import die, ensure_parent, judge_response

ap = argparse.ArgumentParser()
ap.add_argument("requirements")
ap.add_argument("bid")
ap.add_argument("-o", "--output", required=True)
args = ap.parse_args()

try:
    reqs = json.load(open(args.requirements, encoding="utf-8"))["requirements"]
except (OSError, json.JSONDecodeError, KeyError) as e:
    die(f"找不到或无法解析要求清单：{args.requirements}（{e}）")
try:
    bid = open(args.bid, encoding="utf-8", errors="ignore").read()
except OSError as e:
    die(f"找不到或无法读取投标文件：{args.bid}（{e}）")

lines = ["# 投标偏离核对表（内部核对用）", "",
         "> ⚠️ 机器核对仅供内部自查：判定基于关键词覆盖，正式偏离表以招标文件指定格式与投标文件原文为准。", ""]
counts = {"✅ 响应": 0, "⚠️ 部分响应": 0, "❌ 未响应": 0}
for r in reqs:
    verdict = judge_response(r["req"], bid)
    counts[verdict] += 1
    lines.append(f"### {verdict}｜{r['cat']}")
    lines.append(f"- 招标要求：{r['req']}")
    lines.append("")
lines.insert(4, f"- 汇总：✅ {counts['✅ 响应']} ｜ ⚠️ {counts['⚠️ 部分响应']} ｜ ❌ {counts['❌ 未响应']}（共 {len(reqs)} 条）")
ensure_parent(args.output)
open(args.output, "w", encoding="utf-8").write("\n".join(lines))
print(f"[lls-biaoshu] 偏离表 → {args.output}")
print(f"[lls-biaoshu] ✅响应 {counts['✅ 响应']} | ⚠️部分 {counts['⚠️ 部分响应']} | ❌未响应 {counts['❌ 未响应']}")
if counts["❌ 未响应"] or counts["⚠️ 部分响应"]:
    print("[lls-biaoshu] 🔴 未响应/部分响应项逐条人工确认——废标风险就在这些行里")
