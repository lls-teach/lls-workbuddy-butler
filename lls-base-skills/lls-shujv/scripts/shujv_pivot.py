#!/usr/bin/env python3
"""数据透视：行=分组列，列=值列的多级聚合（sum/mean/count），写回 Excel 新表。

用法: python3 shujv_pivot.py 数据.csv --group 类别 --value 金额 --agg sum -o 透视.xlsx [--rows 附加行列]
"""
import argparse

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from lls_shujv_utils import die, ensure_parent, guard_overwrite, group_agg, read_table

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("--group", required=True)
ap.add_argument("--value", required=True)
ap.add_argument("--agg", choices=["sum", "mean", "count"], default="sum")
ap.add_argument("-o", "--output", required=True)
ap.add_argument("--force", action="store_true")
args = ap.parse_args()

header, data = read_table(args.input)
gi, vi = header.index(args.group), header.index(args.value)
agg = group_agg(data, gi, vi, args.agg)

wb = Workbook()
ws = wb.active
ws.title = f"{args.group}_{args.agg}"
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
