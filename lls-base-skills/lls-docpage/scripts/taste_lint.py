#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""taste 文案 lint：扫描 PPT 文案中的陈词与 stock 结尾。纯标准库，零依赖。
输出分级：[FAIL] banned 词 / [WARN] warned 词 / [PASS] 通过。
FAIL 全修；WARN 修掉或写一句话辩护进交付报告。

用法：
    python scripts/taste_lint.py --text slides.txt      # 扫描纯文本（一页一行或全文）
    python scripts/taste_lint.py --scan-js build.mjs    # 扫描构建脚本中的字符串
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEXICON = os.path.join(HERE, "..", "references", "taste-copy-tells.json")


def load_lexicon():
    with open(LEXICON, encoding="utf-8") as f:
        return json.load(f)


def extract_js_strings(path):
    with open(path, encoding="utf-8") as f:
        src = f.read()
    # 取双引号/单引号/模板字符串中的中文片段
    parts = re.findall(r'"([^"\n]{2,})"|\'([^\'\n]{2,})\'|`([^`]{2,})`', src)
    texts = []
    for g in parts:
        s = next(x for x in g if x)
        if re.search(r'[\u4e00-\u9fff]', s):
            texts.append(s)
    return texts


def lint_texts(texts, lex):
    fails, warns = [], []
    for i, t in enumerate(texts, 1):
        for w in lex["banned"]:
            c = t.count(w)
            if c:
                fails.append((i, w, c))
        for w in lex["warned"]:
            c = t.count(w)
            if c:
                warns.append((i, w, c))
    return fails, warns


def main(argv=None):
    ap = argparse.ArgumentParser(description="taste 文案 lint")
    ap.add_argument("--text", default=None, help="纯文本文件路径")
    ap.add_argument("--scan-js", default=None, help="构建脚本路径，扫描其中字符串")
    args = ap.parse_args(argv)
    if not args.text and not args.scan_js:
        ap.error("需要 --text 或 --scan-js")

    lex = load_lexicon()
    if args.scan_js:
        texts = extract_js_strings(args.scan_js)
    else:
        with open(args.text, encoding="utf-8") as f:
            texts = [ln.strip() for ln in f if ln.strip()]

    fails, warns = lint_texts(texts, lex)
    for i, w, c in fails:
        print("[FAIL] banned 词“%s”出现 %d 次（第 %d 段）" % (w, c, i))
    for i, w, c in warns:
        print("[WARN] warned 词“%s”出现 %d 次（第 %d 段），需删掉或一句话辩护" % (w, c, i))
    if not fails and not warns:
        print("[PASS] 文案检查通过")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
