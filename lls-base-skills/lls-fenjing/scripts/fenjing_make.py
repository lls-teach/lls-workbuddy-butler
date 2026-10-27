#!/usr/bin/env python3
"""口播稿/要点 → 分镜脚本表（镜头号/景别建议/画面描述位/台词/时长秒）。

用法: python3 fenjing_make.py 口播稿.md -o 分镜表.md [--xlsx 分镜表.xlsx]
景别建议规则：开场=近景（人物出镜建立信任）、数据/要点=特写（强调）、
总结/金句=中景（节奏放缓）、收尾 CTA=近景。
"""
import argparse

from lls_fenjing_utils import die, ensure_parent, split_lines, duration_of

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("-o", "--output", required=True)
ap.add_argument("--xlsx", help="同时输出 Excel 分镜表")
ap.add_argument("--title", default="短视频分镜脚本")
args = ap.parse_args()

lines = split_lines(open(args.input, encoding="utf-8").read())
if not lines:
    die("口播稿为空")

rows, total_sec, t0 = [], 0, 0
for i, line in enumerate(lines):
    dur = duration_of(line)
    shot = "近景" if i == 0 or i == len(lines) - 1 else ("特写" if any(ch.isdigit() for ch in line) else "中景")
    visual = "人物出镜口播" if i == 0 else ("要点/数据画面（贴图或字幕特写）" if any(ch.isdigit() for ch in line) else "口播+B-roll 空镜")
    rows.append([i + 1, t0, dur, shot, visual, line])
    t0 += dur
    total_sec += dur

md = [f"# {args.title}（总时长约 {total_sec} 秒）", "",
      "| 镜头 | 起点(s) | 时长(s) | 景别 | 画面 | 台词 |", "|---|---|---|---|---|---|"]
for r in rows:
    md.append("| " + " | ".join(str(x) for x in r) + " |")
md += ["", "> 景别为建议值，按实际素材调整；台词字数已按 4 字/秒校准时长。"]
ensure_parent(args.output)
open(args.output, "w", encoding="utf-8").write("\n".join(md))

if args.xlsx:
    from openpyxl import Workbook
    from openpyxl.styles import Font
    wb = Workbook()
    ws = wb.active
    ws.title = "分镜脚本"
    ws.append(["镜头", "起点(秒)", "时长(秒)", "景别", "画面", "台词"])
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
    for r in rows:
        ws.append(r)
    ws.column_dimensions["F"].width = 60
    wb.save(args.xlsx)
    print(f"[lls-fenjing] Excel 分镜表 → {args.xlsx}")
print(f"[lls-fenjing] 分镜表 {len(rows)} 镜头 / 总时长 {total_sec} 秒 → {args.output}")
