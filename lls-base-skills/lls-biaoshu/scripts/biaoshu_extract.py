#!/usr/bin/env python3
"""从招标文件提取硬性要求清单 → JSON（内部核对用偏离检查的输入）。

用法: python3 biaoshu_extract.py 招标文件.txt -o 要求清单.json
注意：输入应为纯文本（docx/pdf 先走底座 Word 文档处理技能/PDF 文档处理技能 提取）。
"""
import argparse
import json

from lls_biaoshu_utils import die, ensure_parent, extract_requirements

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("-o", "--output", required=True)
args = ap.parse_args()

text = open(args.input, encoding="utf-8", errors="ignore").read()
if len(text.strip()) < 100:
    die("招标文件文本太短（<100 字）——请先用底座技能提取全文")
reqs = extract_requirements(text)
ensure_parent(args.output)
json.dump({"source": args.input, "count": len(reqs), "requirements": reqs},
          open(args.output, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
from collections import Counter
cats = Counter(r["cat"] for r in reqs)
print(f"[lls-biaoshu] 硬性要求 {len(reqs)} 条 → {args.output}")
print("[lls-biaoshu] 分类分布:", ", ".join(f"{c} {n}" for c, n in cats.most_common()))
