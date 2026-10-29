"""lls-fenjing 共享工具：镜头切分、时长分配（4 字/秒）、景别词表。"""
import re
import sys

SHOTS = ["远景", "全景", "中景", "近景", "特写", "空镜"]
SPEED = 4  # 中文口播 4 字/秒（240 字/分钟）


def die(msg, code=1):
    print(f"[lls-fenjing] 错误: {msg}", file=sys.stderr)
    sys.exit(code)


def ensure_parent(path):
    import os
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path


def split_lines(text: str) -> list[str]:
    out = []
    for block in re.split(r"\n\s*\n", text):
        b = re.sub(r"\s+", " ", block).strip()
        if b:
            out.append(b)
    return out


def duration_of(line: str) -> int:
    return max(2, round(len(re.sub(r"\s", "", line)) / SPEED))


def split_long_line(line: str, limit: int = 200, target: int = 100) -> list[str]:
    """单段超长（>limit 字）时按句切分打包，不足一句按 target 字硬切。

    对应 SKILL.md 失败分支 #1：单镜头台词 200 字 → 拆成 2-3 个镜头。
    长度未超限时原样返回单段，保证原有“一段 = 一镜头”行为不变。
    """
    if len(re.sub(r"\s", "", line)) <= limit:
        return [line]
    # 按中文句末标点切分，标点留在前一句末尾；无标点的长串走硬切兜底
    parts = [p for p in re.split(r"(?<=[，。！？；、])", line) if p]
    chunks: list[str] = []
    buf = ""
    for p in parts:
        if len(re.sub(r"\s", "", p)) > target:
            if buf:
                chunks.append(buf)
                buf = ""
            s = p
            while len(re.sub(r"\s", "", s)) > target:
                chunks.append(s[:target])
                s = s[target:]
            buf = s
            continue
        if buf and len(re.sub(r"\s", "", buf + p)) > target:
            chunks.append(buf)
            buf = p
        else:
            buf += p
    if buf:
        chunks.append(buf)
    return chunks or [line]
