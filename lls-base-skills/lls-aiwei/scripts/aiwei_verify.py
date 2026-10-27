#!/usr/bin/env python3
"""改写前后对比验收：密度下降幅度 + 字数变化 + 残留清单。改丢内容 = 不合格。

用法: python3 aiwei_verify.py 原文.md 改写版.md
合格线: 密度下降 ≥50%，字数变化 ≤±20%，残留命中 ≤3。
"""
import sys

from lls_aiwei_utils import (WORD_BANK, WORD_PATTERNS, abstract_hits,
                             length_uniformity, parallel_hits, sentences,
                             summary_hits)

def density(text: str) -> float:
    chars = max(len(text.replace(" ", "").replace("\n", "")), 1) / 1000
    word_score = sum(len(p.findall(text)) for p in WORD_PATTERNS.values())
    struct_score = len(parallel_hits(text)) * 2 + len(summary_hits(text)) * 2 + len(abstract_hits(text)) * 2
    return (word_score + struct_score) / chars

def main() -> None:
    argv = [a for a in sys.argv[1:] if a != "--allow-length"]
    allow_len = "--allow-length" in sys.argv[1:]
    old = open(argv[0], encoding="utf-8", errors="ignore").read() if len(argv) > 0 else ""
    new = open(argv[1], encoding="utf-8", errors="ignore").read() if len(argv) > 1 else ""
    if not old or not new:
        print("[lls-aiwei] 用法: aiwei_verify.py 原文.md 改写版.md")
        sys.exit(1)

    d_old, d_new = density(old), density(new)
    drop = (d_old - d_new) / d_old * 100 if d_old else 0
    len_old, len_new = len(old.replace(" ", "").replace("\n", "")), len(new.replace(" ", "").replace("\n", ""))
    len_delta = (len_new - len_old) / len_old * 100 if len_old else 0

    residue = []
    for w, pat in WORD_PATTERNS.items():
        n = len(pat.findall(new))
        if n:
            residue.append((w, n))
    residue.sort(key=lambda kv: -kv[1])

    verdict_ok = drop >= 50 and abs(len_delta) <= 20 and len(residue) <= 3
    print(f"[lls-aiwei] 密度：{d_old:.1f} → {d_new:.1f}（下降 {drop:.0f}%）")
    print(f"[lls-aiwei] 字数：{len_old} → {len_new}（{len_delta:+.0f}%，合格线 ±20%）")
    if residue:
        print(f"[lls-aiwei] 残留 AI 味词 {len(residue)} 个：" + "、".join(f"{w}×{n}" for w, n in residue[:6]))
    if verdict_ok:
        print("[lls-aiwei] ✅ 验收通过")
    else:
        why = []
        if drop < 50: why.append("密度下降不足 50%")
        if abs(len_delta) > 20 and not allow_len:
            why.append("字数变化超 ±20%（疑似改丢内容或过度发挥）——重度去味文本自然缩水属正常，确认无丢失后可加 --allow-length 放行")
        if len(residue) > 3: why.append("残留命中过多")
        print(f"[lls-aiwei] ❌ 验收不通过：{'；'.join(why)}")
        sys.exit(1)

main()
