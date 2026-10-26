#!/usr/bin/env python3
"""解析单张发票文本 → 结构化 JSON（字段 + 置信度 + 校验问题）。

用法:
  python3 fapiao_parse.py 发票.txt -o 发票.json
  cat 发票文本 | python3 fapiao_parse.py - -o 发票.json
字段: invoice_no / date / total / buyer / kind，每个字段带 confidence；
confidence < 0.85 的字段在 "manual_review" 列表里标"待人工核对"。
"""
import argparse
import json
import sys

from lls_fapiao_utils import die, first_match, norm_date, to_amount


def parse_invoice_text(text: str) -> dict:
    inv: dict = {}
    for field in ("invoice_no", "date", "total", "buyer", "kind"):
        value, conf = first_match(text, field)
        if field == "date":
            value = norm_date(value)
        if field == "total":
            value = to_amount(value)
        if field == "kind":
            value = value or "未识别"
            conf = 0.95 if value != "未识别" else 0.5
        inv[field] = {"value": value, "confidence": conf}

    problems = []
    no = inv["invoice_no"]["value"]
    if no:
        if len(no) not in (8, 10, 20):
            problems.append(f"发票号码长度 {len(no)} 位，不在白名单 {{8,10,20}}（数电票为 20 位）")
    else:
        problems.append("未找到发票号码")
    total = inv["total"]["value"]
    if total is None:
        problems.append("未找到价税合计（小写）金额")
    elif total <= 0:
        problems.append(f"金额异常: {total}")

    manual = [f for f in ("invoice_no", "date", "total", "buyer") if inv[f]["value"] and inv[f]["confidence"] < 0.85]
    return {"fields": inv, "manual_review": manual, "problems": problems}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="发票文本文件，或 '-' 读 stdin")
    ap.add_argument("-o", "--output", help="输出 JSON（缺省打印 stdout）")
    args = ap.parse_args()

    text = sys.stdin.read() if args.input == "-" else (open(args.input, encoding="utf-8", errors="ignore").read() if args.input else "")
    if not text.strip():
        die("输入文本为空")
    result = parse_invoice_text(text)
    out = json.dumps(result, ensure_ascii=False, indent=1)
    if args.output:
        from lls_fapiao_utils import ensure_parent
        ensure_parent(args.output)
        open(args.output, "w", encoding="utf-8").write(out)
        print(f"[lls-fapiao] 解析完成 → {args.output}（manual_review: {len(result['manual_review'])} 字段待人工核对）")
    else:
        print(out)


if __name__ == "__main__":
    main()
