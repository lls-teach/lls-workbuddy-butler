#!/usr/bin/env python3
"""分镜表 lint：台词语速、总时长、景别合法性、空画面位。

用法: python3 fenjing_check.py 分镜表.md [--limit 60]
"""
import argparse
import re

from lls_fenjing_utils import SHOTS, die

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("--limit", type=int, default=60, help="视频总时长上限（秒）")
args = ap.parse_args()

md = open(args.input, encoding="utf-8").read()
rows = [l for l in md.split("\n") if l.startswith("|") and "---" not in l][1:]
problems, total = [], 0
for r in rows:
    cells = [c.strip() for c in r.strip("|").split("|")]
    if len(cells) < 6:
        problems.append(f"列数不足: {r[:40]}")
        continue
    no, start, dur, shot, visual, line = cells[0], cells[1], cells[2], cells[3], cells[4], cells[5]
    try:
        d = int(dur)
    except ValueError:
        problems.append(f"镜头 {no} 时长非整数: {dur}")
        continue
    total += d
    words = len(re.sub(r"\s", "", line))
    if words / max(d, 1) > 5.5:
        problems.append(f"镜头 {no} 语速过快：{words} 字 / {d} 秒（>5.5 字/秒，念不完）")
    if shot not in SHOTS:
        problems.append(f"镜头 {no} 景别不在词表: {shot}（可选 {'/'.join(SHOTS)}）")
    if not visual or visual.startswith("TODO"):
        problems.append(f"镜头 {no} 画面描述缺失")
if total > args.limit:
    problems.append(f"总时长 {total} 秒超上限 {args.limit} 秒——砍镜头或压缩台词")
if problems:
    print(f"[lls-fenjing] ❌ {len(problems)} 项：")
    for p in problems:
        print("  - " + p)
    exit(1)
print(f"[lls-fenjing] ✅ {len(rows)} 镜头 / 总时长 {total} 秒，语速与结构全部达标")
