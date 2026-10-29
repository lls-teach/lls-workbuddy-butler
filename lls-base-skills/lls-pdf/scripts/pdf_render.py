#!/usr/bin/env python3
"""把 PDF 渲染成 PNG 图片（pypdfium2，BSD 许可的 PDFium 绑定，中文渲染友好）。

用法: python3 pdf_render.py 输入.pdf -o 输出目录/ [--dpi 200] [-p 1-3]
输出: <输出目录>/page_001.png ...
"""
import argparse
import os

import pypdfium2 as pdfium

from lls_pdf_utils import die, ensure_parent, ensure_utf8_stdio, parse_page_range


def main() -> None:
    ap = argparse.ArgumentParser(description="PDF 渲染为 PNG")
    ap.add_argument("input")
    ap.add_argument("-o", "--output-dir", required=True)
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("-p", "--pages")
    ap.add_argument("--password", default="")
    args = ap.parse_args()

    ensure_utf8_stdio()
    ensure_parent(os.path.join(args.output_dir, "_"))
    try:
        pdf = pdfium.PdfDocument(args.input, password=args.password or None)
    except Exception as e:  # noqa: BLE001
        die(f"无法打开 PDF: {e}")
    try:
        total = len(pdf)
        idx = parse_page_range(args.pages, total)
    except ValueError as e:
        die(str(e))
    scale = args.dpi / 72.0

    for i in idx:
        page = pdf[i]
        bitmap = page.render(scale=scale)
        img = bitmap.to_pil()
        out = os.path.join(args.output_dir, f"page_{i + 1:03d}.png")
        img.save(out)
        print(f"[lls-pdf] → {out}（{img.width}x{img.height}）")
        page.close()

    print(f"[lls-pdf] 共渲染 {len(idx)}/{total} 页 → {os.path.abspath(args.output_dir)}")
    pdf.close()


if __name__ == "__main__":
    main()
