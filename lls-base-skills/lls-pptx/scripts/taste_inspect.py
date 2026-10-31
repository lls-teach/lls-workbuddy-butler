#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""taste 渲染质检：对渲染后的 PNG 页做程序化测量（Pillow）。
这是"lint（源码）→测量（渲染）→人看（十三遍）"三层中的测量层。
文字碰撞/溢出这类要 OCR 的不做，留给十三遍看图法第 12 遍。

检查项（每页）：
  [FAIL] 画幅比不是 16:9（±2%）
  [WARN] 空白率 >88%：疑似空洞
  [WARN] 内容贴边：四边 4% 条带内有非底色像素 >2%
  [WARN] 主色跑出牌面配色：与牌面 4 色色距>70 的颜色占比 >12%

用法：
    python scripts/taste_inspect.py --pages "render/p-*.png" --palette rose-grey-green
"""
import argparse
import glob
import json
import math
import os
import sys

try:
    from PIL import Image
except ImportError:
    print("需要 Pillow：pip install pillow", file=sys.stderr)
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
DECK_PATH = os.path.join(HERE, "..", "references", "taste-palettes.json")


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def analyze(path, palette):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    small = img.resize((480, int(480 * h / w)))
    px = list(small.getdata())
    n = len(px)
    paper = hex2rgb(palette["paper"])
    pal_colors = [hex2rgb(palette[k]) for k in ("paper", "ink", "accent", "block")]

    fails, warns = [], []

    # 1. 画幅比
    ratio = w / h
    if abs(ratio - 16 / 9) > 0.02 * (16 / 9):
        fails.append("画幅比 %.2f 不是 16:9" % ratio)

    def is_bg(p):
        return dist(p, paper) < 36

    # 2. 空白率（幻灯片校准：纸底图表计入空白，合法稀疏页约 88–96%，仅 >97% 告警）
    blank = sum(1 for p in px if is_bg(p)) / n
    if blank > 0.97:
        warns.append("空白率 %.0f%%，疑似空洞" % (blank * 100))

    # 3. 贴边
    sw, sh = small.size
    bw, bh = max(1, sw // 25), max(1, sh // 25)
    strips = {
        "左": [px[y * sw + x] for y in range(sh) for x in range(bw)],
        "右": [px[y * sw + x] for y in range(sh) for x in range(sw - bw, sw)],
        "上": [px[y * sw + x] for y in range(bh) for x in range(sw)],
        "下": [px[y * sw + x] for y in range(sh - bh, sh) for x in range(sw)],
    }
    for edge, sp in strips.items():
        nonbg = [p for p in sp if not is_bg(p)]
        hit = len(nonbg) / len(sp)
        if hit <= 0.02:
            continue
        # 满版铺底色不算贴边：条带内主导色占比>90% 即视为底
        from collections import Counter
        top = Counter(nonbg).most_common(1)[0]
        if top[1] / len(sp) > 0.80:
            continue
        warns.append("%s边贴边（内容占比 %.0f%%）" % (edge, hit * 100))

    # 4. 主色 vs 牌面配色
    colors = small.getcolors(480 * 480)
    out_cov = 0.0
    if colors:
        for cnt, col in colors:
            if min(dist(col, pc) for pc in pal_colors) > 70:
                out_cov += cnt / n
    if out_cov > 0.12:
        warns.append("跑出牌面配色的颜色占比 %.0f%%，疑似助手配色" % (out_cov * 100))

    return fails, warns


def main(argv=None):
    ap = argparse.ArgumentParser(description="taste 渲染质检")
    ap.add_argument("--pages", required=True, help="渲染 PNG 的 glob，如 \"render/p-*.png\"")
    ap.add_argument("--palette", required=True, help="牌面 id")
    args = ap.parse_args(argv)

    deck = json.load(open(DECK_PATH, encoding="utf-8"))["cards"]
    pal = next((c for c in deck if c["id"] == args.palette), None)
    if not pal:
        print("没有这张牌：%s" % args.palette, file=sys.stderr)
        return 1

    files = sorted(glob.glob(args.pages))
    if not files:
        print("没有匹配的页面：%s" % args.pages, file=sys.stderr)
        return 1

    any_fail = False
    for f in files:
        fails, warns = analyze(f, pal)
        name = os.path.basename(f)
        if fails:
            any_fail = True
            for m in fails:
                print("[FAIL] %s：%s" % (name, m))
        for m in warns:
            print("[WARN] %s：%s" % (name, m))
        if not fails and not warns:
            print("[PASS] %s" % name)
    if any_fail:
        return 1
    print("测量完成：无 FAIL；WARN 按纪律处理（修或一句话辩护进报告）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
