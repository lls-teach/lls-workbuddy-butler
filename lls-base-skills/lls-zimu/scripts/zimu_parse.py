#!/usr/bin/env python3
"""SRT 结构解析与体检：块数/总时长/语速/重叠/空块。

用法: python3 zimu_parse.py 字幕.srt
"""
import argparse

from lls_zimu_utils import parse_srt

ap = argparse.ArgumentParser()
ap.add_argument("input")
args = ap.parse_args()

text = open(args.input, encoding="utf-8", errors="ignore").read()
blocks, bad = parse_srt(text)
if not blocks:
    print("[lls-zimu] ❌ 未解析出任何字幕块（确认是 SRT 格式）")
    raise SystemExit(1)

total = blocks[-1]["end"] - blocks[0]["start"]
chars = sum(len(b["text"]) for b in blocks)
overlaps = sum(1 for a, b in zip(blocks, blocks[1:]) if b["start"] < a["end"])
speed = chars / total if total else 0
empty = [b["idx"] for b in blocks if not b["text"]]

print(f"[lls-zimu] 块数 {len(blocks)}（坏块跳过 {bad}）｜总时长 {total:.0f} 秒｜文本 {chars} 字")
print(f"[lls-zimu] 平均语速 {speed:.1f} 字/秒（口播舒适区 ≤4）｜时间轴重叠 {overlaps} 处｜空文本块 {len(empty)}")
if speed > 4.5:
    print("[lls-zimu] ⚠️ 语速超舒适区——字幕切换过快，观众跟不上")
if overlaps:
    print("[lls-zimu] ⚠️ 存在时间轴重叠——部分播放器会闪烁")
if empty:
    print(f"[lls-zimu] ⚠️ 空文本块: {empty}")
