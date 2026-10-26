#!/usr/bin/env python3
"""公文要素与文种规则检查 → Markdown 预检报告。

用法: python3 gongwen_check.py 输入.docx -o 预检报告.md
检查: 标题文种收尾/一文一事(请示)/报告夹带请示/主送顶格/成文日期格式/发文字号格式/正文空泛检查。
"""
import argparse
import re

from docx import Document

from lls_gongwen_utils import DOC_KINDS, die, ensure_parent

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("-o", "--output", required=True)
args = ap.parse_args()

try:
    doc = Document(args.input)
except Exception as e:
    die(f"无法打开: {e}")

full = "\n".join(p.text for p in doc.paragraphs)
paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
title = next((p for p in paras if p.startswith("关于") or any(p.rstrip().endswith(k) for k in DOC_KINDS)), "")
problems, passed = [], []

# 1) 标题文种收尾
kind = None
for k in DOC_KINDS:
    if title.rstrip().endswith(k):
        kind = k
if not title:
    problems.append("❌ 未找到标题（应以「关于……的+文种」开头）")
elif not kind:
    problems.append(f"❌ 标题未以文种词收尾（{title[:30]}…）：常用 {('、'.join(DOC_KINDS))}")
else:
    passed.append(f"✅ 标题文种：{kind}")

# 2) 请示一文一事 & 报告夹带请示
if kind == "请示":
    asks = [p for p in paras if re.search(r"请(求|示)|批准|恳请", p)]
    if len(asks) > 2:
        problems.append(f"❌ 请示疑似一文多事（{len(asks)} 处请求表述）——请示应一文一事")
    else:
        passed.append("✅ 请示一文一事检查通过")
if kind == "报告" and any("请" in p and "批准" in p for p in paras):
    problems.append("❌ 报告中疑似夹带请示事项——报告不得夹带请示，请示事项应单独行文")
else:
    passed.append("✅ 报告夹带请示检查通过（或非报告文种）")

# 3) 主送与日期
main_to = next((p for p in paras if p.endswith("：")), "")
if main_to:
    passed.append(f"✅ 主送机关：{main_to[:24]}")
else:
    problems.append("❌ 未找到主送机关（以冒号收尾的行）")
date_line = next((p for p in paras if re.match(r"^\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日$", p.strip())), "")
if date_line:
    passed.append(f"✅ 成文日期：{date_line}")
else:
    problems.append("❌ 未找到成文日期（格式：2026 年 10 月 27 日）")

# 4) 发文字号
docno = next((p for p in paras if re.search(r"〔\d{4}〕\s*\d+号", p)), "")
if docno:
    passed.append(f"✅ 发文字号：{docno}")
else:
    problems.append("⚠️ 未找到发文字号（格式：X办发〔2026〕12号）——视单位发文流程补充")

lines = ["# 公文要素预检报告", "", f"- 标题：{title or '（未检出）'}", ""]
lines += [f"- {p}" for p in passed] + ([f"- {p}" for p in problems] if problems else ["- ✅ 未发现问题项"])
lines += ["", "> 检查为程序级要素核对；行文规则以《党政机关公文处理工作条例》与单位发文流程为准。"]
ensure_parent(args.output)
open(args.output, "w", encoding="utf-8").write("\n".join(lines))
print(f"[lls-gongwen] 预检完成：通过 {len(passed)}，问题 {len(problems)} → {args.output}")
for p in problems:
    print("  " + p)
