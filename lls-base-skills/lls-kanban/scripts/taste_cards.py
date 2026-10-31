#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""taste 亮牌：把美术方向牌渲染成牌面图，展示给用户三选一。
依赖：Pillow（pip install pillow）+ 一个中文字体（自动探测）。

用法：
    python scripts/taste_cards.py --deal 3 --out ./deal/        # 发 3 张并渲染
    python scripts/taste_cards.py --deal 3 --seed 7 --out ./deal/  # 可复现
    python scripts/taste_cards.py --cards rose-grey-green,sand-olive --out ./deal/
"""
import argparse
import json
import os
import random
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("需要 Pillow：pip install pillow", file=sys.stderr)
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
DECK_PATH = os.path.join(HERE, "..", "references", "taste-palettes.json")

W, H = 640, 900
M = 40

_FONT_CANDIDATES = [
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 2),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 2),
    ("/System/Library/Fonts/PingFang.ttc", 0),
    ("C:/Windows/Fonts/msyh.ttc", 0),
]


def load_font(bold, size):
    for path, idx in _FONT_CANDIDATES:
        if bold and "Bold" not in path and "PingFang" not in path and "msyh" not in path:
            continue
        if not bold and "Bold" in path:
            continue
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size, index=idx)
            except Exception:
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue
    return ImageFont.load_default()


def wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for ch in text:
        if draw.textlength(cur + ch, font=font) <= max_w:
            cur += ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def render_card(card, out_path):
    dark = card.get("dark", False)
    paper, ink = card["paper"], card["ink"]
    fg = paper if dark else ink       # 主要文字色
    mut = "#B9B2A4" if dark else "#8A8378"  # 次要文字色

    img = Image.new("RGB", (W, H), paper)
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, W - 10, H - 10], outline=ink, width=6)

    f_title = load_font(True, 62)
    f_id = load_font(False, 24)
    f_sec = load_font(True, 30)
    f_body = load_font(False, 26)
    f_small = load_font(False, 22)
    f_hex = load_font(False, 24)

    y = 52
    d.text((M, y), card["name_zh"], font=f_title, fill=fg)
    y += 92
    d.text((M, y), card["id"], font=f_id, fill=mut)
    y += 44
    d.line([(M, y), (W - M, y)], fill=mut, width=2)
    y += 28

    d.text((M, y), "气质", font=f_sec, fill=fg)
    y += 44
    for ln in wrap(d, card["mood"], f_body, W - 2 * M):
        d.text((M, y), ln, font=f_body, fill=fg)
        y += 38
    y += 8
    d.text((M, y), "适用", font=f_sec, fill=fg)
    y += 44
    for ln in wrap(d, card["for_theme"], f_body, W - 2 * M):
        d.text((M, y), ln, font=f_body, fill=fg)
        y += 38
    y += 16

    d.text((M, y), "配色", font=f_sec, fill=fg)
    y += 48
    roles = [("底", "paper"), ("墨", "ink"), ("强调", "accent"), ("块", "block")]
    for name, key in roles:
        d.rounded_rectangle([M, y, M + 120, y + 64], radius=10, fill=card[key], outline=ink, width=2)
        d.text((M + 140, y + 4), name, font=f_body, fill=fg)
        d.text((M + 140, y + 36), card[key], font=f_hex, fill=mut)
        y += 84
    y += 8

    for ln in wrap(d, "idea：" + card["idea_hint"], f_small, W - 2 * M):
        d.text((M, y), ln, font=f_small, fill=mut)
        y += 34

    d.text((M, H - 56), "taste · lls-pptx", font=f_small, fill=mut)
    img.save(out_path)
    return out_path


def load_deck():
    with open(DECK_PATH, encoding="utf-8") as f:
        return json.load(f)["cards"]


def main(argv=None):
    ap = argparse.ArgumentParser(description="taste 亮牌：渲染牌面图")
    ap.add_argument("--deal", type=int, default=3, help="发几张（默认 3）")
    ap.add_argument("--seed", type=int, default=None, help="随机种子")
    ap.add_argument("--cards", default=None, help="指定牌 id，逗号分隔")
    ap.add_argument("--out", default="./deal", help="输出目录")
    args = ap.parse_args(argv)

    cards = load_deck()
    by_id = {c["id"]: c for c in cards}
    if args.cards:
        picked = [by_id[i.strip()] for i in args.cards.split(",") if i.strip() in by_id]
    else:
        rng = random.Random(args.seed)
        picked = rng.sample(cards, max(1, min(args.deal, len(cards))))

    os.makedirs(args.out, exist_ok=True)
    for c in picked:
        p = os.path.join(args.out, "card-%s.png" % c["id"])
        render_card(c, p)
        print("牌面图：%s（%s · %s）" % (p, c["name_zh"], c["id"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
