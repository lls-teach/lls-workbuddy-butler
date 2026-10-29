#!/usr/bin/env python3
"""按默认规范重设论文样式（只动格式不动内容）。OMML 公式对象自动跳过。

用法: python3 lunwen_format.py 输入.docx -o 输出.docx
标题识别：段落样式名含 Heading/标题，或文本匹配 ^[0-9]+(.[0-9]+)*[ ] 章节号模式。
"""
import argparse
import re
from typing import Optional

from lls_lunwen_utils import die, ensure_parent, guard_overwrite, set_body_font, set_cn_font

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Cm, Pt
except ImportError:
    die("缺少 python-docx，请先安装依赖：pip install -r scripts/requirements.txt")

STYLE = {
    "body_font": "宋体", "body_size": 12, "body_line": 1.5, "body_indent_chars": 2,
    "h1": ("黑体", 16), "h2": ("黑体", 14), "h3": ("黑体", 12),
}
H_PAT = re.compile(r"^(?:(\d+)\.|(\d+\.\d+)\.|(\d+\.\d+\.\d+)\s)")

def level_of(text: str, style_name: str) -> Optional[int]:
    # 标题层级：先长模式后短模式（1.1.1 优先于 1.1 优先于 1.）。
    # 样式名同时认英文 Heading 与中文 Word 的“标题”（中文版 Word 样式名即“标题 1/2/3”）。
    if "Heading 3" in style_name or "标题 3" in style_name or re.match(r"^\d+\.\d+\.\d+[\s　]", text):
        return 3
    if "Heading 2" in style_name or "标题 2" in style_name or re.match(r"^\d+\.\d+[\s　][^\d.]", text):
        return 2
    if "Heading 1" in style_name or "标题 1" in style_name or re.match(r"^\d+[\.、]?\s*[\u4e00-\u9fffA-Za-z]", text):
        return 1
    return None

CAPTION_PAT = re.compile(r"^(图|表)\s*(\d+)-(\d+)[\s　]")
SENTENCE_END = ("。", "；", "？", "！")

def is_caption(text: str) -> bool:
    """题注段：以“图/表 章-序号”开头且不是完整句子（带句末标点的是正文引用句，不是题注）。"""
    return bool(CAPTION_PAT.match(text)) and not any(p in text for p in SENTENCE_END)

REF_PAT = re.compile(r"^\[\d+\]")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    try:
        doc = Document(args.input)
    except Exception as e:
        die(f"无法打开（.doc 旧格式请先另存为 .docx）: {e}")

    for sec in doc.sections:
        sec.top_margin = sec.bottom_margin = Cm(2.54)
        sec.left_margin = sec.right_margin = Cm(3.17)

    stats = {"h1": 0, "h2": 0, "h3": 0, "body": 0}
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        lvl = level_of(text, para.style.name if para.style else "")
        if lvl:
            font, size = STYLE[f"h{lvl}"]
            for run in para.runs:
                set_cn_font(run, font)
                run.font.size = Pt(size)
                run.font.bold = True
            para.paragraph_format.space_before = Pt(12 if lvl == 1 else 6)
            para.paragraph_format.space_after = Pt(6)
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            stats[f"h{lvl}"] += 1
        elif is_caption(text):
            # 图表题注：宋体五号（10.5pt）居中，不首行缩进
            for run in para.runs:
                set_cn_font(run, STYLE["body_font"])
                run.font.size = Pt(10.5)
            pf = para.paragraph_format
            pf.line_spacing = STYLE["body_line"]
            pf.first_line_indent = Pt(0)
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            stats["body"] += 1
        elif REF_PAT.match(text):
            # 参考文献：宋体五号，悬挂缩进（左缩进 2 字符、首行反向 2 字符）
            for run in para.runs:
                set_cn_font(run, STYLE["body_font"])
                run.font.size = Pt(10.5)
            pf = para.paragraph_format
            pf.line_spacing = STYLE["body_line"]
            pf.left_indent = Pt(10.5 * 2)
            pf.first_line_indent = Pt(-10.5 * 2)
            stats["body"] += 1
        else:
            for run in para.runs:
                set_body_font(run, STYLE["body_font"])
                run.font.size = Pt(STYLE["body_size"])
            pf = para.paragraph_format
            pf.line_spacing = STYLE["body_line"]
            pf.first_line_indent = Pt(STYLE["body_size"] * STYLE["body_indent_chars"])
            stats["body"] += 1

    out = guard_overwrite(args.output, args.force)
    ensure_parent(out)
    doc.save(out)
    print(f"[lls-lunwen] 格式重设完成 → {out}")
    print(f"[lls-lunwen] 一级标题 {stats['h1']} | 二级 {stats['h2']} | 三级 {stats['h3']} | 正文段 {stats['body']}")

main()
