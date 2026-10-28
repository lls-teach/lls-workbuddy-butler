#!/usr/bin/env python3
"""批量编辑已有工作簿：改单元格 / 追加行 / 追加列。默认不改原文件（输出 _new）。

用法:
  改单元格: python3 xlsx_edit.py 表.xlsx --set "Sheet1!B2=已审核" --set "Sheet1!C2=100" -o 新表.xlsx
  追加一行: python3 xlsx_edit.py 表.xlsx --append-sheet Sheet1 --row-json '["张三","市场部",3000]' -o 新表.xlsx
  加公式列: python3 xlsx_edit.py 表.xlsx --set "Sheet1!E1=小计" --set "Sheet1!E2=C2+D2" -o 新表.xlsx
"""
import argparse
import json

from openpyxl import load_workbook

from lls_xlsx_utils import die, ensure_parent, guard_overwrite


def parse_cell_ref(ref: str) -> tuple[str, int, int, str]:
    """'Sheet1!B2=值' → (sheet, row, col, value)"""
    if "!" not in ref or "=" not in ref:
        die(f'格式非法: {ref!r}，应为 "表名!单元格=值"')
    ref_part, value = ref.split("=", 1)
    sheet, cell = ref_part.split("!", 1)
    col_letters = "".join(ch for ch in cell if ch.isalpha())
    digits = "".join(ch for ch in cell if ch.isdigit())
    if not col_letters or not digits:
        die(f"单元格地址非法: {cell!r}")
    col = 0
    for ch in col_letters.upper():
        col = col * 26 + (ord(ch) - 64)
    return sheet, int(digits), col, value


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--set", dest="sets", action="append", default=[], help='表!单元格=值，可多次')
    ap.add_argument("--append-sheet", help="向该表追加行")
    ap.add_argument("--row-json", help='追加的行: ["a","b",1]（配合 --append-sheet）')
    ap.add_argument("-o", "--output", required=True, help="输出文件（不会改动原文件）")
    ap.add_argument("--password", default="")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    try:
        wb = load_workbook(args.input)
    except Exception as e:  # noqa: BLE001
        die(f"无法打开: {e}")

    if args.sets:
        for ref in args.sets:
            sheet, row, col, value = parse_cell_ref(ref)
            if sheet not in wb.sheetnames:
                die(f"工作表 {sheet!r} 不存在，可选: {wb.sheetnames}")
            wb[sheet].cell(row=row, column=col, value=value)
            cell_addr = ref.split("=", 1)[0].split("!", 1)[1]
            print(f"[lls-xlsx] {sheet}!{cell_addr} ← {value!r}")

    if args.append_sheet:
        if args.append_sheet not in wb.sheetnames:
            die(f"工作表 {args.append_sheet!r} 不存在，可选: {wb.sheetnames}")
        if not args.row_json:
            die("--append-sheet 需要 --row-json")
        row = json.loads(args.row_json)
        ws = wb[args.append_sheet]
        ws.append(row)
        print(f"[lls-xlsx] {args.append_sheet} 追加 1 行: {row}")

    if not args.sets and not args.append_sheet:
        die("至少给一个 --set 或 --append-sheet/--row-json")

    out = guard_overwrite(args.output, args.force)
    ensure_parent(out)
    wb.save(out)
    print(f"[lls-xlsx] 已保存 → {out}（原文件未动: {args.input}）")


if __name__ == "__main__":
    main()
