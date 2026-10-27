"""lls-aiwei 共享工具：AI 味检测词库与句级结构模式（自研，覆盖 80+ 词 + 4 类句级特征）。"""
import re

# ── 词级 AI 味（词 → 改写方向）──
WORD_BANK = {
    # 结构套话
    "首先": "直接说第一件事", "其次": "接着说第二件事", "再者": "还有一件事",
    "此外": "另外有个事", "综上所述": "以上这些说白了就是", "总而言之": "一句话总结：",
    "值得注意的是": "有个细节要注意：", "需要指出的是": "得说清楚一点：",
    "众所周知": "（删掉，直接说事）", "不言而喻": "（删掉）", "毋庸置疑": "（删掉）",
    "在这个充满挑战的时代": "（删掉）", "随着…的发展": "改成具体时间或事件开头",
    # 动词套话
    "赋能": "帮…做到（说清帮谁做到什么）", "助力": "帮", "旨在": "是为了",
    "致力于": "一直在做", "深耕": "专注做了多年", "拥抱": "开始用",
    "拉通": "把…串起来", "对齐": "商量一致", "沉淀": "留下", "构建…生态": "把相关的事做起来",
    # 形容/副词套话
    "显著提升": "提了多少（写具体数字）", "有效提升": "提升了（写数字）",
    "极大地": "（删掉，让数字说话）", "有效地": "（删掉）", "广泛应用": "用在哪些地方（举实例）",
    "日益增长": "越来越（写数字）", "越来越高": "越来越（写数字）",
    "淋漓尽致": "拉满", "可圈可点": "能打", "行之有效": "真的管用", "卓有成效": "见效了",
    # 空洞强化
    "强大的": "强在哪（写具体）", "高效的": "快在哪（写数字）", "全面的": "全在哪（列举）",
    "深入的": "深到哪（写细节）", "专业的": "专业在哪（写证据）", "优质的": "好在哪（写标准）",
    "一站式": "到底包含哪些（列举）", "全方位": "覆盖了哪些（列举）", "多维度": "哪几个维度（列举）",
    "智能化": "自动做了什么（写动作）", "不断完善": "改了什么（写事实）", "不断发展": "发生了什么（写事实）",
    # 公文/汇报腔
    "扎实推进": "做了什么（写事实）", "稳步推进": "推进到哪（写进度）", "狠抓落实": "抓了什么（写事实）",
    "高度重视": "具体做了什么（写动作）", "决策部署": "哪个决定（写内容）",
}
WORD_PATTERNS = {k: re.compile(re.escape(k)) for k in WORD_BANK}

# ── 句级结构模式 ──
SUMMARY_OPEN = re.compile(r"^(总之|综上|可见|因此|由此可以看出|总的来说)", re.M)
ABSTRACT_STACK = re.compile(r"[一-龥]{1,4}[性化度][一-龥]{0,2}[性化度][一-龥]{0,2}[性化度]")

def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"[。！？\n]", text) if len(s.strip()) >= 6]

def parallel_hits(text: str) -> list[str]:
    """排比三连：同一句里 ≥3 个逗号/顿号分句且开头 2 字相同（AI 爱用的整齐排比）。"""
    hits = []
    for sent in sentences(text):
        parts = [p.strip() for p in re.split(r"[，,]", sent) if len(p.strip()) >= 4]
        if len(parts) >= 3:
            heads = [p[:2] for p in parts]
            if len(set(heads)) == 1 or len(set(heads)) <= len(parts) // 2:
                hits.append(sent)
    return hits

def abstract_hits(text: str) -> list[str]:
    return [m.group(0) for m in ABSTRACT_STACK.finditer(text)]

def summary_hits(text: str) -> list[str]:
    return [s for s in sentences(text) if SUMMARY_OPEN.match(s)]

def length_uniformity(text: str) -> float | None:
    """连续 ≥5 句的句长标准差/均值（变异系数）。<0.15 = AI 均匀句长特征。"""
    ss = sentences(text)
    for i in range(len(ss) - 4):
        window = [len(s) for s in ss[i:i + 5]]
        mean = sum(window) / 5
        if mean == 0:
            continue
        var = sum((x - mean) ** 2 for x in window) / 5
        cv = (var ** 0.5) / mean
        if cv < 0.15:
            return round(cv, 3)
    return None

def die(msg, code=1):
    print(f"[lls-aiwei] 错误: {msg}", file=sys.stderr)
    sys.exit(code)

def ensure_parent(path):
    import os
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path

import sys
