"""lls-shuzhi 共享工具：覆盖保护、量化检测、述职大纲合成。"""
import os
import re
import sys

def die(msg, code=1):
    print(f"[lls-shuzhi] 错误: {msg}", file=sys.stderr)
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
    print(f"[lls-shuzhi] 目标已存在，改写到 {alt}", file=sys.stderr)
    return alt

QUANT_PAT = re.compile(r"(\d+(?:\.\d+)?\s*[%％万亿个条家次人元小时天月年])|(\d{2,})")

def quant_score(text: str) -> tuple[int, int]:
    """返回 (含量化数字的成果条数, 成果总条数)。"""
    items = [l[2:].strip() for l in text.split("\n") if l.startswith("- ")]
    hit = sum(1 for l in items if QUANT_PAT.search(l))
    return hit, len(items)

def compose_outline(data: dict) -> str:
    """结构化述职 JSON → lls-pptx v2.2 大纲（KPI 页 + 状态表 + 决策表）。"""
    lines = []
    kpis = data.get("kpis", [])
    if kpis:
        lines.append(f"# {data.get('period', '本周期')}业绩总览")
        for k in kpis[:4]:
            parts = [str(k.get("value", "")), k.get("label", ""), k.get("note", "")]
            lines.append("[KPI] " + "|".join(p for p in parts if p))
        lines.append("= " + data.get("source", "述职人自报数据"))
        lines.append("> " + data.get("verdict", ""))
    for proj in data.get("projects", []):
        lines.append(f"# {proj.get('name', '重点项目')}")
        for s in proj.get("status_rows", []):
            lines.append("[STATUS] " + "|".join(str(x) for x in s))
        for b in proj.get("bullets", []):
            lines.append("- " + b)
        if proj.get("takeaway"):
            lines.append("> " + proj["takeaway"])
    issues = data.get("issues", [])
    if issues:
        lines.append("# 问题与复盘")
        for it in issues:
            lines.append(f"- {it.get('problem', '')} → {it.get('action', '')}")
        lines.append("> 复盘为了下季度不再踩同一个坑")
    plans = data.get("plans", [])
    if plans:
        lines.append("# 下期计划")
        lines.append("[TABLE] 事项|目标|里程碑|负责人")
        for p in plans:
            lines.append("[TABLE] " + "|".join(str(p.get(k, "")) for k in ("item", "goal", "milestone", "owner")))
        lines.append("> 计划到人到时间，才是计划")
    return "\n".join(lines)
