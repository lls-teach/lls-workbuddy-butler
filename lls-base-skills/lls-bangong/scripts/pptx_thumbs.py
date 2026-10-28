#!/usr/bin/env python3
"""渲染缩略图总览网格（每张 12 页一版，带页码标签）。用于选模板版式与视觉总检。

用法: python3 pptx_thumbs.py 输入.pptx [前缀]
依赖: LibreOffice（soffice，转 PDF 用）+ pypdfium2（渲染）。缺失时给出安装指引。
输出: <前缀>-1.jpg（超过 12 页续 -2、-3 …）
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile

from lls_pptx_utils import die

GRID_COLS, GRID_ROWS = 4, 3
CELL_W = 640


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
        "  Windows/Linux: https://www.libreoffice.org/download\n"
        "安装后重试。若只需内容检查，用 pptx_check.py（零渲染）代替。")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("prefix", nargs="?", default="thumbnails")
    args = ap.parse_args()

    soffice = soffice_or_die()
    try:
        import pypdfium2 as pdfium
    except ImportError:
        die("缺 pypdfium2: pip install pypdfium2")

    tmp = tempfile.mkdtemp(prefix="lls_pptx_thumbs_")
    print(f"[lls-pptx] LibreOffice 转换中（大文件可能较慢）…", file=sys.stderr)
    r = subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", tmp, args.input],
                       capture_output=True, text=True, timeout=180)
    pdfs = glob.glob(os.path.join(tmp, "*.pdf"))
    if not pdfs:
        die(f"soffice 转换失败: {r.stderr[:300]}")
    try:
        pdf = pdfium.PdfDocument(pdfs[0])
    except Exception as e:  # noqa: BLE001
        die(f"渲染失败: {e}")

    from PIL import Image  # pypdfium2 渲染依赖 Pillow
    total = len(pdf)
    pages = []
    for i in range(total):
        img = pdf[i].render(scale=CELL_W / 675.0).to_pil()  # 13.333in * 72dpi ≈ 960px 基准
        pages.append(img)

    import math
    sheets = math.ceil(total / (GRID_COLS * GRID_ROWS))
    outs = []
    for s in range(sheets):
        chunk = pages[s * 12:(s + 1) * 12]
        rows = math.ceil(len(chunk) / GRID_COLS)
        cell_h = int(CELL_W * 7.5 / 13.333)
        grid = Image.new("RGB", (CELL_W * GRID_COLS + 8 * (GRID_COLS + 1),
                                 (cell_h + 30) * rows + 8 * (rows + 1)), (235, 235, 235))
        for idx, img in enumerate(chunk):
            col, row = idx % GRID_COLS, idx // GRID_COLS
            x = 8 + col * (CELL_W + 8)
            y = 8 + row * (cell_h + 30)
            grid.paste(img.resize((CELL_W, cell_h)), (x, y + 24))
            from PIL import ImageDraw
            d = ImageDraw.Draw(grid)
            d.text((x + 4, y + 4), f"slide {s * 12 + idx + 1}", fill=(180, 30, 30))
        out = f"{args.prefix}-{s + 1}.jpg"
        grid.save(out, quality=85)
        outs.append(out)
        print(f"[lls-pptx] → {out}（第 {s * 12 + 1}–{min((s + 1) * 12, total)} 页）")
    print(f"[lls-pptx] 共 {total} 页，{len(outs)} 张总览图。先看总览，再细看封面/最密页/图表页/结束页。")
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
