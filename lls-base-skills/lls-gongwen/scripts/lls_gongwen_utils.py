"""lls-gongwen 共享工具：GB/T 9704 版式常量 + 文种规则。"""
import os
import sys

CN_FS = "仿宋"          # 正文仿宋_GB2312 的可用替代
CN_HEI = "黑体"
CN_KAI = "楷体"
CN_SONG = "宋体"

def die(msg, code=1):
    print(f"[lls-gongwen] 错误: {msg}", file=sys.stderr)
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
    print(f"[lls-gongwen] 目标已存在，改写到 {alt}", file=sys.stderr)
    return alt

DOC_KINDS = ["通知", "请示", "报告", "函", "纪要", "批复", "决定", "意见"]
def title_kind(title: str) -> str | None:
    """标题结尾的文种词（关于XX的通知 → 通知）。"""
    for k in DOC_KINDS:
        if title.rstrip().endswith(k):
            return k
    return None

def set_cn_font(run, name: str = CN_FS) -> None:
    """python-docx 中文字体需同时写 eastAsia 属性。"""
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    rfonts = rpr.find(ns + "rFonts")
    if rfonts is None:
        from docx.oxml.ns import qn
        rfonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rfonts)
    rfonts.set(ns + "eastAsia", name)
