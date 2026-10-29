"""lls-htmlppt 共享工具：大纲解析（#/##/-/> 语法）。"""
import re


def die(msg, code=1):
    import sys
    print(f"[lls-htmlppt] 错误: {msg}", file=sys.stderr)
    sys.exit(code)


def ensure_parent(path):
    import os
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path


def parse_outline(text: str) -> dict:
    """大纲 → {title, subtitle, slides:[{title, bullets, takeaway}]}。

    '# ' 首个 = deck 标题；'## ' = 页标题；'- ' = 要点；'> ' = 结论。
    """
    title, subtitle, slides = "", "", []
    cur = None
    for raw in text.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("# ") and not slides:
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            slides.append({"title": line[3:].strip(), "bullets": [], "takeaway": None})
            cur = slides[-1]
            continue
        if line.startswith("> "):
            if cur is None:
                slides.append({"title": "", "bullets": [], "takeaway": line[2:].strip()})
                cur = slides[-1]
            else:
                cur["takeaway"] = line[2:].strip()
            continue
        if line.startswith("- ") or line.startswith("* "):
            if cur is None:
                slides.append({"title": "", "bullets": [], "takeaway": None})
                cur = slides[-1]
            cur["bullets"].append(line[2:].strip())
            continue
        # 普通行视作要点
        if cur is None:
            slides.append({"title": line.strip(), "bullets": [], "takeaway": None})
            cur = slides[-1]
        else:
            cur["bullets"].append(line.strip())
    return {"title": title, "subtitle": subtitle, "slides": slides}


def guard_overwrite(path: str, force: bool = False) -> str:
    import os
    if not os.path.exists(path) or force:
        return path
    root, ext = os.path.splitext(path)
    alt = f"{root}_new{ext}"
    n = 2
    while os.path.exists(alt):
        alt = f"{root}_new{n}{ext}"
        n += 1
    import sys
    print(f"[lls-htmlppt] 目标已存在，改写到 {alt}", file=sys.stderr)
    return alt
