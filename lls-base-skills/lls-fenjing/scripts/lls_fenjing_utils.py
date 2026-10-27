"""lls-fenjing 共享工具：镜头切分、时长分配（4 字/秒）、景别词表。"""
import re

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
