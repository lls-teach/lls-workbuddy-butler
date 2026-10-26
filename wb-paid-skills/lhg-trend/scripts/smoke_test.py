#!/usr/bin/env python3
"""lhg-trend 产出物冒烟校验：检查热点扫描报告是否遵守 skill 纪律。

用法：
    python3 scripts/smoke_test.py <报告.md> [--topic-mode]

检查项：
    W-1  30 天窗口声明：标题行含起止日期（YYYY-MM-DD ~ YYYY-MM-DD）
    W-2  热度数字可查：含"播放/点赞/热度/阅读量/讨论量/赔率"的行必须同时含 http 或"来源"
    W-3  诚实降级：健康检查节中标记为不可用/未采用/❌ 的信源，
         不得在报告其他位置被归因热度数字
    W-4  三件套：每个"### "热点标题下必须出现"为什么值得做""切入角度""对标账号是否已做"
    W-5  候选数量（发现模式）：候选节中"### "热点数为 5–10；主题模式用 --topic-mode 跳过
"""
import re
import sys

HEAT_WORDS = ["播放", "点赞", "热度", "阅读量", "讨论量", "赔率", "转发", "转推", "评论数"]


def check(path, topic_mode=False):
    text = open(path, encoding="utf-8").read()
    lines = text.splitlines()
    fails = []

    # W-1：窗口声明
    if not re.search(r"20\d{2}-\d{2}-\d{2}\s*[~～-]\s*20\d{2}-\d{2}-\d{2}", text):
        fails.append("W-1 窗口声明缺失：标题行未写明 30 天起止日期（YYYY-MM-DD ~ YYYY-MM-DD）")

    # 切出健康检查节，其余为正文
    m = re.search(r"##\s*信源健康检查", text)
    health, body = (text[m.start():], text[: m.start()]) if m else ("", text)

    # W-2：热度数字必须可查。只查"热度词 + 数量"的事实型表述：
    # 先剥离"（热度分：高/中/低）"这类定性标签，再要求数字带量词形态
    # （万/亿/k/%/赞/播放/阅读/转推/评论/条/次），避免"### 1."编号与"赔率解读"误伤。
    for i, ln in enumerate(lines, 1):
        clean = re.sub(r"（热度分：[高中低]）", "", ln)
        if (
            any(w in clean for w in HEAT_WORDS)
            and re.search(r"\d[\d.,]*\s*(万|亿|[kK]|%|赞|播放|阅读|转推|评论|条|次|人)", clean)
            and "http" not in clean
            and "来源" not in clean
            and "出处" not in clean
        ):
            fails.append(f"W-2 第{i}行热度数字无出处：{ln.strip()[:60]}")

    # W-3：诚实降级——失效信源不得被归因热度
    dead = []
    for row in re.findall(r"\|\s*([^|]+?)\s*\|\s*❌[^\n]*", health):
        dead.append(row.strip())
    for row in re.findall(r"\|\s*([^|]+?)\s*\|\s*[^|]*?(?:不可用|未采用)[^\n]*", health):
        name = row.strip()
        if name and name not in dead:
            dead.append(name)
    for name in dead:
        short = re.sub(r"[（(].*[)）]", "", name).strip()
        for i, ln in enumerate(body.splitlines(), 1):
            if short and short in ln and any(w in ln for w in HEAT_WORDS):
                fails.append(f"W-3 诚实降级失败：健康检查已标「{name}」不可用，"
                             f"第{i}行却归因其热度数字：{ln.strip()[:60]}")

    # W-4：三件套（候选榜在健康检查节之后，故扫全文）
    sections = re.split(r"^###\s+", text, flags=re.M)
    hotspots = [s for s in sections[1:] if s.strip()]
    for hs in hotspots:
        title = hs.splitlines()[0][:30]
        for key in ["为什么值得做", "切入角度", "对标账号是否已做"]:
            if key not in hs:
                fails.append(f"W-4 热点「{title}」缺三件套：{key}")

    # W-5：候选数量（发现模式）
    if not topic_mode:
        n = len(hotspots)
        if n and not (5 <= n <= 10):
            fails.append(f"W-5 发现模式候选话题 {n} 个，不在 5–10 范围内")

    return fails


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    topic_mode = "--topic-mode" in sys.argv
    if not args:
        print("用法：python3 scripts/smoke_test.py <报告.md> [--topic-mode]")
        sys.exit(2)
    fails = check(args[0], topic_mode)
    if fails:
        print("❌ 冒烟测试 FAIL：")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("✅ 冒烟测试全绿")


if __name__ == "__main__":
    main()
