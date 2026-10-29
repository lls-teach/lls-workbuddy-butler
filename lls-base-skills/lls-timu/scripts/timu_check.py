#!/usr/bin/env python3
"""试题库验收：JSON 数组每题检查题干/选项数/答案存在/重复题干。

用法: python3 timu_check.py 题库.json
题 JSON: {"q":"题干","options":["A","B","C","D"],"answer":"A","topic":"章节"}
"""
import json
import sys

problems, passed = [], []
try:
    items = json.load(open(sys.argv[1], encoding="utf-8"))
except IndexError:
    print("[lls-timu] 用法: timu_check.py 题库.json"); sys.exit(1)
except Exception as e:
    print(f"[lls-timu] 错误: {e}"); sys.exit(1)

if not isinstance(items, list):
    print("[lls-timu] 错误: 题库 JSON 应为数组，每项为一题对象")
    sys.exit(1)
if not items:
    print("[lls-timu] 错误: 题库为空（0 题）")
    sys.exit(1)

stems = {}
for i, q in enumerate(items, 1):
    if not isinstance(q, dict):
        problems.append(f"第 {i} 题格式错误（非对象）")
        continue
    stem = q.get("q", "")
    if not isinstance(stem, str) or not stem.strip():
        problems.append(f"第 {i} 题题干为空")
    opts = q.get("options")
    if opts is not None and (not isinstance(opts, list) or len(opts) < 2):
        problems.append(f"第 {i} 题选项不足 2 个")
    if not q.get("answer"):
        problems.append(f"第 {i} 题缺答案")
    # 查重用完整题干：旧写法只取前 30 字，前缀相同的不同题会被误判重复；
    # 空题干不再参与查重，避免“题干为空”之外再多一条重复
    stem_key = stem.strip() if isinstance(stem, str) else ""
    if stem_key:
        if stem_key in stems:
            problems.append(f"第 {i} 题与第 {stems[stem_key]} 题题干重复")
        else:
            stems[stem_key] = i
if problems:
    print(f"[lls-timu] ❌ {len(problems)} 项：")
    for p in problems:
        print("  - " + p)
    sys.exit(1)
print(f"[lls-timu] ✅ {len(items)} 题全部通过（题干/选项/答案/查重）")
