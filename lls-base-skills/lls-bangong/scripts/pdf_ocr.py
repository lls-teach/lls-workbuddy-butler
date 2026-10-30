#!/usr/bin/env python3
"""中文 OCR（可选依赖 PaddleOCR，Apache-2.0）。输入 PDF 或图片，输出带页分隔的文本。

用法: python3 pdf_ocr.py 输入.pdf或图片 [-p 1-3] -o 输出.txt [--lang ch]
注意: 首次运行会下载识别模型（数百 MB），需告知用户。超过 20 页请先单页试跑确认质量。
"""
import argparse
import os
import sys
import tempfile

from lls_pdf_utils import die, ensure_parent, ocr_lines, parse_page_range

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


def pdf_to_images(pdf_path: str, pages_spec: str | None) -> list[tuple[int, str]]:
    """复用同目录的 pdf_render 逻辑出图，返回 (页码, 图片路径) 列表。"""
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(pdf_path)
    total = len(pdf)
    idx = parse_page_range(pages_spec, total)
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
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="中文 OCR")
    ap.add_argument("input")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("-p", "--pages")
    ap.add_argument("--lang", default="ch", help="ch=中英混合 en=英文")
    args = ap.parse_args()

    engine = load_engine(args.lang)

    if args.input.lower().endswith(".pdf"):
        images = pdf_to_images(args.input, args.pages)
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


if __name__ == "__main__":
    main()
