#!/usr/bin/env python3
"""平台文案 lint：平台规范 + AI 味检测（双报告合一）。

用法: python3 wentan_check.py 文案.md --platform 小红书
平台: 小红书/公众号/抖音口播/朋友圈
"""
import argparse
import re

from lls_wenan_utils import AI_FLAVOR, PLATFORMS

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("--platform", required=True, choices=list(PLATFORMS))
args = ap.parse_args()

spec = PLATFORMS[args.platform]
text = open(args.input, encoding="utf-8").read()
lines = [l for l in text.split("\n") if l.strip()]
title = lines[0].strip() if lines else ""
body_wo_title = "\n".join(lines[1:]) if len(lines) > 1 else ""

problems, passed = [], []

# 标题
if spec["title_max"]:
    if len(title) > spec["title_max"]:
        problems.append(f"❌ 标题 {len(title)} 字超平台上限 {spec['title_max']}")
    else:
        passed.append(f"✅ 标题 {len(title)} 字（≤{spec['title_max']}）")
if spec["emoji_required"] and not re.search(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", title):
    problems.append("⚠️ 小红书标题建议带 1 个 emoji（钩子位）")

# 正文长度
body_len = len(re.sub(r"\s", "", body_wo_title))
if body_len > spec["body_max"]:
    problems.append(f"❌ 正文 {body_len} 字超上限 {spec['body_max']}——删细节保留钩子")
else:
    passed.append(f"✅ 正文 {body_len} 字（≤{spec['body_max']}）")

# 标签
tags = re.findall(r"#\S+", text)
if spec["tags_min"] and len(tags) < spec["tags_min"]:
    problems.append(f"⚠️ 标签 {len(tags)} 个 < 最低 {spec['tags_min']} 个（流量入口）")
else:
    passed.append(f"✅ 标签 {len(tags)} 个")

# AI 味
flavor = []
for w in AI_FLAVOR:
    n = text.count(w)
    if n:
        flavor.append((w, n))
if flavor:
    flavor.sort(key=lambda kv: -kv[1])
    problems.append(f"🤖 AI 味命中 {sum(n for _, n in flavor)} 处：")
    for w, n in flavor[:8]:
        problems.append(f"    「{w}」×{n} → 改写方向：{AI_FLAVOR[w]}")
else:
    passed.append("✅ AI 味黑名单 0 命中")

# 抖音口播专项：长句
if args.platform == "抖音口播":
    long_sents = [s for s in re.split(r"[。！？\n]", text) if len(s.strip()) > 15]
    if long_sents:
        problems.append(f"⚠️ {len(long_sents)} 句超过 15 字（口播断句）——拆成短句")

out_lines = [f"# {args.platform} 文案体检", ""]
out_lines += [f"- {p}" for p in passed] + [f"- {p}" for p in problems]
out_lines += ["", "> AI 味改写由对话中的 AI 执行；改完重跑本检查直到全绿。"]
print("\n".join(out_lines))
import sys
sys.exit(1 if problems else 0)
