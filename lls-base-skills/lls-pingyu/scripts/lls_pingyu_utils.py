"""lls-pingyu 共享工具：评语批量 lint 规则。"""
import re

# 负面标签词 → 成长性表述建议
NEGATIVE_LABELS = {
    "笨": "需要更多的练习时间", "懒": "学习主动性有待激发",
    "差": "基础还需夯实", "不认真": "专注度有待提升",
    "不努力": "投入度有待提高", "不听话": "规则意识有待建立",
    "太差": "还有较大提升空间", "顽皮": "活泼好动，需要正向引导",
}
# 通用好评开头（重复检测黑名单——评语开头最易模板化）
GENERIC_OPENERS = ["该生", "该同学", "你是一个", "你是个", "本学期"]

def die(msg, code=1):
    print(f"[lls-pingyu] 错误: {msg}", file=__import__("sys").stderr)
    __import__("sys").exit(code)


def parse_comments(text: str) -> list[dict]:
    """评语 md → [{name, comment}]，支持 '姓名：评语' 行或 '### 姓名' 段落。"""
    if text.startswith("\ufeff"):  # Windows 记事本 UTF-8 BOM：去 BOM，防首个姓名被污染
        text = text[1:]
    students = []
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^(?:###\s*)?([^：:]{1,12})[:：]\s*(.+)$", line)
        if m and not line.startswith("#"):
            students.append({"name": m.group(1).strip(), "comment": m.group(2).strip()})
        elif line.startswith("###"):
            students.append({"name": line.lstrip("# ").strip(), "comment": ""})
    return students
