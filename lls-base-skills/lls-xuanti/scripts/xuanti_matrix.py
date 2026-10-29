#!/usr/bin/env python3
"""赛道×人群×平台 → 选题矩阵（96 张选题卡）+ 评分卡模板 → Markdown。

用法: python3 xuanti_matrix.py --lane "技能变现" --crowd "平台新手创作者" --platform "抖音+小红书" -o 选题矩阵.md
"""
import argparse

from lls_xuanti_utils import matrix, scorecard_template, ensure_parent

ap = argparse.ArgumentParser()
ap.add_argument("--lane", required=True, help="赛道，如 技能变现")
ap.add_argument("--crowd", required=True, help="目标人群")
ap.add_argument("--platform", required=True, help="投放平台")
ap.add_argument("-o", "--output", required=True)
args = ap.parse_args()
for _name, _value in (("--lane", args.lane), ("--crowd", args.crowd), ("--platform", args.platform)):
    if not _value.strip():
        ap.error(f"{_name} 不能为空或全空白")

cards = matrix(args.lane, args.crowd, args.platform)
lines = [
    f"# 选题矩阵：{args.lane} × {args.crowd} × {args.platform}", "",
    f"- 共 {len(cards)} 张选题卡（角度 6 × 形式 4 × 钩子 4）",
    "- 使用方式：AI 为每张卡起 1 个具体标题 → 用评分卡打分 → ≥10 分的进制作排期。", "",
    "## 选题卡", "",
]
for c in cards:
    lines.append(f"**#{c['id']:02d}** [{c['angle']} × {c['form']} × {c['hook']}]")
    lines.append(f"- 标题待填：围绕「{args.lane}」面向「{args.crowd}」，{c['hook']}开场，{c['form']}呈现")
    lines.append("")
lines += ["## 选题评分卡（复制使用）", "", scorecard_template()]
ensure_parent(args.output)
open(args.output, "w", encoding="utf-8").write("\n".join(lines))
print(f"[lls-xuanti] 选题矩阵 {len(cards)} 卡 → {args.output}")
