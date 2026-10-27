#!/usr/bin/env python3
"""已备资料 × 清单对照 → 缺项报告。

用法: python3 baoshui_check.py --type "小规模纳税人·查账征收" --have 已备清单.txt -o 缺项报告.md
已备清单格式：每行一项（写关键词即可，如"对账单""发票汇总"）。
"""
import argparse

from lls_baoshui_utils import CHECKLISTS, DISCLAIMER, die, ensure_parent

ap = argparse.ArgumentParser()
ap.add_argument("--type", required=True)
ap.add_argument("--have", required=True)
ap.add_argument("-o", "--output", required=True)
args = ap.parse_args()

if args.type not in CHECKLISTS:
    die(f"类型必须是: {' / '.join(CHECKLISTS)}")
data = CHECKLISTS[args.type]
freq = "按月" if args.type == "一般纳税人" else "按季"
items = data["按季资料" if freq == "按季" else "按月资料"]
have = open(args.have, encoding="utf-8", errors="ignore").read()

lines = [f"# 报税资料缺项报告（{args.type}）", ""]
missing = []
for item in items:
    kws = [w for w in ["发票", "对账单", "台账", "流水", "凭证", "工资", "社保", "盘点", "回执", "申报"] if w in item]
    if any(k in have for k in kws) or item[:8] in have:
        lines.append(f"- ✅ {item}")
    else:
        lines.append(f"- ❌ 缺：{item}")
        missing.append(item)
lines += ["", DISCLAIMER]
ensure_parent(args.output)
open(args.output, "w", encoding="utf-8").write("\n".join(lines))
print(f"[lls-baoshui] 缺项报告 → {args.output}（缺 {len(missing)}/{len(items)}）")
