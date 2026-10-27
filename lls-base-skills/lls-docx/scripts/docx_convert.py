#!/usr/bin/env python3
"""docx 输出验证与格式转换（LibreOffice headless）。

用法:
  验证输出（转 PDF 供人工/视觉检查）: python3 docx_convert.py 输出.docx --to pdf
  旧格式迁移:                          python3 docx_convert.py 老文档.doc --to docx
输出: 同名 .pdf / .docx（同目录）。转完 PDF 后可渲染逐页查看。
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys

from lls_docx_utils import die


def soffice_or_die() -> str:
    path = shutil.which("soffice") or shutil.which("libreoffice")
    if path:
        return path
    for extra in ["/Applications/LibreOffice.app/Contents/MacOS/soffice",
                  "C:/Program Files/LibreOffice/program/soffice.exe"]:
        if os.path.exists(extra):
            return extra
    die("未找到 LibreOffice（soffice）。安装指引:\n"
        "  macOS: brew install --cask libreoffice\n"
        "  Windows/Linux: https://www.libreoffice.org/download")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--to", choices=["pdf", "docx"], required=True)
    ap.add_argument("--timeout", type=int, default=90)
    args = ap.parse_args()

    if not os.path.exists(args.input):
        die(f"文件不存在: {args.input}")
    if args.to == "docx" and args.input.lower().endswith(".docx"):
        die("输入已是 .docx，无需转换（验证输出请 --to pdf）")

    outdir = os.path.dirname(os.path.abspath(args.input))
    r = subprocess.run([soffice_or_die(), "--headless", "--convert-to", args.to,
                        "--outdir", outdir, args.input],
                       capture_output=True, text=True, timeout=args.timeout)
    stem = os.path.splitext(os.path.basename(args.input))[0]
    out = os.path.join(outdir, f"{stem}.{args.to}")
    produced = out if os.path.exists(out) else (glob.glob(os.path.join(outdir, f"{stem}*.pdf")) or [None])[0]
    if not produced:
        die(f"转换失败: {r.stderr[:300]}")
    print(f"[lls-docx] 已转换 → {produced}")
    if args.to == "pdf":
        print("[lls-docx] 写入后验证纪律：渲染成图，逐页核对标题/表格/页眉是否如预期。")
    if args.to == "docx":
        print("[lls-docx] 旧格式已迁移为 .docx，后续用 docx_read/docx_edit 处理。")


if __name__ == "__main__":
    main()
