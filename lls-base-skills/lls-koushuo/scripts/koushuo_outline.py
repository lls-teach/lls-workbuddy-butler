#!/usr/bin/env python3
"""主题+要点 → 带时长预算的口播稿骨架（黄金 3 秒钩子位/正文分段/金句位/CTA 位）。

用法: python3 koushuo_outline.py --title 主题 --minutes 3 --points "要点1,要点2,要点3" -o 骨架.md
"""
import argparse
import re

from lls_koushuo_utils import WPM, die, ensure_parent

ap = argparse.ArgumentParser()
ap.add_argument("--title", required=True)
ap.add_argument("--minutes", type=float, required=True)
ap.add_argument("--points", required=True, help="逗号分隔（支持 , ， 、）")
ap.add_argument("-o", "--output", required=True)
args = ap.parse_args()

if args.minutes <= 0:
    die("目标时长须大于 0（分钟）")
points = [p.strip() for p in re.split(r"[,，、]", args.points) if p.strip()]
if not points:
    die("至少一个要点")
total_chars = int(WPM * args.minutes)
hook_chars = int(total_chars * 0.12)
cta_chars = int(total_chars * 0.08)
body_chars = total_chars - hook_chars - cta_chars
per = body_chars // len(points)

out = [
    f"# 口播稿骨架：{args.title}（目标 {args.minutes} 分钟 ≈ {total_chars} 字）", "",
    f"## 【开场钩子】预算 {hook_chars} 字（前 3 秒决定完播）",
    "- 问句式 / 数字式 / 反常识式 三选一，例：「你有没有发现……」",
    "", f"## 【正文】预算 {body_chars} 字（每段 {per} 字左右，拆成 ≤150 字的小段口播）",
]
for i, p in enumerate(points, 1):
    out += [f"### 段 {i}：{p}（约 {per} 字）", "- 论点 + 例子/数据 + 一句小结", ""]
out += [
    "## 【金句位】（正文最后一段收尾，可截图传播的一句话）",
    "", f"## 【CTA】预算 {cta_chars} 字", "- 关注/点赞/评论区提问/下期预告 三选一",
]
ensure_parent(args.output)
open(args.output, "w", encoding="utf-8").write("\n".join(out))
print(f"[lls-koushuo] 骨架 → {args.output}（钩子 {hook_chars} 字 / 正文 {body_chars} 字 / CTA {cta_chars} 字）")
