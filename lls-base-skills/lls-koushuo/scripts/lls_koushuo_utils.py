"""lls-koushuo 共享工具：口播时长预算、开场钩子检查、分镜结构。"""
import re
import sys

# 中文口播语速：240 字/分钟（舒适区 220-260）
WPM = 240

def die(msg, code=1):
    print(f"[lls-koushuo] 错误: {msg}", file=sys.stderr)
    sys.exit(code)

def budget_check(text: str, target_minutes: float) -> dict:
    if target_minutes <= 0:
        die("目标时长须大于 0（分钟）")
    chars = len(re.sub(r"\s", "", text))
    est_minutes = chars / WPM
    return {"chars": chars, "target_minutes": target_minutes,
            "estimated_minutes": round(est_minutes, 1),
            "delta_pct": round((est_minutes - target_minutes) / target_minutes * 100)}

def hook_check(text: str) -> str | None:
    """前 60 字须有钩子：问句/数字/反常识/利益点。"""
    head = re.sub(r"\s", "", text)[:60]
    if not head:
        return "开场为空"
    if re.search(r"[？?]", head):
        return None
    if re.search(r"\d", head):
        return None
    hooks = ["你有没有", "为什么", "千万别", "我劝你", "90%", "大多数", "很多人", "错了", "真相", "秘密", "居然"]
    if any(h in head for h in hooks):
        return None
    return "前 60 字无钩子（问句/数字/反常识/利益点均未命中）——完播率会死在开头"

def split_scenes(text: str) -> list[tuple[str, int]]:
    """按空行或 ## 分段 → (段首摘要, 字数)。"""
    scenes = []
    for block in re.split(r"\n\s*\n", text):
        b = re.sub(r"\s", "", block)
        if b:
            scenes.append((b[:20], len(b)))
    return scenes


def ensure_parent(path: str) -> str:
    import os
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path
