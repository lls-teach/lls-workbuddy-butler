#!/usr/bin/env python3
"""结构化 JSON → 周报 docx（本周概览/完成事项/进行中/下周计划/风险求助 五段式）。

用法: python3 zhouba_create.py 周报.json -o 周报.docx
JSON: {"who":"姓名","period":"2026 W44","done":["事项（含量化）"],"doing":["…"],"next":["…"],"risk":["…"]}
"""
import argparse
import json
import sys

try:
    from docx import Document
    from docx.shared import Pt
except ModuleNotFoundError:
    print("[lls-zhouba] 错误: 缺少 python-docx，请先执行 "
          "pip install -r scripts/requirements.txt", file=sys.stderr)
    sys.exit(1)

from lls_jianli_utils_guard import ensure_parent, guard_overwrite, set_cn_font

# Windows 旧控制台默认编码（如 cp936）无法输出“→”时直接抛
# UnicodeEncodeError；能重设就重设为 UTF-8，不能则用 replace 兜底。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ap = argparse.ArgumentParser()
ap.add_argument("json")
ap.add_argument("-o", "--output", required=True)
ap.add_argument("--force", action="store_true")
args = ap.parse_args()

try:
    with open(args.json, encoding="utf-8") as _f:
        data = json.load(_f)
except FileNotFoundError:
    print(f"[lls-zhouba] 错误: 找不到文件: {args.json}", file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"[lls-zhouba] 错误: JSON 解析失败 {args.json}: {e}", file=sys.stderr)
    sys.exit(1)
except OSError as e:
    print(f"[lls-zhouba] 错误: 无法读取文件 {args.json}: {e}", file=sys.stderr)
    sys.exit(1)
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
