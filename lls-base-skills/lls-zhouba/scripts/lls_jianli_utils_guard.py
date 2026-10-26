"""zhouba 的极简 docx 辅助（避免跨包依赖）。"""
import os, sys

def die(msg, code=1):
    print(f"[lls-zhouba] 错误: {msg}", file=sys.stderr)
    sys.exit(code)

def ensure_parent(path):
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path

def guard_overwrite(path, force=False):
    if not os.path.exists(path) or force:
        return path
    root, ext = os.path.splitext(path)
    alt = f"{root}_new{ext}"
    print(f"[lls-zhouba] 目标已存在，改写到 {alt}", file=sys.stderr)
    return alt

def set_cn_font(run, name="宋体"):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    rf = rpr.find(ns + "rFonts")
    if rf is None:
        from docx.oxml.ns import qn
        rf = rpr.makeelement(qn("w:rFonts"), {}); rpr.append(rf)
    rf.set(ns + "eastAsia", name)
