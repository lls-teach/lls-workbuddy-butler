#!/usr/bin/env python3
"""Markdown 缩进大纲 → 思维导图双输出（FreeMind .mm 可导入 XMind/幕布 + 自包含 HTML 交互图）。

用法: python3 naotu_make.py 大纲.md -o 中心主题 [--html]
md 语法：# 中心主题 / ## 一级分支 / - 二级要点 / 缩进两空格 - 三级细节
标题层级与要点层级统一标尺：## = 1 级、### = 2 级、- = 2 级、
缩进两空格的 - = 3 级，依此类推；层级跳级时就近贴靠上一级，不丢节点。
"""
import argparse
import html
import os
import re

from lls_naotu_utils import die, ensure_parent

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("-o", "--output", required=True, help="输出 .mm 文件基础名")
ap.add_argument("--html", action="store_true", help="同时输出自包含 HTML")
args = ap.parse_args()

try:
    lines = open(args.input, encoding="utf-8").read().split("\n")
except FileNotFoundError:
    die(f"输入文件不存在: {args.input}")
except UnicodeDecodeError:
    die(f"输入文件不是 UTF-8 编码: {args.input}")
# 解析
root, nodes = None, []
for line in lines:
    if re.match(r"^# ", line):
        root = line[2:].strip()
        break
if not root:
    root = "中心主题"
raw_nodes = []
for line in lines:
    if line.startswith("# "):
        continue
    m = re.match(r"^(\s*)[-*]\s+(.*)$", line)
    if m:
        # - 本身是 2 级（SKILL 层级语法：## 一级分支 / - 二级要点），
        # 每多缩进两空格加一级；与标题标尺（##=1、###=2）对齐。
        depth = len(m.group(1)) // 2 + 2
        raw_nodes.append((depth, m.group(2).strip()))
    else:
        h = re.match(r"^(#{2,})\s+(.*)$", line)
        if h:
            depth = len(h.group(1)) - 1
            raw_nodes.append((depth, h.group(2).strip()))
# 归一化：先以首节点为 1 级平移（纯要点大纲首个 - 本是 2 级，
# 平移后为 1 级，且同级要点仍互为兄弟，不会因首节点被压级而变父子），
# 再把跳级压到上一节点深一级；下降不限。否则递归建树会把跳级
# 节点及之后节点静默丢掉。
nodes = []
prev = 0
first_raw = raw_nodes[0][0] if raw_nodes else 1
for depth, text in raw_nodes:
    nd = depth - first_raw + 1
    if nd < 1:
        nd = 1
    if nodes and nd > prev + 1:
        nd = prev + 1
    nodes.append((nd, text))
    prev = nd
if not nodes:
    die("大纲为空（需要 ## 一级分支 与 - 要点）")

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
ensure_parent(mm_path)
open(mm_path, "w", encoding="utf-8").write(mm)

# 自包含 HTML（缩进树；与 .mm 用同一归一化节点表、同一递归结构，
# 保证两者节点一一对应，且标签成对闭合）
def build_html(nodes, idx, depth):
    """递归构建 HTML 片段，返回 (html, next_idx)。"""
    if idx >= len(nodes) or nodes[idx][0] < depth:
        return "", idx
    out = []
    while idx < len(nodes) and nodes[idx][0] == depth:
        text = nodes[idx][1]
        child_html, idx = build_html(nodes, idx + 1, depth + 1)
        child = f"<ul>{child_html}</ul>" if child_html else ""
        out.append(f"<li>{html.escape(text)}{child}</li>")
    return "".join(out), idx

tree_body, _ = build_html(nodes, 0, 1)
tree_html = f'<ul class="root">{tree_body}</ul>'

html_doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>{html.escape(root)}</title>
<style>body{{font-family:'PingFang SC','Microsoft YaHei',sans-serif;margin:24px;background:#fafaf7;color:#212428}}
ul{{list-style:none;padding-left:22px;border-left:2px solid #d9dce0}} li{{margin:6px 0;line-height:1.6}}
.root{{border-left:none;font-weight:bold;font-size:18px}}</style></head><body>
<h2>{html.escape(root)}</h2>{tree_html}</body></html>"""
# 只替换末尾扩展名：目录名含 .mm 时 str.replace 会改坏目录部分。
html_path = os.path.splitext(mm_path)[0] + ".html"
ensure_parent(html_path)
open(html_path, "w", encoding="utf-8").write(html_doc)

print(f"[lls-naotu] FreeMind → {mm_path}（可导入 XMind/幕布/FreeMind）")
print(f"[lls-naotu] HTML 预览 → {html_path}（浏览器直接打开，分支缩进树）")
print(f"[lls-naotu] 节点 {len(nodes)} 个，中心「{root}」")
