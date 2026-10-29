"""lls-xuanti 共享工具：三维选题矩阵 + 评分卡。"""
import itertools

FORMS = ["图文", "口播视频", "清单合集", "案例拆解", "教程步骤", "对比测评"]
HOOKS = ["问句钩子", "数字钩子", "反常识钩子", "身份钩子", "利益钩子", "避坑钩子"]
ANGLES = ["新手入门", "进阶技巧", "避坑警示", "案例拆解", "工具盘点", "行业趋势"]


def matrix(lane: str, crowd: str, platform: str) -> list[dict]:
    """赛道×人群×平台 → 角度×形式×钩子 组合选题卡（96 张确定性枚举，AI 负责给每张卡起标题）。"""
    cards = []
    n = 0
    for angle, form, hook in itertools.product(ANGLES, FORMS[:4], HOOKS[:4]):
        n += 1
        cards.append({
            "id": n,
            "angle": angle, "form": form, "hook": hook,
            "seed": f"[{lane}·{crowd}·{platform}] {angle}角度 + {form} 形式 + {hook}",
        })
    return cards


def scorecard_template() -> str:
    return """| 选题 | 竞争密度(1-5) | 情绪强度(1-5) | 实操价值(1-5) | 总分 | 值得做? |
|---|---|---|---|---|---|
| （AI 填入选题标题） | | | | | |
评分口径：竞争密度=同类内容多少（越少越好）；情绪强度=能否触发共鸣/焦虑/好奇；实操价值=看完能立刻做什么。总分=三项之和（3-15），≥10 优先制作。"""


def ensure_parent(path: str) -> str:
    import os
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path
