#!/usr/bin/env python3
"""通用 Markdown → lls-pptx 大纲（拆页 + 结构映射 + 页数预算）。

用法: python3 mdppt_convert.py 笔记.md -o 大纲.md [--max-bullets 4]
映射: # 首个=封面 / 其余#=章节分隔页 / ##=内容页标题 / - 要点(≤4/页)
      > =结论带 / ```=代码页 / |=表格页 / 长段落=AI 提炼位（标 🔶）
输出可直接喂给底座 lls-pptx 的 pptx_create.py。
"""
import argparse

from lls_mdppt_utils import die, ensure_parent, parse_md

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

out = []
page_est = 0
ai_spots = []

for sl in slides:
    kind = sl["kind"]
    if kind == "cover":
        continue  # 封面由 lls-pptx --title 生成
    if kind == "section":
        out.append(f"# {sl['title']}")
        page_est += 1
        continue
    if kind == "code":
        out.append(f"## {sl['title'] or '代码'}")
        lang, code = sl.get("code") or ("", "")
        for ln in code.split("\n")[:14]:
            out.append("    " + ln)
        out.append("")
        page_est += 1
        continue
    if kind == "table":
        rows = sl["table"]
        out.append(f"## {sl['title'] or '表格'}")
        for r in rows[:8]:
            out.append("| " + " | ".join(r) + " |")
        out.append("")
        page_est += 1
        continue
    if kind == "para":
        text = sl.get("para", "")
        if len(text) > 80:
            out.append(f"## 🔶 提炼：{text[:40]}…")
            out.append(f"- （AI 提炼位）将以下段落提炼为 ≤{args.max_bullets} 条要点：")
            out.append(f"- 原文：{text[:200]}")
            ai_spots.append(text[:40])
        else:
            out.append(f"## {text[:40]}")
        out.append("")
        page_est += 1
        continue

    # bullets 页（自动拆页）
    title = sl.get("title", "")
    bullets = sl.get("bullets", [])
    take = sl.get("takeaway")
    chunks = [bullets[i:i + args.max_bullets] for i in range(0, len(bullets), args.max_bullets)] or [[]]
    for ci, chunk in enumerate(chunks):
        suffix = f"（{ci+1}/{len(chunks)}）" if len(chunks) > 1 else ""
        out.append(f"## {title}{suffix}")
        for b in chunk:
            out.append(f"- {b}")
        if take and ci == len(chunks) - 1:
            out.append(f"> {take}")
        out.append("")
        page_est += 1

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
