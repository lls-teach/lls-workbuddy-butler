"""lls-huiyi 共享工具：转写稿清洗、说话人分离、行动项/决策抽取。"""
import re

FILLERS = ["嗯", "啊", "呃", "那个那个", "就是说", "然后然后", "这个这个", "对对对", "就是说"]

ACTION_HINT = r"(负责|跟进|落实|截止|周[一二三四五六日]|月底|月底前|下周|本周内|之前完成|提交|输出|安排|协调)"
DECISION_HINT = r"(决定|确定|同意|拍板|定下来|敲定|否决|通过)"

def clean(text: str) -> str:
    """去口头禅、压缩重复标点、按句重组。"""
    for f in FILLERS:
        text = text.replace(f, "")
    # 去 BOM 残留；去口头禅后残留的孤标点（如“张三：嗯，大家”→“张三：，大家”）。
    text = text.replace("\ufeff", "")
    text = re.sub(r"([:：])\s*[，,、；;]", r"\1", text)
    text = re.sub(r"(?m)^[，,、；;]+", "", text)
    text = re.sub(r"([。！？，,])\1+", r"\1", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

def split_turns(text: str) -> list[tuple[str, str]]:
    """识别 '说话人：内容' 行；无说话人归为 ""（未标注）。"""
    turns = []
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^([^:：\d]{1,12})[:：]\s*(.+)$", line)
        if m:
            turns.append((m.group(1).strip(), m.group(2).strip()))
        else:
            turns.append(("", line))
    return turns

def extract_actions(text: str) -> list[str]:
    out = []
    for sent in re.split(r"[。！？\n]", text):
        sent = sent.strip()
        if sent and re.search(ACTION_HINT, sent) and len(sent) > 6:
            out.append(sent)
    return out

def extract_decisions(text: str) -> list[str]:
    out = []
    for sent in re.split(r"[。！？\n]", text):
        sent = sent.strip()
        if sent and re.search(DECISION_HINT, sent) and len(sent) > 6:
            out.append(sent)
    return out


def ensure_parent(path: str) -> str:
    import os
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path
