#!/usr/bin/env python3
"""字幕清洗：口头禅删除 + 错别字替换表 + 连续重复行去重（时间轴不动）。

用法:
  python3 zimu_clean.py 字幕.srt -o 修正.srt
  python3 zimu_clean.py 字幕.srt -o 修正.srt --map 替换.json    # {"错词":"对词",...}
  python3 zimu_clean.py 字幕.srt -o 修正.srt --no-fillers --no-typos --no-dedupe
"""
import argparse
import json
import os

from lls_zimu_utils import clean_text, die, ensure_parent, parse_srt, write_srt


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--map", help="替换表 JSON（键=错词 值=对词）")
    ap.add_argument("--no-fillers", action="store_true", help="关闭口头禅删除")
    ap.add_argument("--no-typos", action="store_true", help="关闭错别字替换（--map 不生效）")
    ap.add_argument("--no-dedupe", action="store_true", help="关闭连续重复行去重")
    args = ap.parse_args(argv)

    # 铁律：禁止覆盖原 SRT，输出一律写新文件。
    if os.path.abspath(args.output) == os.path.abspath(args.input):
        die("输出路径与输入 SRT 相同，拒绝覆盖原文件，请换一个新输出文件")

    do_fillers = not args.no_fillers
    do_typos = not args.no_typos
    if args.no_typos and args.map:
        print("[lls-zimu] ⚠️ 已关闭错别字替换，--map 本次被忽略")
    replacements = None
    if do_typos and args.map:
        try:
            with open(args.map, encoding="utf-8-sig") as f:
                replacements = json.load(f)
        except FileNotFoundError:
            die(f"替换表不存在：{args.map}")
        except json.JSONDecodeError as e:
            die(f"替换表不是合法 JSON：{args.map}（{e}）")
        except OSError as e:
            die(f"替换表无法读取：{args.map}（{e}）")
        if not isinstance(replacements, dict):
            die(f"替换表须为 JSON 对象（键=错词 值=对词）：{args.map}")

    try:
        with open(args.input, encoding="utf-8-sig", errors="ignore") as f:
            text = f.read()
    except FileNotFoundError:
        die(f"输入文件不存在：{args.input}")
    except OSError as e:
        die(f"输入文件无法读取：{args.input}（{e}）")
    blocks, _ = parse_srt(text)
    if not blocks:
        print("[lls-zimu] ❌ 无字幕块")
        return 1

    dedupe = not args.no_dedupe
    filler_n = rep_n = dedupe_n = 0
    kept_blocks = []
    prev = None
    for b in blocks:
        new, fn, rn = clean_text(b["text"], replacements, do_fillers=do_fillers, do_typos=do_typos)
        b["text"], filler_n, rep_n = new, filler_n + fn, rep_n + rn
        # 去重是真删块：重复块不进输出列表；被删块不更新 prev，
        # 这样 A A A 三连重复能连续删掉后两块，而不是只删一块。
        if dedupe and prev is not None and b["text"] and b["text"] == prev:
            dedupe_n += 1
            continue
        kept_blocks.append(b)
        prev = b["text"]

    ensure_parent(args.output)
    write_srt(kept_blocks, args.output)
    empty_kept = sum(1 for b in kept_blocks if not b["text"])
    print(f"[lls-zimu] 清洗完成 → {args.output}")
    print(f"[lls-zimu] 口头禅删除 {filler_n} 处 ｜ 替换 {rep_n} 处 ｜ 连续重复去重 {dedupe_n} 块 ｜ 保留 {len(kept_blocks)}/{len(blocks)} 块")
    if empty_kept:
        print(f"[lls-zimu] ⚠️ 清洗后空文本块 {empty_kept} 块（仅口头禅的块会留空，不自动删块，体检会列出）")
    print("[lls-zimu] ⚠️ 替换表请人工过目——字幕纠错以不改变原意为底线")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
