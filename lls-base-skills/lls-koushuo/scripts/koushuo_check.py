#!/usr/bin/env python3
"""口播稿 lint：时长预算 / 开场钩子 / 段落节奏 / CTA 存在。

用法: python3 koushuo_check.py 口播稿.md --minutes 3
"""
import argparse
import re

from lls_koushuo_utils import budget_check, die, hook_check, split_scenes

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("--minutes", type=float, required=True, help="目标时长（分钟）")
args = ap.parse_args()

text = open(args.input, encoding="utf-8").read()
b = budget_check(text, args.minutes)
print(f"[lls-koushuo] 字数 {b['chars']} | 预计 {b['estimated_minutes']} 分钟（目标 {b['target_minutes']}，偏差 {b['delta_pct']:+d}%）")
problems = []
if abs(b["delta_pct"]) > 15:
    direction = "删减" if b["delta_pct"] > 0 else "扩写"
    problems.append(f"时长偏差 {b['delta_pct']:+d}%（中文口播按 {240} 字/分钟估算）——建议{direction}")
hook = hook_check(text)
if hook:
    problems.append(hook)
scenes = split_scenes(text)
long_scenes = [(h, n) for h, n in scenes if n > 300]
if long_scenes:
    problems.append(f"{len(long_scenes)} 段超过 300 字（{long_scenes[:3]}）——口播单段建议 ≤150 字，超长拆分")
if not re.search(r"(关注|点赞|评论区|私信|下期|链接|主页)", text):
    problems.append("无 CTA（关注/点赞/评论区/私信…）——结尾引导缺失")
if problems:
    print(f"[lls-koushuo] ⚠️ {len(problems)} 项：")
    for p in problems:
        print("  - " + p)
    exit(1)
print("[lls-koushuo] ✅ 时长/钩子/节奏/CTA 全部达标")
