#!/usr/bin/env python3
"""数据透视：行=分组列，列=值列的多级聚合（sum/mean/count），写回 Excel 新表。

用法: python3 shujv_pivot.py 数据.csv --group 类别 --value 金额 --agg sum -o 透视.xlsx [--rows 附加行列]
"""
import argparse
import re

from lls_shujv_utils import col_index, die, ensure_parent, guard_overwrite, group_agg, read_table

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
except ModuleNotFoundError:
    die("缺少 openpyxl：请先按 SKILL.md 第 0 步安装 scripts/requirements.txt")

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("--group", required=True)
ap.add_argument("--value", required=True)
ap.add_argument("--agg", choices=["sum", "mean", "count"], default="sum")
ap.add_argument("-o", "--output", required=True)
ap.add_argument("--force", action="store_true")
args = ap.parse_args()

header, data = read_table(args.input)
gi, vi = col_index(header, args.group), col_index(header, args.value)
agg = group_agg(data, gi, vi, args.agg)

wb = Workbook()
ws = wb.active
# Excel 工作表名禁 \ / ? * [ ] : 且最长 31 字符：非法字符改 _ 并截断，
# 否则分组列名含斜杠会直接崩溃、超长会产生 Excel 打不开的文件。
ws.title = re.sub(r'[\\/:?*\[\]]', '_', f"{args.group}_{args.agg}")[:31]
ws.append([args.group, f"{args.value}_{args.agg}"])
for c in ws[1]:
    c.font = Font(bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor="1F6FEB")
for k, v in agg:
    ws.append([k, v])
ws.column_dimensions["A"].width = 24
ws.column_dimensions["B"].width = 16

out = guard_overwrite(args.output, args.force)
ensure_parent(out)
wb.save(out)
print(f"[lls-shujv] 透视表 {len(agg)} 行 → {out}")
