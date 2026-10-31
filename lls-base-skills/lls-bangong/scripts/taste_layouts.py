#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""taste 版式牌：为每页指派版式蓝图，同构图一 deck 最多 2 次。纯标准库。
版式牌从 lls-pptx v1–v5 验证过的版式提炼（references/taste-layouts.json）。

用法：
    python scripts/taste_layouts.py --assign --pages 12 --seed 3   # 指派 12 页版式
    python scripts/taste_layouts.py --redraw-layout 5 --current hero-number --seed 7
    python scripts/taste_layouts.py --list                          # 看整副牌
"""
import argparse
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "..", "references", "taste-layouts.json")


def load_lib():
    with open(LIB, encoding="utf-8") as f:
        return json.load(f)


def eligible(layouts, page, total):
    out = []
    for l in layouts:
        slots = l.get("slots")
        if slots is None:
            out.append(l)
        elif page in slots or (page == total and -1 in slots):
            out.append(l)
    return out


def assign(pages, seed):
    lib = load_lib()
    layouts = lib["layouts"]
    cap = lib.get("cap_per_deck", 2)
    rng = random.Random(seed)
    used = {}
    result = {}
    for p in range(1, pages + 1):
        pool = [l for l in eligible(layouts, p, pages) if used.get(l["id"], 0) < cap]
        if not pool:  # 兜底：放宽上限
            pool = eligible(layouts, p, pages)
        # 固定槽位优先：封面/末页有专属版式时直接定，不消耗随机
        fixed = [l for l in pool if l.get("slots") == [p] or (p == pages and l.get("slots") == [-1])]
        pick = fixed[0] if fixed else rng.choice(pool)
        used[pick["id"]] = used.get(pick["id"], 0) + 1
        result[p] = pick
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="taste 版式牌：指派/重抽")
    ap.add_argument("--assign", action="store_true", help="为整 deck 指派版式")
    ap.add_argument("--pages", type=int, default=12, help="总页数")
    ap.add_argument("--seed", type=int, default=None, help="随机种子")
    ap.add_argument("--redraw-layout", type=int, default=None, metavar="PAGE", help="重抽某页版式")
    ap.add_argument("--current", default=None, help="该页当前版式 id（重抽时排除）")
    ap.add_argument("--list", action="store_true", help="列出整副牌")
    args = ap.parse_args(argv)

    lib = load_lib()
    layouts = lib["layouts"]

    if args.list:
        for l in layouts:
            print("【%s】(%s)｜%s｜适用：%s" % (l["name_zh"], l["id"], l["结构"], l["适用"]))
        print("共 %d 张｜同构图一 deck 最多 %d 次" % (len(layouts), lib.get("cap_per_deck", 2)))
        return 0

    if args.redraw_layout:
        p = args.redraw_layout
        pool = [l for l in eligible(layouts, p, args.pages) if l["id"] != args.current]
        if not pool:
            print("无可替换版式", file=sys.stderr)
            return 1
        rng = random.Random(args.seed)
        pick = rng.choice(pool)
        print("第 %d 页重抽：%s → %s（%s）｜理由必填，写进简报" % (p, args.current, pick["name_zh"], pick["id"]))
        return 0

    if args.assign:
        result = assign(args.pages, args.seed)
        print("版式指派（seed=%s，同构图≤%d 次）：\n" % (args.seed, lib.get("cap_per_deck", 2)))
        for p in range(1, args.pages + 1):
            l = result[p]
            print("第 %2d 页：%s（%s）" % (p, l["name_zh"], l["id"]))
        print("\n指派结果写入设计简报；换某页版式用 --redraw-layout <页> --current <id>，理由写进简报")
        return 0

    ap.error("需要 --assign、--redraw-layout 或 --list")


if __name__ == "__main__":
    sys.exit(main())
