#!/usr/bin/env python3
"""通用 Markdown → 演示大纲（拆页 + 结构映射 + 页数预算）。

用法: python3 mdppt_convert.py 笔记.md -o 大纲.md [--max-bullets 4]
映射: # 首个=封面 / 其余#=章节分隔页 / ##=内容页标题 / - 要点(≤4/页)
      > =结论带 / ```=代码页(≤14 行/页，超出拆页) / |=表格页(≤8 行/页，超出拆页)
      / 长段落=AI 提炼位（标 🔶）
输出大纲再由 mdppt_render.py 渲染成 PPT 文件，内容页数与本脚本的
页数预算一致（渲染另加封面 1 页）。
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lls_mdppt_utils import die, ensure_parent, iter_pages, parse_md

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("-o", "--output", required=True)
ap.add_argument("--max-bullets", type=int, default=4)
args = ap.parse_args()

md = open(args.input, encoding="utf-8", errors="ignore").read()
data = parse_md(md)
slides = data["slides"]
if not slides:
    die("md 为空或无可用结构")

pages = iter_pages(slides, args.max_bullets)
out = []
page_est = 0
ai_spots = []

for pg in pages:
    kind = pg["kind"]
    if kind == "cover":
        continue  # 封面由渲染步骤生成
    page_est += 1
    if kind == "section":
        out.append(f"# {pg['title']}")
        continue
    if kind == "code":
        out.append(f"## {pg['title']}")
        for ln in pg["lines"]:
            out.append("    " + ln)
        out.append("")
        continue
    if kind == "table":
        out.append(f"## {pg['title']}")
        for r in pg["rows"]:
            out.append("| " + " | ".join(r) + " |")
        out.append("")
        continue
    if kind == "para":
        out.append(f"## {pg['title']}")
        for b in pg["bullets"]:
            out.append(f"- {b}")
        if pg.get("ai_spot"):
            ai_spots.append(pg["para"][:40])
        out.append("")
        continue
    # bullets 页（自动拆页）
    out.append(f"## {pg['title']}")
    for b in pg["bullets"]:
        out.append(f"- {b}")
    if pg.get("takeaway"):
        out.append(f"> {pg['takeaway']}")
    out.append("")

cover_title = next((s["title"] for s in slides if s["kind"] == "cover"), "")
header = (f"<!-- 由 lls-mdppt 转换：{len(slides)} 个结构块 → 约 {page_est} 页 -->\n"
          if True else "")
if ai_spots:
    header += f"<!-- 🔶 AI 提炼位 {len(ai_spots)} 处：长段落需你提炼成要点后再渲染 -->\n"

ensure_parent(args.output)
open(args.output, "w", encoding="utf-8").write(header + "\n".join(out))
print(f"[lls-mdppt] 转换完成 → {args.output}")
print(f"[lls-mdppt] 约 {page_est} 页 ｜ AI 提炼位 {len(ai_spots)} 处 ｜ 封面标题：{cover_title or '（无 # 首行，自行指定）'}")
if ai_spots:
    print("[lls-mdppt] ⚠️ 长段落需你提炼要点后再渲染（大纲中已标 🔶）")
