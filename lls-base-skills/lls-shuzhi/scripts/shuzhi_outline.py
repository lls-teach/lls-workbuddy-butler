#!/usr/bin/env python3
"""结构化述职 JSON → lls-pptx v2.2 大纲，并输出量化体检。

用法: python3 shuzhi_outline.py 述职.json -o 述职大纲.md
JSON 键: period/kpis[{value,label,note}]/projects[{name,status_rows,bullets,takeaway}]/
        issues[{problem,action}]/plans[{item,goal,milestone,owner}]/verdict/source
"""
import argparse

from lls_shuzhi_utils import compose_outline, ensure_parent, quant_score

ap = argparse.ArgumentParser()
ap.add_argument("json")
ap.add_argument("-o", "--output", required=True)
args = ap.parse_args()

data = __import__("json").load(open(args.json, encoding="utf-8"))
outline = compose_outline(data)
ensure_parent(args.output)
open(args.output, "w", encoding="utf-8").write(outline)

hit, total = quant_score(outline)
print(f"[lls-shuzhi] 大纲已生成 → {args.output}")
print(f"[lls-shuzhi] 量化体检：成果条目 {total} 条，含数字 {hit} 条" +
      ("" if total == 0 or hit == total else f" —— {total - hit} 条无数字，述职汇报的数字就是信用，建议与用户逐条确认真实数据"))
