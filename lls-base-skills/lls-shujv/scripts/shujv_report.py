#!/usr/bin/env python3
"""表数据 → Markdown 分析报告（概览/数值列统计/分组聚合/异常值/IQR）。

用法: python3 shujv_report.py 数据.csv|xlsx [-o 报告.md] [--group 类别列] [--value 金额列] [--agg sum|mean|count]
"""
import argparse
from lls_shujv_utils import die, ensure_parent, group_agg, numeric_cols, read_table, describe

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("-o", "--output", default="")
ap.add_argument("--group", help="分组列（生成聚合表）")
ap.add_argument("--value", help="聚合值列（数值）")
ap.add_argument("--agg", choices=["sum", "mean", "count"], default="sum")
args = ap.parse_args()

header, data = read_table(args.input)
ncols = numeric_cols(header, data)
lines = [f"# 数据分析报告：{args.input}", "",
         f"- 规模：{len(data)} 行 × {len(header)} 列", ""]
lines += ["## 一、数值列概览", "", "| 列 | 数量 | 合计 | 均值 | 最小 | 最大 | 异常值(IQR) |", "|---|---|---|---|---|---|---|"]
for i in ncols:
    vals = [r[i] for r in data if isinstance(r[i], (int, float))]
    d = describe(vals)
    lines.append(f"| {header[i]} | {d['count']} | {d['sum']:,} | {d['mean']:,} | {d['min']:,} | {d['max']:,} | {d['outlier_n']} |")

if args.group and args.value:
    gi, vi = header.index(args.group), header.index(args.value)
    agg = group_agg(data, gi, vi, args.agg)
    lines += ["", f"## 二、按 {args.group} 的 {args.agg}（Top 10）", "", f"| {args.group} | {args.agg} |", "|---|---|"]
    for k, v in agg[:10]:
        lines.append(f"| {k} | {v:,} |")
    if len(agg) > 1:
        head_share = agg[0][1] / sum(v for _, v in agg) * 100 if sum(v for _, v in agg) else 0
        lines += ["", f"> 集中度：第 1 名占 {head_share:.0f}%。"]

if args.output:
    ensure_parent(args.output)
    open(args.output, "w", encoding="utf-8").write("\n".join(lines))
    print(f"[lls-shujv] 报告 → {args.output}")
else:
    print("\n".join(lines))
