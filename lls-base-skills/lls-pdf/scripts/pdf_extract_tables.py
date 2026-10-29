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

from lls_pdf_utils import die, ensure_parent, ensure_utf8_stdio, parse_page_range

# pdfplumber 的合法策略名是 lines/text（另有 lines_strict/explicit），
# 不是 lattice/stream；CLI 保留 lattice/stream 叫法，这里做映射。
# lattice（有框线表格）→ lines；stream（无边框、按文本对齐）→ text。
STRATEGY_MAP = {"lattice": "lines", "stream": "text"}


def main() -> None:
    ap = argparse.ArgumentParser(description="提取 PDF 表格为 CSV")
    ap.add_argument("input")
    ap.add_argument("-o", "--output-dir", required=True)
    ap.add_argument("-p", "--pages")
    ap.add_argument("--mode", choices=["auto", "lattice", "stream"], default="auto",
                    help="lattice=有框线表格 stream=无边框（缺省 auto 先 lattice 后 stream）")
    args = ap.parse_args()

    ensure_utf8_stdio()
    ensure_parent(os.path.join(args.output_dir, "_"))
    modes = ["lattice", "stream"] if args.mode == "auto" else [args.mode]

    try:
        pdf = pdfplumber.open(args.input)
    except Exception as e:  # noqa: BLE001
        die(f"无法打开 PDF: {e}")
    try:
        total = len(pdf.pages)
        idx = parse_page_range(args.pages, total)
    except ValueError as e:
        die(str(e))

    saved = 0
    for i in idx:
        page = pdf.pages[i]
        tables = []
        for mode in modes:
            strategy = STRATEGY_MAP[mode]
            try:
                tables = page.extract_tables({"vertical_strategy": strategy,
                                              "horizontal_strategy": strategy})
            except Exception as e:  # noqa: BLE001
                die(f"第 {i + 1} 页表格提取失败（模式 {mode}）: {e}")
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
