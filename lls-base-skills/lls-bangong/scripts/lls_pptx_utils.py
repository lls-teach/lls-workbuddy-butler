"""lls-pptx 共享工具：覆盖保护、中文字体设置、大纲解析。"""
from __future__ import annotations

import os
import re
import sys

from pptx.oxml.ns import qn

CN_FONT = "微软雅黑"


def die(msg: str, code: int = 1) -> None:
    print(f"[lls-pptx] 错误: {msg}", file=sys.stderr)
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
    print(f"[lls-pptx] 目标已存在，改写到 {alt}（要覆盖请加 --force）", file=sys.stderr)
    return alt


def parse_outline(text: str) -> list[dict]:
    """v3 大纲解析（吸收 jingmei 版式词汇）：

      '# '  页标题（写结论不写话题）
      '[KPI] 31,940|技能总量|仍在高速增长'        KPI 数字行（一页最多 4 个）
      '[STATUS] 名称|空位说明|时间|状态|色'        语义状态表行（色: amber/blue/good/muted，缺省按状态关键词）
      '[BAR] 58|实名认证'                          进度条行（百分比）
      '[TABLE] 合作项|我方投入|贵方投入|周期'       斑马纹表格行（首个 TABLE 行为表头）
      '- '  要点（>=5 自动两列）
      '> '  本页结论（结论带）
      '= '  来源行（页脚上方）
    """
    slides: list[dict] = []

    def new_page():
        return {"title": "", "kpis": [], "bars": [], "status_rows": [], "table_rows": [],
                "bullets": [], "takeaway": None, "source": None}

    cur = None
    for raw in text.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("# "):
            cur = new_page(); cur["title"] = line[2:].strip(); slides.append(cur)
            continue
        if cur is None:
            cur = new_page(); slides.append(cur)
        if line.startswith("[KPI] "):
            parts = [p.strip() for p in line[6:].split("|")]
            cur["kpis"].append(parts + [""] * (3 - len(parts)))
        elif line.startswith("[STATUS] "):
            parts = [p.strip() for p in line[9:].split("|")]
            cur["status_rows"].append(parts + [""] * (5 - len(parts)))
        elif line.startswith("[BAR] "):
            parts = [p.strip() for p in line[6:].split("|")]
            cur["bars"].append(parts + [""] * (2 - len(parts)))
        elif line.startswith("[TABLE] "):
            cur["table_rows"].append([p.strip() for p in line[8:].split("|")])
        elif line.startswith("> "):
            cur["takeaway"] = line[2:].strip()
        elif line.startswith("= "):
            cur["source"] = line[2:].strip()
        elif line.startswith("- "):
            cur["bullets"].append(line[2:].strip())
        else:
            cur["bullets"].append(line.strip())
    return [s for s in slides if s["title"] or s["bullets"] or s["kpis"] or s["status_rows"] or s["bars"] or s["table_rows"]]


def apply_cn_font(run, name: str = CN_FONT) -> None:
    """python-pptx 的 font.name 只写 a:latin；CJK 必须同时写 a:ea，否则部分渲染器丢字形。"""
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = rPr.makeelement(qn("a:ea"), {})
        rPr.append(ea)
    ea.set("typeface", name)
