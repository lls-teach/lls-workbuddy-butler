#!/usr/bin/env python3
"""字幕清洗：口头禅删除 + 错别字替换表 + 连续重复行去重（时间轴不动）。

用法:
  python3 zimu_clean.py 字幕.srt -o 修正.srt
  python3 zimu_clean.py 字幕.srt -o 修正.srt --map 替换.json    # {"错词":"对词",...}
"""
import argparse
import json

from lls_zimu_utils import clean_text, ensure_parent, parse_srt, write_srt

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("-o", "--output", required=True)
ap.add_argument("--map", help="替换表 JSON（键=错词 值=对词）")
ap.add_argument("--fillers", action="store_true", default=True, help="删除口头禅（默认开）")
ap.add_argument("--no-dedupe", action="store_true")
args = ap.parse_args()

replacements = json.load(open(args.map, encoding="utf-8")) if args.map else None
blocks, _ = parse_srt(text=open(args.input, encoding="utf-8", errors="ignore").read())
if not blocks:
    print("[lls-zimu] ❌ 无字幕块")
    raise SystemExit(1)

dedupe = not args.no_dedupe
filler_n = rep_n = dedupe_n = 0
prev = None
for b in blocks:
    new, fn, rn = clean_text(b["text"], replacements)
    b["text"], filler_n, rep_n = new, filler_n + fn, rep_n + rn
    if dedupe and prev is not None and b["text"] and b["text"] == prev:
        b["text"] = ""
        dedupe_n += 1
    prev = b["text"]

ensure_parent(args.output)
write_srt(blocks, args.output)
kept = sum(1 for b in blocks if b["text"])
print(f"[lls-zimu] 清洗完成 → {args.output}")
print(f"[lls-zimu] 口头禅删除 {filler_n} 处 ｜ 替换 {rep_n} 处 ｜ 连续重复去重 {dedupe_n} 块 ｜ 保留 {kept}/{len(blocks)} 块")
print("[lls-zimu] ⚠️ 替换表请人工过目——字幕纠错以不改变原意为底线")
