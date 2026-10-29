#!/usr/bin/env python3
"""从招标文件提取硬性要求清单 → JSON（内部核对用偏离检查的输入）。

用法: python3 biaoshu_extract.py 招标文件.txt -o 要求清单.json
注意：输入应为纯文本（docx/pdf 需先提取为纯文本）。
"""
import argparse
import json

from lls_biaoshu_utils import check_missing_elements, die, ensure_parent, extract_requirements

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("-o", "--output", required=True)
args = ap.parse_args()

try:
    text = open(args.input, encoding="utf-8", errors="ignore").read()
except OSError as e:
    die(f"找不到或无法读取招标文件：{args.input}（{e}）")
if len(text.strip()) < 100:
    die("招标文件文本太短（<100 字）——请先将文件提取为纯文本全文")
reqs = extract_requirements(text)
missing = check_missing_elements(text)
ensure_parent(args.output)
json.dump({"source": args.input, "count": len(reqs), "missing_elements": missing, "requirements": reqs},
          open(args.output, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
from collections import Counter
cats = Counter(r["cat"] for r in reqs)
print(f"[lls-biaoshu] 硬性要求 {len(reqs)} 条 → {args.output}")
print("[lls-biaoshu] 分类分布:", ", ".join(f"{c} {n}" for c, n in cats.most_common()))
if missing:
    print("[lls-biaoshu] 缺要素 ❌：" + "、".join(missing) + "——全文未出现，人工确认")
else:
    print("[lls-biaoshu] 缺要素：5 项齐全")
