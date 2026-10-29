#!/usr/bin/env python3
"""把 Markdown 源文档渲染成 .pptx（基础渲染）。

用法: python3 mdppt_render.py 笔记.md -o 演示.pptx [--title 封面标题]
依赖: python-pptx（见 scripts/requirements.txt，纯 Python，Windows 可用官方 wheel）。

与 mdppt_convert.py 共用 lls_mdppt_utils.iter_pages 的分页逻辑，
因此 .pptx 的内容页数 = 转换大纲的页数预算，另加封面 1 页。
页型：封面 / 章节分隔页 / 要点页 / 代码页（等宽字体）/ 表格页 / 段落页。
长段落仍按大纲渲染为 🔶 提炼位页：提炼结果须先写回源文档对应位置
再渲染，本脚本不解析人工改动后的大纲文件。
字体只用 Windows 原生字体名（微软雅黑 / Consolas），生成时不依赖
本机是否装有该字体，文件在 PowerPoint 中打开即按此字体显示。
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lls_mdppt_utils import die, ensure_parent, iter_pages, parse_md

TITLE_FONT = "微软雅黑"
BODY_FONT = "微软雅黑"
CODE_FONT = "Consolas"


def main():
    try:
        from pptx import Presentation
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN
        from pptx.util import Inches, Pt
    except ImportError:
        die("未装 python-pptx，请先在虚拟环境内执行：pip install -r scripts/requirements.txt")

    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--title", default="", help="封面标题（默认取文档第一个 # 标题，无则用“演示”）")
    ap.add_argument("--max-bullets", type=int, default=4)
    args = ap.parse_args()

    md = open(args.input, encoding="utf-8", errors="ignore").read()
    slides = parse_md(md)["slides"]
    if not slides:
        die("md 为空或无可用结构")

    pages = iter_pages(slides, args.max_bullets)
    cover_title = args.title or next((s["title"] for s in slides if s["kind"] == "cover"), "") or "演示"
    content_pages = [p for p in pages if p["kind"] != "cover"]
    total = len(content_pages) + 1  # 内容页 + 封面 1 页

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    def add_text(slide, left, top, width, height, size=20, bold=False, align=None):
        box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
        tf = box.text_frame
        tf.word_wrap = True
        return box, tf

    def set_para(para, text, size=20, bold=False, font=BODY_FONT, color=None, align=None):
        para.text = ""
        run = para.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.name = font
        if color is not None:
            run.font.color.rgb = color
        if align is not None:
            para.alignment = align
        return para

    def add_title(slide, text, size=32):
        _, tf = add_text(slide, 0.6, 0.4, 12.1, 1.0, size=size, bold=True)
        set_para(tf.paragraphs[0], text, size=size, bold=True, font=TITLE_FONT)

    def add_footer(slide, index):
        _, tf = add_text(slide, 12.2, 7.05, 0.7, 0.3)
        set_para(tf.paragraphs[0], f"{index}/{total}", size=11,
                 color=RGBColor(0x80, 0x80, 0x80), align=PP_ALIGN.RIGHT)

    # 封面
    slide = prs.slides.add_slide(blank)
    _, tf = add_text(slide, 1.0, 2.8, 11.3, 1.2)
    set_para(tf.paragraphs[0], cover_title, size=40, bold=True, font=TITLE_FONT, align=PP_ALIGN.CENTER)
    add_footer(slide, 1)

    index = 1
    for pg in content_pages:
        index += 1
        kind = pg["kind"]
        slide = prs.slides.add_slide(blank)
        if kind == "section":
            _, tf = add_text(slide, 1.0, 3.0, 11.3, 1.2)
            set_para(tf.paragraphs[0], pg["title"], size=36, bold=True,
                     font=TITLE_FONT, align=PP_ALIGN.CENTER)
            add_footer(slide, index)
            continue
        add_title(slide, pg["title"])
        if kind == "bullets":
            _, tf = add_text(slide, 0.8, 1.6, 11.7, 5.0)
            first = True
            for b in pg["bullets"]:
                para = tf.paragraphs[0] if first else tf.add_paragraph()
                first = False
                set_para(para, f"•  {b}", size=22)
            if pg.get("takeaway"):
                para = tf.add_paragraph()
                set_para(para, f"结论：{pg['takeaway']}", size=22, bold=True,
                         color=RGBColor(0x1F, 0x4E, 0x79))
        elif kind == "code":
            _, tf = add_text(slide, 0.8, 1.6, 11.7, 5.0)
            first = True
            for ln in pg["lines"]:
                para = tf.paragraphs[0] if first else tf.add_paragraph()
                first = False
                set_para(para, ln, size=14, font=CODE_FONT)
            if not pg["lines"]:
                set_para(tf.paragraphs[0], "", size=14, font=CODE_FONT)
        elif kind == "table":
            rows = pg["rows"]
            cols = len(rows[0]) if rows else 0
            if cols:
                shape = slide.shapes.add_table(len(rows), cols,
                                               Inches(0.6), Inches(1.6),
                                               Inches(12.1), Inches(5.0))
                table = shape.table
                for ci in range(cols):
                    table.columns[ci].width = Inches(12.1 / cols)
                for ri, row in enumerate(rows):
                    for ci, cell_text in enumerate(row):
                        cell = table.cell(ri, ci)
                        cell.text = ""
                        para = cell.text_frame.paragraphs[0]
                        is_header = (ri == 0 and pg.get("chunk_index", 0) == 0)
                        set_para(para, cell_text, size=16, bold=is_header)
                        if is_header:
                            cell.fill.solid()
                            cell.fill.fore_color.rgb = RGBColor(0xD9, 0xE2, 0xF3)
        elif kind == "para":
            _, tf = add_text(slide, 0.8, 1.6, 11.7, 5.0)
            if pg["bullets"]:
                first = True
                for b in pg["bullets"]:
                    para = tf.paragraphs[0] if first else tf.add_paragraph()
                    first = False
                    set_para(para, f"•  {b}", size=22)
            elif pg.get("para"):
                set_para(tf.paragraphs[0], pg["para"], size=22)
        add_footer(slide, index)

    output = args.output
    if not output.lower().endswith(".pptx"):
        output += ".pptx"
    ensure_parent(output)
    prs.save(output)
    print(f"[lls-mdppt] 渲染完成 → {output}")
    print(f"[lls-mdppt] 共 {total} 页（封面 1 + 内容 {len(content_pages)} 页）｜ 封面标题：{cover_title}")


if __name__ == "__main__":
    main()
