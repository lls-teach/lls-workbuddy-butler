#!/usr/bin/env python3
"""创建中文原生 PDF（reportlab + 中文字体自动回退链）。

用法:
  echo "第一段正文..." | python3 pdf_create.py -o 输出.pdf --title 报告标题 [--subtitle 副标题]
  python3 pdf_create.py -o 输出.pdf --title 标题 --stdin-file body.txt

正文语法（简单标记，逐行解析）:
  # 一级标题    ## 二级标题    - 列表项    > 引用    空行分段    普通行为正文
"""
import argparse
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from lls_pdf_utils import (cjk_font_candidates, die, ensure_parent,
                           ensure_utf8_stdio, guard_overwrite)

_FONT_CACHE: str | None = None


def register_cjk_font() -> str:
    """逐个尝试候选字体注册，全部失败才报错。

    旧逻辑只取第一个存在的文件，Linux 上常先命中 CFF 轮廓的
    NotoSansCJK .ttc，随即被 reportlab 以 "postscript outlines are
    not supported" 拒绝，哪怕后面还有可用的 TrueType 字体也直接失败。
    """
    global _FONT_CACHE
    if _FONT_CACHE:
        return _FONT_CACHE
    candidates = cjk_font_candidates()
    failures: list[str] = []
    for path, idx in candidates:
        try:
            pdfmetrics.registerFont(TTFont("LLSCJK", path, subfontIndex=idx))
        except Exception as e:  # noqa: BLE001
            failures.append(f"{path}（{e}）")
            continue
        _FONT_CACHE = "LLSCJK"
        return _FONT_CACHE
    tried = "；".join(failures) if failures else "未找到任何候选中文字体"
    die("没有可用的中文字体（reportlab 只支持 TrueType 轮廓字体，"
        "CFF 轮廓的 Noto CJK .ttc 会被自动跳过）。已尝试: " + tried +
        "。请安装一款 TrueType 中文字体后重试（Windows 自带微软雅黑即可；"
        "Linux 可装文泉驿或 Noto Sans SC 的 TTF 版），或用环境变量 "
        "LLS_CJK_FONT 指向一个 TrueType 中文字体文件，或改用系统「另存为 PDF」。")


def build_styles(font: str) -> dict[str, ParagraphStyle]:
    base = dict(fontName=font, leading=22)
    return {
        "title": ParagraphStyle("t", fontSize=20, spaceAfter=6 * mm, **base),
        "subtitle": ParagraphStyle("st", fontSize=12, textColor="#555555", spaceAfter=10 * mm, **base),
        "h1": ParagraphStyle("h1", fontSize=15, spaceBefore=6 * mm, spaceAfter=3 * mm, **base),
        "h2": ParagraphStyle("h2", fontSize=13, spaceBefore=4 * mm, spaceAfter=2 * mm, **base),
        "body": ParagraphStyle("b", fontSize=11, firstLineIndent=22, spaceAfter=2 * mm, **base),
        "list": ParagraphStyle("li", fontSize=11, leftIndent=6 * mm, spaceAfter=1.5 * mm, **base),
        "quote": ParagraphStyle("q", fontSize=11, leftIndent=8 * mm, textColor="#444444", spaceAfter=2 * mm, **base),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="创建中文 PDF")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--stdin-file", help="从文件读正文（缺省读 stdin）")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    ensure_utf8_stdio()
    try:
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    if args.stdin_file:
        try:
            with open(args.stdin_file, encoding="utf-8") as f:
                raw = f.read()
        except OSError as e:
            die(f"无法读取正文文件 {args.stdin_file}: {e}")
    else:
        raw = sys.stdin.read()
    if not raw.strip():
        die("正文为空：从 stdin 或 --stdin-file 提供内容")

    font = register_cjk_font()
    styles = build_styles(font)
    out = guard_overwrite(args.output, args.force)
    ensure_parent(out)

    story = []
    if args.title:
        story.append(Paragraph(args.title, styles["title"]))
    if args.subtitle:
        story.append(Paragraph(args.subtitle, styles["subtitle"]))

    def esc(s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    for block in raw.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        for line in block.split("\n"):
            line = line.rstrip()
            if not line:
                continue
            if line.startswith("## "):
                story.append(Paragraph(esc(line[3:]), styles["h2"]))
            elif line.startswith("# "):
                story.append(Paragraph(esc(line[2:]), styles["h1"]))
            elif line.startswith("- "):
                story.append(Paragraph("• " + esc(line[2:]), styles["list"]))
            elif line.startswith("> "):
                story.append(Paragraph(esc(line[2:]), styles["quote"]))
            else:
                story.append(Paragraph(esc(line), styles["body"]))
        story.append(Spacer(1, 2 * mm))

    doc = SimpleDocTemplate(out, pagesize=A4,
                            leftMargin=25 * mm, rightMargin=25 * mm,
                            topMargin=22 * mm, bottomMargin=22 * mm,
                            title=args.title or "LLS PDF")
    doc.build(story)
    print(f"[lls-pdf] 已创建 → {out}（字体: {font}）")


if __name__ == "__main__":
    main()
