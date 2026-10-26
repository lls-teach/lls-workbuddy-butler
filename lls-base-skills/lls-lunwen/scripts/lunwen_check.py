#!/usr/bin/env python3
"""投稿前预检：结构完整性 / 图表编号 / GB/T 7714 参考文献 / 格式残留。输出 Markdown 报告。

用法: python3 lunwen_check.py 输入.docx -o 预检报告.md
"""
import argparse
import re

from docx import Document

from lls_lunwen_utils import die, ensure_parent

REF_PAT = re.compile(r"^\[\d+\]\s+.+\[[JMCDEB/OL]+\]", re.S)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()
    try:
        doc = Document(args.input)
    except Exception as e:
        die(f"无法打开: {e}")

    full = "\n".join(p.text for p in doc.paragraphs)
    problems, passed = [], []

    # 1) 结构完整性
    for kw in ("摘要", "Abstract", "关键词", "参考文献"):
        (passed if kw in full else problems).append(f"{'✅' if kw in full else '❌'} 包含「{kw}」")
    nums = [tuple(int(x) for x in m.group(1).split(".")) for p in doc.paragraphs
            if (m := re.match(r"^(\d+(?:\.\d+){0,2})[\s　]", p.text.strip()))]
    if nums:
        for a, b in zip(nums, nums[1:]):
            if len(b) > len(a) + 1 or (len(b) == len(a) and b[-1] - a[-1] > 1):
                problems.append(f"❌ 章节跳级/缺章：{'.'.join(map(str, a))} → {'.'.join(map(str, b))}")
        passed.append(f"✅ 章节序号 {len(nums)} 个，已检查连续性")

    # 2) 图表编号
    figs = re.findall(r"图\s*(\d+-\d+)", full)
    tabs = re.findall(r"表\s*(\d+-\d+)", full)
    dup_f = [x for x in set(figs) if figs.count(x) > 1]
    if dup_f:
        problems.append(f"❌ 图编号重复: {sorted(dup_f)}")
    else:
        passed.append(f"✅ 图编号 {len(figs)} 个无重复（表 {len(tabs)} 个）")

    # 3) 参考文献 GB/T 7714
    ref_zone = full[full.rfind("参考文献"):] if "参考文献" in full else ""
    refs = [l.strip() for l in ref_zone.split("\n") if re.match(r"^\[\d+\]", l.strip())]
    bad_refs = [l[:60] for l in refs if not REF_PAT.match(l)]
    if refs:
        seq = [int(m.group(1)) for l in refs if (m := re.match(r"^\[(\d+)\]", l))]
        if seq != list(range(1, len(seq) + 1)):
            problems.append(f"❌ 参考文献序号不连续: {seq[:20]}")
        else:
            passed.append(f"✅ 参考文献序号 1-{len(seq)} 连续")
        if bad_refs:
            problems.append(f"❌ {len(bad_refs)} 条参考文献缺 GB/T 7714 要素（类型标识[J]/[M]等）: {bad_refs[:3]}")
        else:
            passed.append(f"✅ {len(refs)} 条参考文献均含类型标识")
    else:
        problems.append("❌ 未找到 [1] 式参考文献条目")

    # 4) 格式残留
    wide_spaces = sum(1 for p in doc.paragraphs if p.text.startswith("  ") and not p.text.startswith("　"))
    if wide_spaces:
        problems.append(f"❌ {wide_spaces} 个段落用空格手动缩进（应使用首行缩进样式）")

    lines = ["# 论文投稿预检报告", ""]
    lines += [f"- {p}" for p in passed] + ([f"- {p}" for p in problems] if problems else ["- ✅ 未发现问题项"])
    lines += ["", "> 本报告只覆盖程序可检查项；选题/内容/查重以学校与导师意见为准。"]
    ensure_parent(args.output)
    open(args.output, "w", encoding="utf-8").write("\n".join(lines))
    print(f"[lls-lunwen] 预检完成：通过 {len(passed)} 项，问题 {len(problems)} 项 → {args.output}")
    for p in problems:
        print("  " + p)

main()
