#!/usr/bin/env python3
"""提取 PDF 中的表格为 CSV（pdfplumber，支持 lattice/stream 两种模式）。

用法: python3 pdf_extract_tables.py 输入.pdf -o 输出目录/ [-p 1-3] [--mode auto|lattice|stream]
每页每张表输出: <输出目录>/p{页码}_t{表序}.csv
"""
import argparse
import csv
import glob
import os

import pdfplumber

from lls_pdf_utils import die, ensure_parent, parse_page_range


def main() -> None:
    ap = argparse.ArgumentParser(description="提取 PDF 表格为 CSV")
    ap.add_argument("input")
    ap.add_argument("-o", "--output-dir", required=True)
    ap.add_argument("-p", "--pages")
    ap.add_argument("--mode", choices=["auto", "lattice", "stream"], default="auto",
                    help="lattice=有框线表格 stream=无边框（缺省 auto 先 lattice 后 stream）")
    args = ap.parse_args()

    ensure_parent(os.path.join(args.output_dir, "_"))
    modes = ["lattice", "stream"] if args.mode == "auto" else [args.mode]

    try:
        pdf = pdfplumber.open(args.input)
    except Exception as e:  # noqa: BLE001
        die(f"无法打开 PDF: {e}")
    total = len(pdf.pages)
    idx = parse_page_range(args.pages, total)

    saved = 0
    for i in idx:
        page = pdf.pages[i]
        tables = []
        for mode in modes:
            tables = page.extract_tables({"vertical_strategy": mode, "horizontal_strategy": mode})
            if tables:
                break
        for t_no, table in enumerate(tables, 1):
            out = os.path.join(args.output_dir, f"p{i + 1}_t{t_no}.csv")
            with open(out, "w", newline="", encoding="utf-8-sig") as f:
                csv.writer(f).writerows([("" if c is None else str(c).strip()) for c in row] for row in table)
            saved += 1

    print(f"[lls-pdf] 共 {len(idx)} 页，提取出 {saved} 张表 → {os.path.abspath(args.output_dir)}/p*_t*.csv")
    if saved == 0:
        print("[lls-pdf] ⚠️ 未识别到表格。若为扫描件请走 OCR 路线；若为不规则排版请人工核对。")
    pdf.close()


if __name__ == "__main__":
    main()
