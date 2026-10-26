#!/usr/bin/env python3
"""按 GB/T 9704 版式创建公文 docx。

用法: python3 gongwen_create.py -o 文件.docx --json 要素.json
要素 JSON: title/doc_number/main_to/body[list]/attachment_note/issuer/date
版式: 页边距 上3.7 下3.5 左2.8 右2.6；标题二号宋体加粗居中；正文三号仿宋；
      一级标题黑体、二级楷体；成文日期右空四字（近似右对齐）。
"""
import argparse
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

from lls_gongwen_utils import CN_FS, CN_HEI, CN_KAI, ensure_parent, guard_overwrite, set_cn_font
from docx.shared import Pt as _Pt

def para(doc, text, size=16, font=CN_FS, bold=False, align=None, line=28, space_after=0, indent=False):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    set_cn_font(run, font)
    pf = p.paragraph_format
    pf.line_spacing = _Pt(line)  # GB/T 9704：固定 28 磅行距
    pf.space_after = Pt(space_after)
    if indent:
        pf.first_line_indent = Pt(size * 2)
    if align is not None:
        p.alignment = align
    return p

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    import json
    e = json.load(open(args.json, encoding="utf-8"))
    for k in ("title", "main_to", "body", "issuer", "date"):
        if not e.get(k):
            from lls_gongwen_utils import die
            die(f"要素缺失: {k}（{e.get('title', '')}）")

    doc = Document()
    for sec in doc.sections:
        sec.top_margin, sec.bottom_margin = Cm(3.7), Cm(3.5)
        sec.left_margin, sec.right_margin = Cm(2.8), Cm(2.6)

    # 标题（二号 = 22pt，宋体加粗居中替代小标宋）
    para(doc, e["title"], size=22, font="宋体", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, line=36, space_after=10)
    # 发文字号（居中，紧跟标题）
    if e.get("doc_number"):
        para(doc, e["doc_number"], size=16, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)
    # 主送（顶格）
    para(doc, e["main_to"], size=16, space_after=0)
    # 正文：一级标题（一、）黑体；二级（（一））楷体；其余仿宋；全部首行缩进两字
    for block in e["body"]:
        for line in block.split("\n"):
            line = line.strip()
            if not line:
                continue
            if re.match(r"^[一二三四五六七八九十]+、", line):
                para(doc, line, size=16, font=CN_HEI, bold=True, line=28, indent=True)
            elif re.match(r"^[（(][一二三四五六七八九十]+[)）]", line):
                para(doc, line, size=16, font=CN_KAI, line=28, indent=True)
            else:
                para(doc, line, size=16, line=28, indent=True)
    if e.get("attachment_note"):
        para(doc, e["attachment_note"], size=16, space_after=0)
    # 成文日期+落款（右对齐近似右空四字：右对齐后加右侧缩进）
    from docx.shared import Cm as _Cm
    p = para(doc, e["issuer"], size=16, align=WD_ALIGN_PARAGRAPH.RIGHT, line=28)
    p.paragraph_format.right_indent = _Cm(1.4)
    p = para(doc, e["date"].replace("-", " 年 ", 1).replace("-", " 月 ", 1) + " 日"
             if "-" in e["date"] else e["date"], size=16, align=WD_ALIGN_PARAGRAPH.RIGHT, line=28)
    p.paragraph_format.right_indent = _Cm(1.4)

    out = guard_overwrite(args.output, args.force)
    ensure_parent(out)
    doc.save(out)
    print(f"[lls-gongwen] 公文已生成 → {out}（GB/T 9704 常用版式；单位自有版式以其为准）")

main()
