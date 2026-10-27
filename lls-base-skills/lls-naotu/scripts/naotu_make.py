#!/usr/bin/env python3
"""Markdown 缩进大纲 → 思维导图双输出（FreeMind .mm 可导入 XMind/幕布 + 自包含 HTML 交互图）。

用法: python3 naotu_make.py 大纲.md -o 中心主题 [--html]
md 语法：# 中心主题 / ## 一级分支 / - 二级 / 缩进两空格 - 三级
"""
import argparse
import html
import re

from lls_naotu_utils import die, ensure_parent

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("-o", "--output", required=True, help="输出 .mm 文件基础名")
ap.add_argument("--html", action="store_true", help="同时输出自包含 HTML")
args = ap.parse_args()

lines = open(args.input, encoding="utf-8").read().split("\n")
# 解析
root, nodes = None, []
for line in lines:
    if re.match(r"^# ", line):
        root = line[2:].strip()
        break
if not root:
    root = "中心主题"
for line in lines:
    if line.startswith("# "):
        continue
    m = re.match(r"^(\s*)[-*]\s+(.*)$", line)
    if m:
        depth = len(m.group(1)) // 2 + 1
        nodes.append((depth, m.group(2).strip()))
    elif re.match(r"^## ", line):
        nodes.append((1, line[3:].strip()))
    elif re.match(r"^### ", line):
        nodes.append((2, line[4:].strip()))
if not nodes:
    die("大纲为空（需要 ## 一级分支 与 - 要点）")

mm = None
def build_mm(nodes, idx, depth):
    """递归构建 .mm 片段，返回 (xml, next_idx)。"""
    if idx >= len(nodes) or nodes[idx][0] < depth:
        return "", idx
    out = []
    while idx < len(nodes) and nodes[idx][0] == depth:
        text = nodes[idx][1]
        child_xml, idx = build_mm(nodes, idx + 1, depth + 1)
        out.append(f'<node TEXT="{html.escape(text)}">{child_xml}</node>')
    return "".join(out), idx

mm_body, _ = build_mm(nodes, 0, 1)
mm = f'<map version="1.0.1"><node TEXT="{html.escape(root)}">{mm_body}</node></map>'
mm_path = args.output if args.output.endswith(".mm") else args.output + ".mm"
open(mm_path, "w", encoding="utf-8").write(mm)

# 自包含 HTML（缩进树 + 折叠）
tree_html = ['<ul class="root">']
prev = 0
stack_open = 0
for depth, text in nodes:
    while stack_open < depth - 1:
        tree_html.append("<ul>")
        stack_open += 1
    while stack_open > depth - 1:
        tree_html.append("</li></ul>")
        stack_open -= 1
    if stack_open == depth - 1 and tree_html[-1] != '<ul class="root">' and not tree_html[-1].endswith("<ul>"):
        pass
    tree_html.append(f"<li>{html.escape(text)}")
    stack_open = depth - 1
tree_html.append("</li></ul>" * (stack_open + 1))
tree_html.append("</ul>")

html_doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>{html.escape(root)}</title>
<style>body{{font-family:'PingFang SC','Microsoft YaHei',sans-serif;margin:24px;background:#fafaf7;color:#212428}}
ul{{list-style:none;padding-left:22px;border-left:2px solid #d9dce0}} li{{margin:6px 0;line-height:1.6}}
.root{{border-left:none;font-weight:bold;font-size:18px}}</style></head><body>
<h2>{html.escape(root)}</h2>{''.join(tree_html)}</body></html>"""
html_path = mm_path.replace(".mm", ".html")
open(html_path, "w", encoding="utf-8").write(html_doc)

print(f"[lls-naotu] FreeMind → {mm_path}（可导入 XMind/幕布/FreeMind）")
print(f"[lls-naotu] HTML 预览 → {html_path}（浏览器直接打开，分支缩进树）")
print(f"[lls-naotu] 节点 {len(nodes)} 个，中心「{root}」")
