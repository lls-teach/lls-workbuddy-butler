#!/usr/bin/env python3
"""课程信息 → PPT 演示文稿技能 teaching 风格课件大纲（知识点拆页 + 练习页 + 章节分隔页）。

用法: python3 kejian_outline.py --json 课程.json -o 课件大纲.md
JSON: {"course":"课程名","audience":"受众","lessons":[{"topic":"知识点","points":["a","b","c"],"quiz":"练习题?"}]}
拆页规则：每页 ≤4 要点；每 3 个知识点页插 1 页小结；quiz 非空则生成练习页。
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

data = json.load(open(args.json, encoding="utf-8"))
lessons = data.get("lessons", [])
if not lessons:
    die("lessons 为空")

out = [f"# {data.get('course','课程')}（受众：{data.get('audience','未注明')}）"]
section_no = 0
for i, lesson in enumerate(lessons):
    if i % 3 == 0:
        section_no += 1
        out.append(f"# 第{section_no}部分 · {lesson['topic']}")
    points = lesson.get("points", [])
    for j in range(0, max(len(points), 1), 4):
        out.append(f"## {lesson['topic']}" + (f"（{j // 4 + 1}/{ceil(len(points), 4)}）" if len(points) > 4 else ""))
        for p in points[j:j + 4]:
            out.append(f"- {p}")
        if not points:
            out.append("- （待补要点）")
    if lesson.get("quiz"):
        out.append(f"## 课堂练习：{lesson['quiz']}")
if len(lessons) >= 3:
    out.append("# 课程小结")
    for l in lessons:
        out.append(f"- {l['topic']}")

ensure_parent(args.output)
open(args.output, "w", encoding="utf-8").write("\n".join(out))
n_pages = sum(1 for l in out if l.startswith("## "))
print(f"[lls-kejian] 课件大纲 → {args.output}（知识点 {len(lessons)} 个 → 约 {n_pages} 内容页）")
print("[lls-kejian] 下一步：将本大纲交给 PPT 演示文稿技能，以 teaching 风格渲染成片")
