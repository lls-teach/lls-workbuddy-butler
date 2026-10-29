"""lls-jiaoan 共享工具：教案要素规则。"""
import sys


def die(msg, code=1):
    print(f"[lls-jiaoan] 错误: {msg}", file=sys.stderr)
    sys.exit(code)


def ensure_parent(path):
    import os
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path


def guard_overwrite(path, force=False):
    import os
    if not os.path.exists(path) or force:
        return path
    root, ext = os.path.splitext(path)
    alt = f"{root}_new{ext}"
    n = 2
    while os.path.exists(alt):
        alt = f"{root}_new{n}{ext}"
        n += 1
    print(f"[lls-jiaoan] 目标已存在，改写到 {alt}", file=sys.stderr)
    return alt


def set_cn_font(run, name="宋体"):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    rfonts = rpr.find(ns + "rFonts")
    if rfonts is None:
        from docx.oxml.ns import qn
        rfonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rfonts)
    rfonts.set(ns + "eastAsia", name)


# 可测量目标动词参考；"了解/掌握/熟悉"为不可测量弱动词
WEAK_VERBS = ["了解", "掌握", "熟悉", "理解", "知道", "学会"]
STRONG_HINT = ["说出", "列举", "写出", "计算", "画出", "演示", "设计", "比较", "归纳", "解释", "运用", "分析"]
MEASUREMENT_HINTS = ["能够", "会", "能", "说出", "列举", "写出", "演示", "完成"]
