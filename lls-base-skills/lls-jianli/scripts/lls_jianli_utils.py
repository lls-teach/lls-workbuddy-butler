"""lls-jianli 共享工具：覆盖保护、中文 East-Asia 字体、JD 关键词提取。"""
from __future__ import annotations

import os
import re
import sys

CN_FONT = "宋体"
CN_FONT_HEI = "微软雅黑"
STOPWORDS = set("的 了 和 与 及 或 在 是 为 对 从 被 把 将 有 无 会 能 可 需 需要 负责 参与 进行 完成 具体 相关 以下 如下 各种 优先 熟悉 熟练 了解 精通 掌握 等等 使用 通过 基于 以及 我们 你们 公司 岗位 工作 要求 职责 经验 以上 良好 较强 团队 沟通 能力 岗位职责 任职要求 优先考虑 相关经验 事项 内容 方面 工作 内容 情况 问题 进行 通过 确保 保证 满足 达到".split())


def die(msg: str, code: int = 1) -> None:
    print(f"[lls-jianli] 错误: {msg}", file=sys.stderr)
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
    print(f"[lls-jianli] 目标已存在，改写到 {alt}（要覆盖请加 --force）", file=sys.stderr)
    return alt


def set_cn_font(run, name: str = CN_FONT) -> None:
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts")
    if rfonts is None:
        from docx.oxml.ns import qn
        rfonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rfonts)
    rfonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia", name)


def extract_keywords(jd_text: str, min_len: int = 2, top: int = 40) -> list[str]:
    """JD 关键词粗提取：中文 2-6 词元 + 英文/数字词，去停用词，按频次排序。"""
    text = jd_text.replace("\n", " ")
    cn_terms = re.findall(r"[\u4e00-\u9fff]{2,6}", text)
    en_terms = re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{1,20}", text)
    freq: dict[str, int] = {}
    for t in cn_terms + [e.lower() for e in en_terms]:
        if t in STOPWORDS:
            continue
        freq[t] = freq.get(t, 0) + 1
    ranked = sorted(freq.items(), key=lambda kv: -kv[1])
    return [t for t, _ in ranked[:top]]
