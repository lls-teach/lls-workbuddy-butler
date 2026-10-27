#!/usr/bin/env python3
"""AI 味检测报告：词级命中 / 句级结构特征 / AI 味密度（每千字得分）。

用法: python3 aiwei_scan.py 文本.md [-o 报告.md]
密度口径: (词级命中×1 + 排比×2 + 总结腔×2 + 抽象堆叠×2) / 千字
        <3 干净 ｜ 3-8 轻度 ｜ 8-15 中度 ｜ >15 重度
"""
import argparse

from lls_aiwei_utils import (WORD_BANK, WORD_PATTERNS, abstract_hits, die,
                             ensure_parent, length_uniformity, parallel_hits,
                             sentences, summary_hits)

ap = argparse.ArgumentParser()
ap.add_argument("input")
ap.add_argument("-o", "--output")
args = ap.parse_args()

text = open(args.input, encoding="utf-8", errors="ignore").read()
chars = len(re.sub(r"\s", "", text)) if (re := __import__("re")) else 0
if chars == 0:
    die("文本为空")

kilo = max(chars / 1000, 0.1)

# 词级
word_hits = []
for w, pat in WORD_PATTERNS.items():
    n = len(pat.findall(text))
    if n:
        word_hits.append((w, n, WORD_BANK[w]))
word_hits.sort(key=lambda kv: -kv[1])
word_score = sum(n for _, n, _ in word_hits)

# 句级
para = parallel_hits(text)
summ = summary_hits(text)
abst = abstract_hits(text)
struct_score = len(para) * 2 + len(summ) * 2 + len(abst) * 2

density = (word_score + struct_score) / kilo
level = "干净" if density < 3 else "轻度" if density < 8 else "中度" if density < 15 else "重度"

uni = length_uniformity(text)

lines = [f"# AI 味检测报告：{args.input}", "",
         f"- 字数：{chars} ｜ **AI 味密度：{density:.1f}/千字（{level}）**"]
if uni is not None:
    lines.append(f"- ⚠️ 检测到连续 5 句句长几乎一致（变异系数 {uni}）——典型的 AI 均匀句长，改写时故意打破：有的句子 5 个字，有的句子拖到二十多个字。")
lines.append("")
lines.append("## 词级命中（词 → 次数 → 改写方向）")
if word_hits:
    lines += [f"- 「{w}」×{n} → {direction}" for w, n, direction in word_hits]
else:
    lines.append("- 无")
lines.append("")
lines.append("## 句级结构特征")
if para:
    lines.append(f"- 🔁 排比三连 {len(para)} 处（例：{para[0][:50]}…）→ 打破整齐感，长短句交错")
if summ:
    lines.append(f"- 🧾 总结腔 {len(summ)} 处（{[s[:24] for s in summ[:3]]}）→ 段尾总结句删一半，留给读者自己品")
if abst:
    lines.append(f"- 🏗️ 抽象名词堆叠 {len(abst)} 处（{abst[:5]}）→ 换成具体的人/物/动作")
if not para and not summ and not abst:
    lines.append("- 无")
lines.append("")
lines.append("## 改写优先级")
lines.append("1. 先清词级命中（机械替换，见效最快）")
lines.append("2. 再拆排比与总结腔（重写句子结构）")
lines.append("3. 最后打破句长均匀（读一遍，凭语感长短交错）")
lines.append("4. 改完用 aiwei_verify.py 前后对比，密度应显著下降且字数变化 <±20%（防改丢内容）")

if args.output:
    ensure_parent(args.output)
    open(args.output, "w", encoding="utf-8").write("\n".join(lines))
    print(f"[lls-aiwei] 检测报告 → {args.output}（密度 {density:.1f}/千字，{level}）")
else:
    print("\n".join(lines))
