#!/usr/bin/env python3
"""脚本 vs 实录字幕 对齐：找出念错/漏念/加词（koushuo 闭环）。

用法: python3 zimu_diff.py 脚本.md 字幕.srt -o 偏差报告.md
脚本支持任意 md（拼接全部文本比对）。
"""
import argparse
import os

from lls_zimu_utils import align_script, die, ensure_parent, parse_srt


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("srt")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args(argv)

    # 输出一律写新文件，不覆盖脚本或字幕原文件。
    for _src in (args.script, args.srt):
        if os.path.abspath(args.output) == os.path.abspath(_src):
            die(f"输出路径与输入文件相同，拒绝覆盖：{_src}，请换一个新输出文件")

    try:
        with open(args.script, encoding="utf-8-sig", errors="ignore") as f:
            script = f.read()
    except FileNotFoundError:
        die(f"脚本文件不存在：{args.script}")
    except OSError as e:
        die(f"脚本文件无法读取：{args.script}（{e}）")
    try:
        with open(args.srt, encoding="utf-8-sig", errors="ignore") as f:
            srt_text = f.read()
    except FileNotFoundError:
        die(f"字幕文件不存在：{args.srt}")
    except OSError as e:
        die(f"字幕文件无法读取：{args.srt}（{e}）")
    blocks, _ = parse_srt(srt_text)
    subs = [b["text"] for b in blocks]

    diff = align_script(script, subs)
    change = [d for d in diff if d[0] in ("改", "漏", "增")]

    lines = ["# 实录 vs 脚本 偏差报告", "",
             f"- 对齐方式：字符级 difflib ｜ 偏差 {len(change)} 处", "",
             "| 操作 | 脚本 | 实录 |", "|---|---|---|"]
    for op, a, b in change[:30]:
        lines.append(f"| {op} | {a[:24]} | {b[:24]} |")
    if not change:
        lines.append("- ✅ 无显著偏差（口播还原度 100%）")
    lines += ["", "> 用途：偏差大的段落=口播不熟，重录或下次重点练习。"]
    ensure_parent(args.output)
    open(args.output, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print(f"[lls-zimu] 偏差 {len(change)} 处 → {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
