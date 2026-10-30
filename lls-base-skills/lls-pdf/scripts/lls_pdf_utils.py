"""lls-pdf 共享工具：中文字体回退链、页码范围解析、参数辅助。

仅依赖标准库 + 各脚本自身声明的开源依赖（pypdf/pdfplumber/reportlab/pypdfium2）。
"""
from __future__ import annotations

import glob
import os
import sys

# 中文字体回退链：TrueType 轮廓的候选在前，CFF（PostScript）轮廓的在后。
# 原因：reportlab 的 TTFont 只支持 TrueType 轮廓，遇到 CFF 字体（如 Linux
# 发行版常见的 NotoSansCJK-Regular.ttc OTF 版）会报 "postscript outlines
# are not supported"。调用方必须逐个尝试注册、失败跳过下一个，不能只取
# 第一个存在的文件就认定可用。macOS / Windows / Linux 路径按存在性过滤，
# 不存在的路径在任何平台上都会被 glob 跳过，因此这份表本身是跨平台的。
# 另支持环境变量 LLS_CJK_FONT 指向单个字体文件（优先于全部候选）。
FONT_CANDIDATES = [
    # Windows 自带 TrueType 字体（Windows 下 glob 对大小写不敏感）
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simsun.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    # Linux TrueType 字体：文泉驿（TrueType TTC）、Noto Sans SC 的 TTF 版
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansSC-Regular.ttf",
    "/usr/share/fonts/**/NotoSansSC*.ttf",
    "/usr/share/fonts/**/wqy-zenhei.ttc",
    os.path.expanduser("~/.fonts/**/NotoSansSC*.ttf"),
    os.path.expanduser("~/.local/share/fonts/**/NotoSansSC*.ttf"),
    # macOS 字体
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    # CFF 轮廓的 Noto CJK（Linux 常见，但 reportlab 无法注册，仅作最后尝试）
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
]


def cjk_font_candidates() -> list[tuple[str, int]]:
    """展开后的去重候选列表，每项为 (字体路径, ttc 子字体索引)。

    环境变量 LLS_CJK_FONT 指定的文件排在最前。glob 模式先 expanduser /
    expandvars 再展开，Windows 的 %LOCALAPPDATA% 风格路径也能用。
    """
    seen: set[str] = set()
    ordered: list[str] = []
    env_font = os.environ.get("LLS_CJK_FONT", "").strip()
    if env_font:
        ordered.append(env_font)
    for pattern in FONT_CANDIDATES:
        pattern = os.path.expanduser(os.path.expandvars(pattern))
        for path in sorted(glob.glob(pattern, recursive=True)):
            if os.path.isfile(path) and path not in seen:
                seen.add(path)
                ordered.append(path)
    # ttc 集合默认取第 0 个子字体；PingFang 用 0（常规体）
    return [(path, 0) for path in ordered]


def find_cjk_font() -> tuple[str, int] | None:
    """返回第一个存在的 (字体路径, ttc 子字体索引)；找不到返回 None。

    注意：存在 ≠ reportlab 可注册（CFF 字体会注册失败）。pdf_create 不
    直接用本函数定生死，而是逐个尝试注册，见 pdf_create.register_cjk_font。
    """
    candidates = cjk_font_candidates()
    return candidates[0] if candidates else None


def ensure_utf8_stdio() -> None:
    """把 stdout/stderr 切到 UTF-8（失败则静默跳过）。

    Windows 控制台默认编码常为 GBK，直接 print ✅/⚠️/ℹ️ 等字符会抛
    UnicodeEncodeError 导致脚本在干完活后崩溃。Linux/macOS 下本就
    是 UTF-8，此调用无实际影响。
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass


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
    """覆盖保护：目标已存在且未加 --force 时，自动改名并提示。

    改名会递增后缀（_new、_new2、_new3……），避免第二次重复运行
    静默覆盖上一次的 _new 文件。
    """
    if not os.path.exists(path) or force:
        return path
    root, ext = os.path.splitext(path)
    alt = f"{root}_new{ext}"
    n = 2
    while os.path.exists(alt):
        alt = f"{root}_new{n}{ext}"
        n += 1
    print(f"[lls-pdf] 目标已存在，改写到 {alt}（要覆盖请加 --force）", file=sys.stderr)
    return alt


def die(msg: str, code: int = 1) -> None:
    print(f"[lls-pdf] 错误: {msg}", file=sys.stderr)
    sys.exit(code)
