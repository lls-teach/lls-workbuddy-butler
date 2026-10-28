"""lls-docx 共享工具：覆盖保护、中文 East-Asia 字体设置。"""
from __future__ import annotations

import os
import sys

CN_FONT = "宋体"
CN_FONT_HEI = "微软雅黑"


def die(msg: str, code: int = 1) -> None:
    print(f"[lls-docx] 错误: {msg}", file=sys.stderr)
    sys.exit(code)


def ensure_parent(path: str) -> str:
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path


def guard_overwrite(path: str, force: bool = False) -> str:
    if not os.path.exists(path) or force:
        return path
    root, ext = os.path.splitext(path)
    alt = f"{root}_new{ext}"
    print(f"[lls-docx] 目标已存在，改写到 {alt}（要覆盖请加 --force）", file=sys.stderr)
    return alt


def set_cn_font(run, name: str = CN_FONT) -> None:
    """python-docx 设置中文字体必须同时设 east-asia 属性。"""
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(
        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts")
    if rfonts is None:
        from docx.oxml.ns import qn
        rfonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rfonts)
    rfonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia", name)
