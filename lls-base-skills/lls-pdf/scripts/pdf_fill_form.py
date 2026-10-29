#!/usr/bin/env python3
"""填写 AcroForm 表单字段（pypdf），字段值来自 JSON。

用法:
  1) 先列出可填字段: python3 pdf_fill_form.py 表单.pdf --list
  2) 填写: python3 pdf_fill_form.py 表单.pdf --data 字段.json -o 已填.pdf
字段 JSON: {"姓名": "张三"} 或 {"fullname": "张三"}（键=字段名，精确或双向包含匹配）
"""
import argparse
import json
import sys

from pypdf import PdfReader, PdfWriter

from lls_pdf_utils import die, ensure_parent, ensure_utf8_stdio, guard_overwrite


def main() -> None:
    ap = argparse.ArgumentParser(description="填写 AcroForm 表单")
    ap.add_argument("input")
    ap.add_argument("--data", help="字段 JSON 文件")
    ap.add_argument("--list", action="store_true", help="仅列出可填字段")
    ap.add_argument("-o", "--output")
    ap.add_argument("--password", default="")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    ensure_utf8_stdio()
    try:
        reader = PdfReader(args.input)
    except Exception as e:  # noqa: BLE001
        die(f"无法打开 PDF {args.input}: {e}")
    if reader.is_encrypted and not reader.decrypt(args.password or ""):
        die("PDF 已加密且密码不正确")

    fields = reader.get_fields() or {}
    if args.list or not fields:
        print(f"[lls-pdf] 可填字段 {len(fields)} 个:")
        for k, v in fields.items():
            print(f"  - {k}  (类型 {v.get('/FT')}, 当前值 {v.get('/V')!r})")
        if not fields and not args.list:
            die("该 PDF 没有 AcroForm 表单字段。若为纸质表格扫描件，请走 OCR 路线或人工处理。")
        return

    if not args.data or not args.output:
        die("填写模式需要 --data 与 -o（列出字段用 --list）")
    try:
        with open(args.data, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        die(f"无法读取字段 JSON {args.data}: {e}")

    def match_key(field: str) -> str | None:
        if field in data:
            return field
        for k in data:
            if k in field or field in k:
                return k
        return None

    writer = PdfWriter()
    writer.append(reader)

    filled: dict[str, str] = {}
    failed: list[tuple[str, str]] = []
    for field in fields:
        key = match_key(field)
        if key is None:
            continue
        value = str(data[key])
        try:
            for page in writer.pages:
                writer.update_page_form_field_values(page, {field: value}, auto_regenerate=False)
            filled[field] = value
        except Exception as e:  # noqa: BLE001
            failed.append((field, str(e)))

    out = guard_overwrite(args.output, args.force)
    ensure_parent(out)
    with open(out, "wb") as f:
        writer.write(f)

    print(f"[lls-pdf] 已填写 {len(filled)}/{len(data)} 个字段 → {out}")
    for k, v in filled.items():
        print(f"  {k} = {v}")
    if failed:
        print("[lls-pdf] ⚠️ 写入失败的字段:", failed, file=sys.stderr)
    leftover = [k for k in data if k not in {match_key(f) for f in filled}]
    if leftover:
        print(f"[lls-pdf] ⚠️ JSON 中这些键未匹配到表单字段: {leftover}（用 --list 核对字段名）")
    no_value = [f for f in fields if match_key(f) is None]
    if no_value:
        print(f"[lls-pdf] ℹ️ 表单中未提供值的字段: {no_value}")


if __name__ == "__main__":
    main()
