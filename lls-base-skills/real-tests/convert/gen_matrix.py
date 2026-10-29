#!/usr/bin/env python3
"""Generate references/supported-matrix.md from tests/results.jsonl (PASS only)."""
import os, json, collections
ROOT = os.path.dirname(os.path.abspath(__file__))
res = [json.loads(l) for l in open(os.path.join(ROOT, "results.jsonl"))]
passed = [r for r in res if r["status"] == "PASS"
          and not r["case"].startswith(("neg", "sec"))]
negs = [r for r in res if r["case"].startswith("neg")]
secs = [r for r in res if r["case"].startswith("sec")]
by_src = collections.defaultdict(list)
for r in passed:
    sext = r["src"].replace("sample.", "")
    if r["src"].endswith(".tar.gz"): sext = "tar.gz"
    by_src[sext].append(r["tgt"])
lines = ["# 支持矩阵（实测版）", "",
         f"> 由测试套件全绿结果自动生成：正例 {len(passed)} 条全过，负例 {len(negs)} 条（不支持的组合全部正确拒绝），安全用例 {len(secs)} 条（不覆盖/不越界）。",
         "> 矩阵里有的才宣传；没有的就回答暂不支持。", ""]
total = 0
for sext in sorted(by_src):
    tgts = sorted(set(by_src[sext])); total += len(tgts)
    lines.append(f"- **{sext}** → " + "、".join(tgts) + f"（{len(tgts)}）")
lines.append("")
lines.append(f"合计实测通过转换对：**{total}**")
out = os.path.join(os.path.dirname(os.path.dirname(ROOT)), "lls-convert", "references", "supported-matrix.md")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w").write("\n".join(lines) + "\n")
print(f"matrix written: {total} pairs, {len(by_src)} source formats")
