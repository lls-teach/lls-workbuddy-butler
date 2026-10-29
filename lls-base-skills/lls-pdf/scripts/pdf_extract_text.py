#!/usr/bin/env python3
"""提取 PDF 文本（支持密码、页码范围），输出 UTF-8 文本文件。

用法: python3 pdf_extract_text.py 输入.pdf [-p 1-3,5] [-o out.txt] [--password PW] [--preview N]
"""
import argparse
import sys

from pypdf import PdfReader

from lls_pdf_utils import die, ensure_parent, ensure_utf8_stdio, parse_page_range


def main() -> None:
    ap = argparse.ArgumentParser(description="提取 PDF 文本")
    ap.add_argument("input", help="输入 PDF 路径")
    ap.add_argument("-p", "--pages", help="页码范围，如 1-3,5（缺省=全部）")
    ap.add_argument("-o", "--output", help="输出 txt 路径（缺省=同名 .txt）")
    ap.add_argument("--password", default="", help="打开密码（如有）")
    ap.add_argument("--preview", type=int, default=5, help="stdout 预览前 N 行（默认 5，0=关闭）")
    args = ap.parse_args()

    ensure_utf8_stdio()
    try:
        reader = PdfReader(args.input)
        if reader.is_encrypted:
            if not reader.decrypt(args.password or ""):
                die("PDF 已加密且密码不正确或未提供 --password")
        total = len(reader.pages)
        idx = parse_page_range(args.pages, total)
    except ValueError as e:
        die(str(e))
    except Exception as e:  # noqa: BLE001
        die(f"无法打开 PDF: {e}")

    out_path = args.output or (args.input.rsplit(".", 1)[0] + ".txt")
    ensure_parent(out_path)

    chunks = []
    empty_pages = []
    for i in idx:
        text = (reader.pages[i].extract_text() or "").strip()
        if not text:
            empty_pages.append(i + 1)
        chunks.append(f"===== 第 {i + 1} 页 =====\n{text}")

    full = "\n\n".join(chunks)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full)

    print(f"[lls-pdf] 已提取 {len(idx)}/{total} 页 → {out_path}（{len(full)} 字符）")
    if empty_pages:
        print(f"[lls-pdf] ⚠️ 以下页无文本层（疑似扫描件）: {empty_pages} → 建议走 pdf_render.py + pdf_ocr.py")
    if args.preview > 0:
        lines = [ln for ln in full.splitlines() if ln.strip()][: args.preview]
        print("[lls-pdf] 预览:")
        for ln in lines:
            print("  " + ln[:80])


if __name__ == "__main__":
    main()
