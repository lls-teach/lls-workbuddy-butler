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

from lls_pdf_utils import die, ensure_parent, find_cjk_fonts, guard_overwrite

_FONT_CACHE: str | None = None


def register_cjk_font() -> str | None:
    """逐个尝试回退链，返回首个 reportlab 能注册的字体；全部失败返回 None。

    旧逻辑只试第一个候选、失败即退出：在只有 CFF 轮廓 Noto CJK 的
    Linux 系统上，第一个候选注册失败就全盘报错，尽管后面并无可用项；
    更重要的是，调用方拿到 None 后可走 PyMuPDF 回退路径（见下），
    而不是直接宣判中文 PDF 做不出来。
    """
    global _FONT_CACHE
    if _FONT_CACHE:
        return _FONT_CACHE
    errors: list[str] = []
    for path, idx in find_cjk_fonts():
        try:
            pdfmetrics.registerFont(TTFont("LLSCJK", path, subfontIndex=idx))
        except Exception as e:  # noqa: BLE001
            errors.append(f"{path}: {e}")
            continue
        _FONT_CACHE = "LLSCJK"
        return _FONT_CACHE
    if errors:
        print(f"[lls-pdf] reportlab 无法注册回退链字体，走 PyMuPDF 回退路径（{'; '.join(errors)}）",
              file=sys.stderr)
    return None


def build_with_pymupdf(out: str, title: str, subtitle: str, raw: str) -> str:
    """PyMuPDF 回退路径：reportlab 注册不到 TrueType 轮廓中文字体时用。

    原理：PyMuPDF 能直接使用 CFF 轮廓的 TTC 字体；先用 fontTools 把
    字体按实际用字子集化（只留用到的字形），再嵌入，避免整套 CJK
    字体（十几 MB）原样塞进 PDF。子集文件只写临时目录，用完删除。
    返回所用字体路径（用于输出提示）。
    """
    import tempfile

    import fitz
    from fontTools import subset
    from fontTools.ttLib import TTCollection

    fonts = find_cjk_fonts()
    if not fonts:
        die("未找到任何中文字体（回退链: PingFang/Songti/微软雅黑/Noto CJK/文泉驿）。"
            "请安装一款中文字体后重试，或改用系统「另存为 PDF」。")

    # 收集全部待排版文字，用于子集化
    lines: list[tuple[str, float, bool]] = []  # (文本, 字号, 是否加粗近似)
    if title:
        lines.append((title, 20, True))
    if subtitle:
        lines.append((subtitle, 12, False))
    for block in raw.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        for line in block.split("\n"):
            line = line.rstrip()
            if not line:
                continue
            if line.startswith("## "):
                lines.append((line[3:], 13, True))
            elif line.startswith("# "):
                lines.append((line[2:], 15, True))
            elif line.startswith("- "):
                lines.append(("• " + line[2:], 11, False))
            elif line.startswith("> "):
                lines.append((line[2:], 11, False))
            else:
                lines.append((line, 11, False))

    font_path, _idx = fonts[0]
    subset_path = None
    try:
        with tempfile.TemporaryDirectory(prefix="lls_pdf_font_") as tmpdir:
            subset_path = tmpdir + "/subset.otf"
            coll = TTCollection(font_path)
            font = coll.fonts[0]
            opts = subset.Options()
            sub = subset.Subsetter(options=opts)
            sub.populate(text="".join(t for t, _s, _b in lines))
            sub.subset(font)
            font.save(subset_path)

            doc = fitz.open()
            page = doc.new_page(width=595, height=842)  # A4 pt
            page.insert_font(fontfile=subset_path, fontname="cjk")
            x, y = 70, 70
            max_w = 595 - 140
            for text, size, _bold in lines:
                if y > 842 - 70:
                    page = doc.new_page(width=595, height=842)
                    page.insert_font(fontfile=subset_path, fontname="cjk")
                    y = 70
                # 按行宽简单折行：按字符数估算（中文按字号计宽，近似即可）
                chars_per_line = max(10, int(max_w / (size * 0.95)))
                rest = text
                first = True
                while rest:
                    chunk, rest = rest[:chars_per_line], rest[chars_per_line:]
                    page.insert_text((x, y), chunk, fontname="cjk", fontsize=size)
                    y += size * 1.7
                    first = False
                if first:
                    y += size * 1.7
                y += 4
            doc.save(out, garbage=4, deflate=True)
    except Exception as e:  # noqa: BLE001
        die(f"PyMuPDF 回退路径失败 {font_path}: {e}")
    return font_path + "（PyMuPDF 回退）"


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

    raw = open(args.stdin_file, encoding="utf-8").read() if args.stdin_file else sys.stdin.read()
    if not raw.strip():
        die("正文为空：从 stdin 或 --stdin-file 提供内容")

    font = register_cjk_font()
    out = guard_overwrite(args.output, args.force)
    ensure_parent(out)
    if font is None:
        used = build_with_pymupdf(out, args.title, args.subtitle, raw)
        print(f"[lls-pdf] 已创建 → {out}（字体: {used}）")
        return
    styles = build_styles(font)

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
