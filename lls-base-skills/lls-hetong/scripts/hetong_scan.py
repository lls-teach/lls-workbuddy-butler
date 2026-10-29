#!/usr/bin/env python3
"""合同风险扫描（规则关键词级，非法律意见）：条款切分 + 风险点定位 + 缺失要素检查。

用法: python3 hetong_scan.py 合同.txt -o 风险报告.md
输出: 每类风险命中条款定位 + 建议；缺要素（违约/争议解决/签署栏）提示。
"""
import argparse
import json

from lls_hetong_utils import RISKS, ensure_parent, split_clauses

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("-o", "--output", required=True)
args = ap.parse_args()

text = open(args.input, encoding="utf-8", errors="ignore").read()
clauses = split_clauses(text)

lines = ["> ⚠️ 本报告为关键词级规则扫描，**不构成法律意见**；签署前请咨询执业律师。", "", "# 合同风险扫描报告", ""]
hits_total = 0
hit_categories = 0
for name, keywords, advice in RISKS:
    found = []
    for head, body in clauses:
        for kw in keywords:
            if kw in body:
                snippet = body[max(0, body.find(kw) - 15):body.find(kw) + 40].replace("\n", "")
                found.append((head, snippet))
                break
    if found:
        hits_total += len(found)
        hit_categories += 1
        lines.append(f"## ⚠️ {name}")
        for head, snippet in found[:3]:
            lines.append(f"- 条款 {head}：…{snippet}…")
        lines.append(f"- 💡 建议：{advice}")
        lines.append("")

must_have = {"违约": "违约责任条款", "争议": "争议解决条款"}
for kw, label in must_have.items():
    if kw not in text:
        lines.append(f"## ❌ 缺失要素：{label}")
        lines.append("- 全文未出现相关字样，签署前必须补齐。")
        lines.append("")
# 签字或盖章任一出现即视为有签署/签章栏，仅两者皆无才报缺失。
if "签字" not in text and "盖章" not in text:
    lines.append("## ❌ 缺失要素：签署/签章栏")
    lines.append("- 全文未出现相关字样，签署前必须补齐。")
    lines.append("")

lines.insert(3, f"- 扫描条款 {len(clauses)} 段，命中风险点 {hits_total} 处（{hit_categories} 类）")
ensure_parent(args.output)
open(args.output, "w", encoding="utf-8").write("\n".join(lines))
print(f"[lls-hetong] 扫描完成：{len(clauses)} 段条款，{hits_total} 处风险命中（{hit_categories} 类） → {args.output}")
print("[lls-hetong] 再次强调：规则扫描≠法律意见，签署前请咨询执业律师")
