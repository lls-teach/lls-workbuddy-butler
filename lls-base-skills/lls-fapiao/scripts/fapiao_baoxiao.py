#!/usr/bin/env python3
"""从批量解析的 JSONL 生成报销单 Excel（分组、SUM 公式、中文列宽、问题标注列）。

用法:
  python3 fapiao_baoxiao.py 汇总.jsonl -o 报销单.xlsx [--by owner|kind|none] [--title Q4报销]
列: 序号/报销人/发票号码/开票日期/类型/金额(元)/待人工核对/问题
末行: 合计（SUM 公式）；"待人工核对"非空的行整行黄底标注。
"""
import argparse
import json

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from lls_fapiao_utils import ensure_parent, guard_overwrite, cjk_width

HEADERS = ["序号", "报销人", "发票号码", "开票日期", "类型", "金额(元)", "待人工核对", "问题"]
WIDTHS = [6, 10, 24, 12, 14, 12, 14, 34]
YELLOW = PatternFill("solid", fgColor="FFF3CD")


def cjk_w(s: str) -> int:
    return sum(2 if ord(ch) > 0x2E7F else 1 for ch in str(s))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--by", choices=["owner", "kind", "none"], default="owner", help="排序方式")
    ap.add_argument("--title", default="报销明细")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    records = [json.loads(l) for l in open(args.jsonl, encoding="utf-8") if l.strip()]
    if not records:
        print("[lls-fapiao] 输入为空，未生成文件")
        return
    if args.by == "owner":
        records.sort(key=lambda r: (r.get("owner", ""), str(r.get("date", {}).get("value") or "")))
    elif args.by == "kind":
        records.sort(key=lambda r: str((r.get("kind") or {}).get("value") or ""))

    wb = Workbook()
    ws = wb.active
    ws.title = args.title or "报销明细"
    ws.append(HEADERS)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F6FEB")
        c.alignment = Alignment(horizontal="center")

    ridx = 1
    flagged = 0
    total = 0.0
    for r in records:
        if "error" in r:
            continue
        fields = r.get("fields") or r
        no = (r.get("invoice_no") or fields.get("invoice_no", {}) or {}).get("value", "")
        date = (r.get("date") or fields.get("date", {}) or {}).get("value", "")
        amount = (r.get("total") or fields.get("total", {}) or {}).get("value")
        kind = (r.get("kind") or fields.get("kind", {}) or {}).get("value", "未识别")
        owner = r.get("owner", "")
        manual = r.get("manual_review", [])
        problems = r.get("problems", [])
        ridx += 1
        ws.append([ridx - 1, owner, no, date, kind, amount, "、".join(manual) or "", "；".join(problems) or ""])
        if amount:
            total += amount
        if manual or problems:
            flagged += 1
            for c in ws[ridx]:
                c.fill = YELLOW

    # 合计行
    ridx += 1
    ws.cell(row=ridx, column=1, value="合计")
    ws.cell(row=ridx, column=6, value=f"=SUM(F2:F{ridx - 1})")
    ws.cell(row=ridx, column=1).font = Font(bold=True)
    ws.cell(row=ridx, column=6).font = Font(bold=True)

    # 中文列宽
    for i, w in enumerate(WIDTHS, 1):
        measured = max((cjk_w(cell.value) for cell in ws[get_column_letter(i)] if cell.value is not None), default=w)
        ws.column_dimensions[get_column_letter(i)].width = min(max(measured + 2, w), 42)

    out = guard_overwrite(args.output, args.force)
    ensure_parent(out)
    wb.save(out)
    print(f"[lls-fapiao] 报销单已生成 → {out}")
    print(f"[lls-fapiao] 明细 {ridx - 2} 笔 · 合计 {total:.2f} 元（公式 F{ridx}）· 黄底待核对 {flagged} 笔")


if __name__ == "__main__":
    main()
