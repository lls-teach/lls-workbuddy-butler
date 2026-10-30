"""lls-xlsx 共享工具：覆盖保护、CSV 编码探测、中文列宽。"""
from __future__ import annotations

import os
import re
import sys


def die(msg: str, code: int = 1) -> None:
    print(f"[lls-xlsx] 错误: {msg}", file=sys.stderr)
    sys.exit(code)


def ensure_parent(path: str) -> str:
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path


def guard_overwrite(path: str, force: bool = False) -> str:
    # Windows 保留字符/设备名要到保存阶段才报裸 OSError，这里提前给出可读错误
    name = os.path.basename(path)
    if os.name == "nt" and (
        re.search(r'[<>:"|?*]', name)
        or re.fullmatch(r"(?i)(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", name)
    ):
        die(f"输出文件名含 Windows 保留字符或设备名，请改名后重试：{name}")
    if not os.path.exists(path) or force:
        return path
    root, ext = os.path.splitext(path)
    alt = f"{root}_new{ext}"
    print(f"[lls-xlsx] 目标已存在，改写到 {alt}（要覆盖请加 --force）", file=sys.stderr)
    return alt


def cjk_width(s: str) -> int:
    """显示宽度：CJK 记 2，其余记 1。"""
    return sum(2 if ord(ch) > 0x2E7F else 1 for ch in str(s))


def smart_read_csv(path: str) -> list[list[str]]:
    """按 utf-8-sig → utf-8 → gbk 顺序尝试读取 CSV。"""
    for enc in ("utf-8-sig", "utf-8", "gbk"):
        try:
            import csv
            with open(path, encoding=enc, newline="") as f:
                return [list(r) for r in csv.reader(f)]
        except UnicodeDecodeError:
            continue
    die(f"CSV 编码无法识别（试过 utf-8/gbk）: {path}")
    return []
