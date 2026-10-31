#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""taste 发牌：给页面发美术方向牌，三选一。纯标准库，零依赖。
按槽位重抽：python scripts/taste_deal.py --redraw palette --seed 9
（只换配色槽位，理由必填，写进简报）
"""
import argparse
import json
import os
import random
import sys

DECK_PATH = os.path.join(os.path.dirname(__file__), "..", "references", "taste-palettes.json")


def load_deck():
    with open(DECK_PATH, encoding="utf-8") as f:
        return json.load(f)


def fmt_card(card, idx=None):
    head = "【牌 %s】%s (%s)" % (idx, card["name_zh"], card["id"]) if idx else "【%s】(%s)" % (card["name_zh"], card["id"])
    lines = [
        head,
        "  气质：%s｜适用：%s" % (card["mood"], card["for_theme"]),
        "  配色：底 %s／墨 %s／强调 %s／块 %s" % (card["paper"], card["ink"], card["accent"], card["block"]),
        "  比例：%s" % card["ratio"],
        "  idea 引导：%s" % card["idea_hint"],
    ]
    if card.get("dark"):
        lines.append("  ※ 深底牌：底墨角色互换，字用浅墨，强调色只给最高光的一处")
    return "\n".join(lines)


def direction_sheet(card):
    return "\n".join([
        "＝＝＝ 美术方向单 ＝＝＝",
        fmt_card(card),
        "",
        "填空（动笔前写出）：",
        "  在这份 deck 里，___（主题独有的东西）变成 ___（版式装置）。",
        "",
        "与风格配方的关系：颜色按本牌走，比例按配方拿；",
        "打架时先换一次牌，主题色极明确时保留比例换颜色，并写进报告。",
    ])


def main(argv=None):
    ap = argparse.ArgumentParser(description="taste 发牌：给 PPT 发美术方向牌")
    ap.add_argument("--options", type=int, default=3, help="发几张牌（默认 3）")
    ap.add_argument("--seed", type=int, default=None, help="随机种子，可复现")
    ap.add_argument("--palette", default=None, help="打印指定牌的方向单（用牌 id）")
    ap.add_argument("--list", action="store_true", help="列出整副牌")
    ap.add_argument("--redraw", default=None, help="按槽位重抽：palette")
    args = ap.parse_args(argv)

    deck = load_deck()
    cards = deck["cards"]

    if args.list:
        for c in cards:
            print(fmt_card(c))
            print()
        print("共 %d 张｜禁用组合：%s" % (len(cards), "、".join(deck["banned"])))
        return 0

    if args.palette:
        hit = [c for c in cards if c["id"] == args.palette]
        if not hit:
            print("没有这张牌：%s，用 --list 查看整副牌" % args.palette, file=sys.stderr)
            return 1
        print(direction_sheet(hit[0]))
        return 0

    rng = random.Random(args.seed)
    n = max(1, min(args.options, len(cards)))
    dealt = rng.sample(cards, n)
    seed_note = "（seed=%s）" % args.seed if args.seed is not None else ""
    if args.redraw == "palette":
        print("按槽位重抽配色%s，新牌如下（理由必填，写进简报）：\n" % seed_note)
    else:
        print("发牌 %d 张%s，选一张最契合主题的：\n" % (n, seed_note))
    for i, c in enumerate(dealt, 1):
        print(fmt_card(c, i))
        print()
    print("选定后跑：python scripts/taste_deal.py --palette <id>  打印方向单")
    return 0


if __name__ == "__main__":
    sys.exit(main())
