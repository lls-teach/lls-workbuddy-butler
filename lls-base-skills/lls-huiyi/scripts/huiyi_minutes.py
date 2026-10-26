#!/usr/bin/env python3
"""转写稿 → 会议纪要骨架（清洗+分说话人+行动项/决策抽取），议题总结由 AI 补写。

用法: python3 huiyi_minutes.py 转写.txt -o 纪要骨架.md [--title 会议名] [--date 2026-10-27]
输出: 清洗后逐段发言（带说话人）+ 行动项清单 + 决策清单 + 未识别发言提示。
"""
import argparse

from lls_huiyi_utils import clean, ensure_parent, extract_actions, extract_decisions, split_turns

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("-o", "--output", required=True)
ap.add_argument("--title", default="会议纪要")
ap.add_argument("--date", default="")
args = ap.parse_args()

raw = open(args.input, encoding="utf-8", errors="ignore").read()
text = clean(raw)
turns = split_turns(text)
actions = extract_actions(text)
decisions = extract_decisions(text)
unknown = sum(1 for sp, _ in turns if not sp)

out = [f"# {args.title}" + (f"（{args.date}）" if args.date else ""), ""]
out.append("## 一、发言记录（已清洗口头禅；「」内为待 AI 补写的议题归纳位）")
for sp, t in turns:
    prefix = f"**{sp}**：" if sp else "（未标注）"
    out.append(f"- {prefix}{t}")
out += ["", "## 二、行动项（规则抽取，需人工确认负责人与截止时间）"]
out += [f"- [ ] {a}" for a in actions] or ["- （未检出明确行动项）"]
out += ["", "## 三、决策记录"]
out += [f"- {d}" for d in decisions] or ["- （未检出明确决策）"]
if unknown:
    out += ["", f"> ⚠️ {unknown} 句未识别说话人——转写工具导出时请保留说话人前缀，或人工补标。"]
ensure_parent(args.output)
open(args.output, "w", encoding="utf-8").write("\n".join(out))
print(f"[lls-huiyi] 纪要骨架 → {args.output}")
print(f"[lls-huiyi] 发言 {len(turns)} 段（未标注 {unknown}）｜行动项 {len(actions)}｜决策 {len(decisions)}")
print("[lls-huiyi] 下一步：AI 基于骨架写议题归纳与总结，行动项需人工确认负责人/截止时间")
