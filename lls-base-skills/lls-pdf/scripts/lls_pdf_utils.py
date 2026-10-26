"""lls-pdf 共享工具：中文字体回退链、页码范围解析、参数辅助。

仅依赖标准库 + 各脚本自身声明的开源依赖（pypdf/pdfplumber/reportlab/pypdfium2）。
"""
from __future__ import annotations

import glob
import os
import sys

# 中文字体回退链：macOS → Windows → Linux 常见 CJK 字体
FONT_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simsun.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
]


def find_cjk_font() -> tuple[str, int] | None:
    """返回 (字体路径, ttc子字体索引)；找不到返回 None。"""
    for pattern in FONT_CANDIDATES:
        for path in glob.glob(pattern):
            if os.path.exists(path):
                # ttc 集合默认取第 0 个子字体；PingFang 用 0（常规体）
                idx = 0
                return path, idx
    return None


def parse_page_range(spec: str | None, total: int) -> list[int]:
    """把 '1-3,5,8-10' 解析成页索引列表（0 基）。spec 为 None 时返回全部页。"""
    if not spec:
        return list(range(total))
    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            start, end = int(a) - 1, int(b)  # 含端点
            if start < 0 or end > total or start >= end:
                raise ValueError(f"页码范围非法: {part}（文档共 {total} 页）")
            pages.extend(range(start, end))
        else:
            i = int(part) - 1
            if i < 0 or i >= total:
                raise ValueError(f"页码越界: {part}（文档共 {total} 页）")
            pages.append(i)
    return sorted(set(pages))


def ensure_parent(path: str) -> str:
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path


def guard_overwrite(path: str, force: bool = False) -> str:
    """覆盖保护：目标已存在且未加 --force 时，自动改名为 _new 后缀并提示。"""
    if not os.path.exists(path) or force:
        return path
    root, ext = os.path.splitext(path)
    alt = f"{root}_new{ext}"
    print(f"[lls-pdf] 目标已存在，改写到 {alt}（要覆盖请加 --force）", file=sys.stderr)
    return alt


def die(msg: str, code: int = 1) -> None:
    print(f"[lls-pdf] 错误: {msg}", file=sys.stderr)
    sys.exit(code)
