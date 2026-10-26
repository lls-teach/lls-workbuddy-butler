"""lls-fapiao 共享工具：中文发票字段正则库 + 置信度标注 + 通用辅助。

设计原则（吸收自底座经验）：
- 低置信度字段必须标注"待人工核对"，绝不静默编造；
- 金额一律转 float（两位小数），文本型数字会害死 SUM；
- 发票号码长度白名单 {8, 10, 20}（数电票 20 位）。
"""
from __future__ import annotations

import os
import re
import sys

# ── 字段正则库（覆盖：数电票 / 增值税电子专票·普票 / 火车票 / 出租车票）──
PATTERNS = {
    "invoice_no": [
        r"(?:发票号码|号码)\s*[:：]?\s*(\d{20})",
        r"(?:发票号码|号码)\s*[:：]?\s*(\d{10})",
        r"(?:发票号码|号码)\s*[:：]?\s*(\d{8})",
        r"\b(\d{20})\b",  # 数电票号码常独立成行
    ],
    "date": [  # 独立日期兜底：标签与数值分行的票面（低置信度，进人工核对）
        r"(?:开票日期|日期)\s*[:：]?\s*(\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)",
        r"(?:开票日期|日期)\s*[:：]?\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2})",
        r"\b(20\d{2}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)\b",
        r"\b(20\d{2}[-/]\d{1,2}[-/]\d{1,2})\b",
    ],
    "total": [
        r"[（(]\s*小写\s*[)）]\s*[¥￥]?\s*([0-9,]+\.[0-9]{2})",
        r"价税合计[（(]小写[)）][¥￥]?\s*([0-9,]+\.[0-9]{2})",
        r"(?:合计金额|价税合计)\s*[:：]?\s*[¥￥]?\s*([0-9,]+\.[0-9]{2})",
        r"[¥￥]\s*([0-9,]+\.[0-9]{2})",
    ],
    "buyer": [
        r"名\s*称\s*[:：]\s*([^\n\x00-\x7f][^\n]{2,30}?(?:公司|中心|所|店|部|厂|银行|集团|商行|工作室|事务所))",
    ],
    "buyer_tax_id": [
        r"(?:纳税人识别号|统一社会信用代码|纳税人识别号)\s*[:：]?\s*([0-9A-Z]{15,20})",
    ],
    "seller_tax_id": [
        r"销售方.*?(?:纳税人识别号|统一社会信用代码)\s*[:：]?\s*([0-9A-Z]{15,20})",
    ],
    "kind": [  # 全角/半角括号都认
        r"(电子发票[（(]普通发票[）)])",
        r"(电子发票[（(]增值税专用发票[）)])",
        r"(数电票|全面数字化的电子发票)",
        r"(增值税电子专用发票|增值税电子普通发票|增值税专用发票|增值税普通发票)",
        r"(火车票|出租车票|机票行程单)",
    ],
}
TYPE_KEYWORDS = {
    "数电票": "数电票", "全面数字化": "数电票", "电子发票(普通发票)": "数电票-普票",
    "电子发票(增值税专用发票)": "数电票-专票", "增值税电子专用发票": "电子专票",
    "增值税专用发票": "专票", "增值税电子普通发票": "电子普票", "增值税普通发票": "普票",
    "火车票": "火车票", "出租车票": "出租车票", "机票行程单": "机票行程单",
}


def die(msg: str, code: int = 1) -> None:
    print(f"[lls-fapiao] 错误: {msg}", file=sys.stderr)
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
    print(f"[lls-fapiao] 目标已存在，改写到 {alt}（要覆盖请加 --force）", file=sys.stderr)
    return alt


def cjk_width(s: str) -> int:
    return sum(2 if ord(ch) > 0x2E7F else 1 for ch in str(s))


def to_amount(s: str | None) -> float | None:
    """'1,160.00'/'¥580' → float；失败返回 None。"""
    if not s:
        return None
    s = str(s).replace(",", "").replace("¥", "").replace("￥", "").strip()
    try:
        return round(float(s), 2)
    except ValueError:
        return None


def first_match(text: str, field: str) -> tuple[str | None, float]:
    """按正则优先级匹配字段，返回 (值, 置信度)。"""
    pats = PATTERNS.get(field, [])
    for i, pat in enumerate(pats):
        m = re.search(pat, text, re.S if field in ("buyer", "seller_tax_id") else 0)
        if m:
            # 命中专用标签 = 高置信；裸正则兜底 = 中置信
            return m.group(1).strip(), 0.95 if i == 0 else (0.85 if i == 1 else 0.6)
    return None, 0.0


def detect_kind(text: str) -> str:
    for pat, name in TYPE_KEYWORDS.items():
        if pat in text:
            return name
    if "火车" in text:
        return "火车票"
    if "出租车" in text or "网约车" in text:
        return "出租车票"
    return "未识别"


def norm_date(s: str | None) -> str | None:
    """'2026年10月27日'/'2026-10-27' → '2026-10-27'。"""
    if not s:
        return None
    m = re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})", s)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", s)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    return s
