#!/usr/bin/env python3
"""编辑已有 PPT：批量替换文字 / 改某页标题。默认不动原文件（输出 _new）。

用法:
  批量替换: python3 pptx_edit.py 输入.pptx --replace "2025=2026" --replace "旧名=新名" -o 新.pptx
  改标题:   python3 pptx_edit.py 输入.pptx --slide 2 --set-title "新标题" --title-size 30 -o 新.pptx
"""
import argparse

from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER
from pptx.util import Pt

from lls_pptx_utils import apply_cn_font, die, ensure_parent, guard_overwrite


def replace_in_shape(shape, pairs: dict[str, str]) -> int:
    count = 0
    if not shape.has_text_frame:
        return count
    for para in shape.text_frame.paragraphs:
        for run in para.runs:
            for old, new in pairs.items():
                if old in run.text:
                    n = run.text.count(old)
                    run.text = run.text.replace(old, new)
                    count += n
    return count


def pick_title_shape(slide):
    """选标题框：旧逻辑取首个非空文本框，在本技能自产 deck 里会误中页眉
    （10pt 运行标题在标题 24-28pt 之前）。新逻辑：占位符标题优先；否则在
    字号 >= 20pt 的文本框中取位置最靠上的一个（标题在证据场 KPI 大数字
    36pt 之上，故不用单纯最大字号）；都没有则回退首个非空框（旧行为）。"""
    candidates = [s for s in slide.shapes if s.has_text_frame and s.text_frame.text.strip()]
    if not candidates:
        return None
    for s in candidates:
        try:
            if s.is_placeholder and s.placeholder_format.type == PP_PLACEHOLDER.TITLE:
                return s
        except Exception:  # noqa: BLE001 - 非占位符形状直接走字号逻辑
            pass
    big = []
    for s in candidates:
        sizes = [r.font.size.pt for p in s.text_frame.paragraphs for r in p.runs if r.font.size]
        if sizes and max(sizes) >= 20:
            big.append((s.top, s))
    if big:
        return min(big, key=lambda t: t[0])[1]
    return candidates[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--replace", dest="replacements", action="append", default=[], help='旧=新，可多次')
    ap.add_argument("--slide", type=int, help="目标页码（配合 --set-title）")
    ap.add_argument("--set-title")
    ap.add_argument("--title-size", type=int, default=30)
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    try:
        prs = Presentation(args.input)
    except Exception as e:  # noqa: BLE001
        die(f"无法打开: {e}")

    total_replaced = 0
    if args.replacements:
        pairs = {}
        for spec in args.replacements:
            if "=" not in spec:
                die(f"--replace 格式应为 旧=新，收到 {spec!r}（缺少 =）")
            old, new = spec.split("=", 1)
            pairs[old] = new
        per_slide = []
        for i, slide in enumerate(prs.slides, 1):
            n = sum(replace_in_shape(shape, pairs) for shape in slide.shapes)
            if n:
                per_slide.append((i, n))
            total_replaced += n
        print(f"[lls-pptx] 替换完成，共 {total_replaced} 处（按页: {per_slide}）")
        if total_replaced == 0:
            print("[lls-pptx] ⚠️ 0 处命中——请核对替换词；SmartArt/图表内文字不在此能力范围")

    if args.slide:
        if not (1 <= args.slide <= len(prs.slides)):
            die(f"页码越界: {args.slide}（共 {len(prs.slides)} 页）")
        if not args.set_title:
            die("--slide 需要 --set-title")
        slide = prs.slides[args.slide - 1]
        title_shape = pick_title_shape(slide)
        if not title_shape:
            die(f"第 {args.slide} 页没有可编辑文本框")
        para = title_shape.text_frame.paragraphs[0]
        if para.runs:
            para.runs[0].text = args.set_title
            for run in para.runs[1:]:
                run.text = ""
        else:
            para.text = args.set_title
        for run in para.runs:
            apply_cn_font(run)
            run.font.size = Pt(args.title_size)
        print(f"[lls-pptx] 第 {args.slide} 页标题已改为 {args.set_title!r}")

    if not args.replacements and not args.slide:
        die("至少给一个 --replace 或 --slide/--set-title")

    out = guard_overwrite(args.output, args.force)
    ensure_parent(out)
    prs.save(out)
    print(f"[lls-pptx] 已保存 → {out}（原文件未动）")


if __name__ == "__main__":
    main()
