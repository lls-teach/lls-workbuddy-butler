#!/usr/bin/env python3
"""课程信息 → teaching 风格课件大纲（知识点拆页 + 练习页 + 章节分隔页）。

用法: python3 kejian_outline.py --json 课程.json -o 课件大纲.md
JSON: {"course":"课程名","audience":"受众","lessons":[{"topic":"知识点","points":["a","b","c"],"quiz":"练习题?"}]}
拆页规则：每页 ≤4 要点；每 3 个知识点前插 1 个章节分隔页
（第 1、4、7…个知识点前）；quiz 非空则生成练习页；课程结束生成课程小结页。
"""
import argparse
import json

def ceil(a, b):
    return -(-a // b)

from lls_shuzhi_like import die, ensure_parent

ap = argparse.ArgumentParser()
ap.add_argument("--json", required=True)
ap.add_argument("-o", "--output", required=True)
args = ap.parse_args()

try:
    with open(args.json, encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    die(f"找不到课程 JSON：{args.json}")
except json.JSONDecodeError as e:
    die(f"课程 JSON 格式错误：{e}")
except UnicodeDecodeError as e:
    die(f"课程 JSON 编码错误（需 UTF-8）：{e}")
if not isinstance(data, dict):
    die("课程 JSON 顶层须为对象")
lessons = data.get("lessons", [])
if not isinstance(lessons, list) or not lessons:
    die("lessons 为空或不是列表")

out = [f"# {data.get('course','课程')}（受众：{data.get('audience','未注明')}）"]
section_no = 0
for i, lesson in enumerate(lessons):
    if not isinstance(lesson, dict) or not lesson.get("topic"):
        die(f"第 {i + 1} 个 lesson 缺 topic")
    if i % 3 == 0:
        section_no += 1
        out.append(f"# 第{section_no}部分 · {lesson['topic']}")
    points = lesson.get("points", [])
    if not isinstance(points, list):
        die(f"第 {i + 1} 个 lesson 的 points 不是列表")
    for j in range(0, max(len(points), 1), 4):
        out.append(f"## {lesson['topic']}" + (f"（{j // 4 + 1}/{ceil(len(points), 4)}）" if len(points) > 4 else ""))
        for p in points[j:j + 4]:
            out.append(f"- {p}")
        if not points:
            out.append("- （待补要点）")
    if lesson.get("quiz"):
        out.append(f"## 课堂练习：{lesson['quiz']}")
out.append("# 课程小结")
for l in lessons:
    out.append(f"- {l['topic']}")

ensure_parent(args.output)
# newline="\n"：Windows 下默认写出 CRLF，显式固定为 LF，保证跨平台输出字节一致。
open(args.output, "w", encoding="utf-8", newline="\n").write("\n".join(out))
n_quiz = sum(1 for l in lessons if l.get("quiz"))
n_pages = sum(1 for l in out if l.startswith("## "))
print(f"[lls-kejian] 课件大纲 → {args.output}（知识点 {len(lessons)} 个 → {n_pages - n_quiz} 知识点页 + {n_quiz} 练习页）")
print("[lls-kejian] 下一步：按 teaching 风格将本大纲渲染成片")
