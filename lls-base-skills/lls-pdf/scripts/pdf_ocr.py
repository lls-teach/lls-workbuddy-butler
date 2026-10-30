#!/usr/bin/env python3
"""中文 OCR（可选依赖 PaddleOCR，Apache-2.0）。输入 PDF 或图片，输出带页分隔的文本。

用法: python3 pdf_ocr.py 输入.pdf或图片 [-p 1-3] -o 输出.txt [--lang ch]
注意: 首次运行会下载识别模型（数百 MB），需告知用户。超过 20 页请先单页试跑确认质量。
"""
import argparse
import os
import shutil
import sys
import tempfile

from lls_pdf_utils import die, ensure_parent, ensure_utf8_stdio, ocr_lines, parse_page_range

requirements_hint = "python3 -m pip install paddleocr paddlepaddle"


def load_engine(lang: str):
    try:
        from paddleocr import PaddleOCR
    except ImportError:
        die("PaddleOCR 未安装。安装命令:\n  " + requirements_hint +
            "\n首次使用会下载模型，耗时取决于网络。装好后再运行本命令。")
    # Windows 上 paddlepaddle 3.x 的 onednn/PIR 推理会报 NotImplementedError，OCR 须关 mkldnn
    kwargs = {"use_angle_cls": True, "lang": lang}
    if sys.platform == "win32":
        kwargs["enable_mkldnn"] = False
    try:
        return PaddleOCR(show_log=False, **kwargs)  # paddleocr 2.x 参数
    except (TypeError, ValueError):
        return PaddleOCR(**kwargs)  # paddleocr 3.x 已移除 show_log


def pdf_to_images(pdf_path: str, pages_spec: str | None) -> tuple[list[tuple[int, str]], str]:
    """复用同目录的 pdf_render 逻辑出图，返回 ((页码, 图片路径) 列表, 临时目录)。

    临时目录由调用方在 finally 里删除，避免每次 OCR 都在系统临时目录
    下留下一批 page_*.png（Windows 下 %TEMP% 同样会越积越多）。
    """
    import pypdfium2 as pdfium
    try:
        pdf = pdfium.PdfDocument(pdf_path)
    except Exception as e:  # noqa: BLE001
        die(f"无法打开 PDF: {e}")
    try:
        total = len(pdf)
        idx = parse_page_range(pages_spec, total)
    except ValueError as e:
        die(str(e))
    tmp = tempfile.mkdtemp(prefix="lls_pdf_ocr_")
    out = []
    scale = 200 / 72.0
    for i in idx:
        page = pdf[i]
        img = page.render(scale=scale).to_pil()
        p = os.path.join(tmp, f"page_{i + 1:03d}.png")
        img.save(p)
        out.append((i + 1, p))
        page.close()
    pdf.close()
    return out, tmp


def main() -> None:
    ap = argparse.ArgumentParser(description="中文 OCR")
    ap.add_argument("input")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("-p", "--pages")
    ap.add_argument("--lang", default="ch", help="ch=中英混合 en=英文")
    args = ap.parse_args()

    ensure_utf8_stdio()
    engine = load_engine(args.lang)

    tmp_dir: str | None = None
    try:
        if args.input.lower().endswith(".pdf"):
            images, tmp_dir = pdf_to_images(args.input, args.pages)
        else:
            images = [(1, args.input)]
        if not images:
            die("没有可处理的页面")

        ensure_parent(args.output)
        parts, low_conf = [], []
        for page_no, img_path in images:
            result = ocr_lines(engine, img_path)
            lines = []
            for text, conf in result:
                if conf < 0.85:
                    low_conf.append((page_no, text))
                lines.append(text)
            parts.append(f"===== 第 {page_no} 页 =====\n" + "\n".join(lines))
            print(f"[lls-pdf] 第 {page_no} 页识别 {len(lines)} 行", file=sys.stderr)

        full = "\n\n".join(parts)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(full)
        print(f"[lls-pdf] OCR 完成 {len(images)} 页 → {args.output}（{len(full)} 字符）")
        if low_conf:
            print(f"[lls-pdf] ⚠️ {len(low_conf)} 行置信度 <0.85，待人工核对，示例: {low_conf[:5]}")
    finally:
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
