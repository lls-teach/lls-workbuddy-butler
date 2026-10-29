#!/usr/bin/env python3
"""原文 → 四平台适配骨架（字数预算/结构模板/改写要点），内容填充由 AI 完成。

用法: python3 wentan_adapt.py 原文.md -o 适配骨架.md
输出: 同一内容在小红书/公众号/抖音口播/朋友圈 四平台的骨架与规范约束。
"""
import argparse

from lls_wenan_utils import PLATFORMS, die, ensure_parent

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("-o", "--output", required=True)
args = ap.parse_args()

try:
    src = open(args.input, encoding="utf-8").read()
except FileNotFoundError:
    die(f"找不到输入文件：{args.input}")
src_len = len(src.strip())

out = [f"# 文案多平台适配骨架（原文 {src_len} 字）", "",
       "> 以下每平台 = 规范约束 + 结构模板。AI 按模板填充，填完逐平台跑 wentan_check.py。", ""]
for name, spec in PLATFORMS.items():
    out += [f"## {name}", f"- 风格：{spec['style']}"]
    if spec["title_max"]:
        out.append(f"- 标题 ≤{spec['title_max']} 字" + ("，建议带 emoji" if spec["emoji_required"] else ""))
    out.append(f"- 正文预算 ≤{spec['body_max']} 字" +
               (f"（原文 {src_len} 字，{'可全量改写' if src_len <= spec['body_max'] else '需压缩至 ' + str(spec['body_max']) + ' 字，砍案例留论点'}）"))
    if spec["tags_min"]:
        out.append(f"- 结尾 ≥{spec['tags_min']} 个 #标签")
    out.append("")
out += ["## 去 AI 味改写要点", "- 黑名单词出现即改（详见 wentan_check.py 内置词库）",
        "- 每段至少一个具体名词/数字/场景，替换抽象总结句",
        "- 口语连接：'但是'替代'然而'、'所以'替代'因此'"]
ensure_parent(args.output)
open(args.output, "w", encoding="utf-8").write("\n".join(out))
print(f"[lls-wenan] 适配骨架 → {args.output}（四平台）")
