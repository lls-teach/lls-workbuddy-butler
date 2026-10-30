"""lls-pdf 共享工具：中文字体回退链、页码范围解析、参数辅助。

仅依赖标准库 + 各脚本自身声明的开源依赖（pypdf/pdfplumber/reportlab/pypdfium2）。
"""
from __future__ import annotations

import glob
import os
import re
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
    fonts = find_cjk_fonts()
    return fonts[0] if fonts else None


def find_cjk_fonts() -> list[tuple[str, int]]:
    """按回退链顺序返回全部已存在的中文字体（路径, ttc子字体索引）。

    调用方应逐个尝试注册：排在前面的字体未必能被当前渲染器接受
    （例如 Linux 上常见的 Noto CJK 集合是 CFF 轮廓，reportlab 的
    TTFont 只接受 TrueType 轮廓，注册会失败），跳过失败项继续往后试，
    而不是在第一个候选上直接报错退出。
    """
    found: list[tuple[str, int]] = []
    for pattern in FONT_CANDIDATES:
        for path in glob.glob(pattern):
            if os.path.exists(path):
                # ttc 集合默认取第 0 个子字体；PingFang 用 0（常规体）
                found.append((path, 0))
    return found


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


def ocr_lines(engine, image_path: str) -> list[tuple[str, float]]:
    """兼容 paddleocr 2.x（.ocr(cls=True) 旧格式）与 3.x（predict 新格式），返回 (文本, 置信度) 列表。"""
    try:
        result = engine.ocr(image_path, cls=True)
        return [(b[1][0], float(b[1][1])) for b in (result[0] or [])]
    except TypeError:  # paddleocr 3.x：.ocr() 不再收 cls，改走 predict
        lines: list[tuple[str, float]] = []
        for res in engine.predict(image_path):
            lines.extend(zip(res["rec_texts"], (float(s) for s in res["rec_scores"])))
        return lines


def guard_overwrite(path: str, force: bool = False) -> str:
    """覆盖保护：目标已存在且未加 --force 时，自动改名为 _new 后缀并提示。"""
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
    print(f"[lls-pdf] 目标已存在，改写到 {alt}（要覆盖请加 --force）", file=sys.stderr)
    return alt


def die(msg: str, code: int = 1) -> None:
    print(f"[lls-pdf] 错误: {msg}", file=sys.stderr)
    sys.exit(code)
