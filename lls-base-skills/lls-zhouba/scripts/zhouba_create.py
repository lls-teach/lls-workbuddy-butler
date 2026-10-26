#!/usr/bin/env python3
"""结构化 JSON → 周报 docx（本周概览/完成事项/进行中/下周计划/风险求助 五段式）。

用法: python3 zhouba_create.py 周报.json -o 周报.docx
JSON: {"who":"姓名","period":"2026 W44","done":["事项（含量化）"],"doing":["…"],"next":["…"],"risk":["…"]}
"""
import argparse
import json

from docx import Document
from docx.shared import Pt

from lls_jianli_utils_guard import ensure_parent, guard_overwrite, set_cn_font

ap = argparse.ArgumentParser()
ap.add_argument("json")
ap.add_argument("-o", "--output", required=True)
ap.add_argument("--force", action="store_true")
args = ap.parse_args()

data = json.load(open(args.json, encoding="utf-8"))
doc = Document()

def para(text, size=11, bold=False):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    set_cn_font(run)
    return p

para(f'周报 · {data.get("who","")} · {data.get("period","")}', 16, True)
SECTIONS = [("done", "✅ 本周完成"), ("doing", "🔄 进行中"), ("next", "📅 下周计划"), ("risk", "🚨 风险与求助")]
for key, title in SECTIONS:
    para(title, 12, True)
    for item in data.get(key, []):
        para("• " + item, 10.5)
    if not data.get(key):
        para("（无）", 10.5)

out = guard_overwrite(args.output, args.force)
ensure_parent(out)
doc.save(out)
print(f"[lls-zhouba] 周报 → {out}（建议再跑 zhouba_lint.py 做量化体检）")
