#!/usr/bin/env python3
"""PDF 写入后验证（零渲染级）：页数、加密、文本层、表单字段、页面尺寸。

用法: python3 pdf_check.py 输出.pdf [--expect-pages N]
纪律: pdf_create / pdf_fill_form / pdf_merge_split 之后必跑本检查；
      再用 pdf_render.py 渲染受影响页做视觉确认（程序检查通过 ≠ 视觉正确）。
"""
import argparse
import sys

from pypdf import PdfReader

from lls_pdf_utils import die, ensure_utf8_stdio


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--expect-pages", type=int, help="预期页数（不符则警告）")
    args = ap.parse_args()

    ensure_utf8_stdio()
    try:
        reader = PdfReader(args.input)
    except Exception as e:  # noqa: BLE001
        die(f"无法打开（输出文件损坏？）: {e}")

    n = len(reader.pages)
    problems = []

    if args.expect_pages and n != args.expect_pages:
        problems.append(f"页数不符: 实际 {n}，预期 {args.expect_pages}")

    encrypted = reader.is_encrypted
    if encrypted:
        problems.append("文件带加密标记")

    empty_text_pages, sizes = [], set()
    form_fields = 0
    for i, page in enumerate(reader.pages):
        text = (page.extract_text() or "").strip()
        if not text:
            empty_text_pages.append(i + 1)
        sizes.add((round(float(page.mediabox.width)), round(float(page.mediabox.height))))
    try:
        fields = reader.get_fields() or {}
        form_fields = len(fields)
    except Exception:  # noqa: BLE001
        pass

    print(f"[lls-pdf] 检查 {args.input}")
    print(f"[lls-pdf] 页数: {n} | 加密: {'是' if encrypted else '否'} | 表单字段: {form_fields} | 页面尺寸: {sorted(sizes)}")
    if empty_text_pages:
        print(f"[lls-pdf] ℹ️ 无文本层的页（可能是扫描件/纯图页）: {empty_text_pages}")
    if len(sizes) > 1:
        problems.append(f"页面尺寸不一致: {sorted(sizes)}——合并/拆分来源不同文件时常见")
    if n == 0:
        problems.append("0 页空文件")
    if problems:
        print("[lls-pdf] ⚠️ " + "; ".join(problems))
        sys.exit(1)
    print("[lls-pdf] ✅ 结构检查通过。下一步：pdf_render.py 渲染受影响页做视觉确认。")
    sys.exit(0)


if __name__ == "__main__":
    main()
