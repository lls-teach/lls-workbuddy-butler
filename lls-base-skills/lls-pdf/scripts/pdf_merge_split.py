#!/usr/bin/env python3
"""合并 / 拆分 PDF。

用法:
  合并: python3 pdf_merge_split.py merge -o 合并.pdf a.pdf b.pdf c.pdf
  拆分: python3 pdf_merge_split.py split 输入.pdf -o 输出目录/ --ranges 1-3,5,8-10
        python3 pdf_merge_split.py split 输入.pdf -o 输出目录/ --every 2   （每 2 页一份）
"""
import argparse
import os

from pypdf import PdfReader, PdfWriter

from lls_pdf_utils import die, ensure_parent, ensure_utf8_stdio, guard_overwrite


def _open_reader(path: str, password: str = ""):
    try:
        reader = PdfReader(path)
    except Exception as e:  # noqa: BLE001
        die(f"无法打开 PDF {path}: {e}")
    if reader.is_encrypted and not reader.decrypt(password or ""):
        die(f"{path} 已加密且密码不正确")
    return reader


def do_merge(args: argparse.Namespace) -> None:
    if len(args.inputs) < 2:
        die("merge 至少需要 2 个输入文件")
    writer = PdfWriter()
    for path in args.inputs:
        reader = _open_reader(path, args.password)
        for page in reader.pages:
            writer.add_page(page)
        print(f"[lls-pdf] 已并入 {path}（{len(reader.pages)} 页）")
    out = guard_overwrite(args.output, args.force)
    ensure_parent(out)
    with open(out, "wb") as f:
        writer.write(f)
    print(f"[lls-pdf] 合并完成 → {out}（共 {len(writer.pages)} 页）")


def do_split(args: argparse.Namespace) -> None:
    reader = _open_reader(args.input, args.password)
    total = len(reader.pages)
    ensure_parent(os.path.join(args.output_dir, "_"))
    stem = os.path.splitext(os.path.basename(args.input))[0]

    groups: list[tuple[str, list[int]]]
    if args.ranges:
        groups = []
        for part in args.ranges.split(","):
            part = part.strip()
            try:
                if "-" in part:
                    a, b = part.split("-", 1)
                    pages = list(range(int(a) - 1, int(b)))
                else:
                    pages = [int(part) - 1]
            except ValueError:
                die(f"拆分范围非法: {part}（应为 1-3,5 这样的页码）")
            for p in pages:
                if p < 0 or p >= total:
                    die(f"页码越界: {p + 1}（共 {total} 页）")
            groups.append((f"{stem}_{part.replace('-', '_')}.pdf", pages))
    elif args.every:
        n = args.every
        groups = []
        for start in range(0, total, n):
            chunk = list(range(start, min(start + n, total)))
            groups.append((f"{stem}_p{start + 1}-{chunk[-1] + 1}.pdf", chunk))
    else:
        die("split 需要 --ranges 或 --every 之一")

    for name, pages in groups:
        writer = PdfWriter()
        for p in pages:
            writer.add_page(reader.pages[p])
        out = guard_overwrite(os.path.join(args.output_dir, name), args.force)
        with open(out, "wb") as f:
            writer.write(f)
        print(f"[lls-pdf] → {out}（{len(pages)} 页）")


def main() -> None:
    ap = argparse.ArgumentParser(description="合并/拆分 PDF")
    sub = ap.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("merge")
    m.add_argument("inputs", nargs="+")
    m.add_argument("-o", "--output", required=True)
    m.add_argument("--password", default="")
    m.add_argument("--force", action="store_true")

    s = sub.add_parser("split")
    s.add_argument("input")
    s.add_argument("-o", "--output-dir", required=True)
    s.add_argument("--ranges", help="如 1-3,5,8-10")
    s.add_argument("--every", type=int, help="每 N 页一份")
    s.add_argument("--password", default="")
    s.add_argument("--force", action="store_true")

    args = ap.parse_args()
    ensure_utf8_stdio()
    if args.cmd == "merge":
        do_merge(args)
    else:
        do_split(args)


if __name__ == "__main__":
    main()
