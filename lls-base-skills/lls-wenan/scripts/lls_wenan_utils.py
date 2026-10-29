"""lls-wenan 共享工具：四平台规范 + AI味检测词库。"""
import re

# 四平台内容规范
PLATFORMS = {
    "小红书": {"title_max": 20, "body_max": 1000, "tags_min": 3, "emoji_required": True,
              "style": "分段短句（每段≤2行）、首行钩子、结尾 3-6 个 #话题标签、适度 emoji"},
    "公众号": {"title_max": 64, "body_max": 5000, "tags_min": 0, "emoji_required": False,
              "style": "长段落叙事、小标题分节、金句加粗、结尾引导在看/关注、摘要 ≤120 字"},
    "抖音口播": {"title_max": 30, "body_max": 600, "tags_min": 1, "emoji_required": False,
              "style": "短句口语（每句≤15字）、3 秒钩子开场、结尾 CTA、240 字/分钟"},
    "朋友圈": {"title_max": 0, "body_max": 200, "tags_min": 0, "emoji_required": False,
              "style": "3 行以内、首行钩子、不换行超过 2 次、留悬念引私信"},
}

# AI 味黑名单（检测→改写方向）
AI_FLAVOR = {
    "首先": "直接说第一件事", "其次": "接着说第二件事", "最后": "收尾直接给结论",
    "综上所述": "以上这些说白了就是", "值得注意的是": "有个细节要注意：",
    "深入探讨": "展开聊聊", "众所周知": "（删掉，直接说事）", "总而言之": "一句话总结：",
    "赋能": "帮…做到", "助力": "帮", "旨在": "是为了", "致力于": "一直在做",
    "凸显": "放大", "彰显": "透出", "淋漓尽致": "拉满", "可圈可点": "能打",
    "让我们一起": "（删掉）", "在这个充满挑战的时代": "（删掉）",
    "然而": "但是，直接说转折", "因此": "所以，直接给结论",
    "此外": "另外，再说一点", "另外": "再说一点",
    "值得一提的是": "有个细节：", "不可否认": "说实话",
    "显而易见": "一眼就能看出来", "换言之": "说白了",
    "简而言之": "一句话：", "总的来说": "总体看",
    "毋庸置疑": "不用多说", "毫无疑问": "肯定",
    "归根结底": "说到底", "本质上": "说白了就是",
    "某种程度上": "在这方面", "一定程度上": "在一定范围里",
    "进一步": "接下来", "更重要的是": "最关键的是",
    "不仅如此": "不光这样", "与此同时": "同一时间",
    "另一方面": "另一头看", "深入分析": "拆开看",
    "显著提升": "明显变好（要给数字）", "有效提升": "真提上来了（要给数字）",
    "持续优化": "一直在改", "着力": "下力气",
    "切实": "落到实处，具体说",
}
AI_PHRASES = list(AI_FLAVOR.keys())


def ai_flavor_scan(text: str) -> list[tuple[str, str]]:
    """返回 [(AI味词, 改写方向)]，按出现次数降序。"""
    found = []
    for w in AI_PHRASES:
        n = text.count(w)
        if n:
            found.append((w, n))
    found.sort(key=lambda kv: -kv[1])
    return [(w, AI_FLAVOR[w]) for w, _ in found]


def ensure_parent(path: str) -> str:
    import os
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path


def die(msg: str, code: int = 1) -> None:
    import sys
    print(f"[lls-wenan] 错误: {msg}", file=sys.stderr)
    sys.exit(code)
