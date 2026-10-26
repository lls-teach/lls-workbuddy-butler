#!/usr/bin/env python3
"""lhg-net skill 级冒烟：校验「取数决策记录」是否符合本 skill 硬性规则。

用法：
    python3 scripts/smoke_test.py <决策记录.md>

决策记录字段（见 references/fixtures/）：
    请求分类 / 路由决策 / 平台 / 后端链状态 / 选择后端 / 开工声明 / 动作清单

规则（对应 SKILL.md）：
    C1 NOT-for 收窄 — 开放式调研必须指路 lhg-deep-research，禁止自处理误触发（1.2）
    C2 分工正确     — 热点选题→lhg-trend，写作→lhg-writing（1.2）
    C3 降级路由     — 选择后端必须是链上"可用"的，禁止选用标记"失效"的后端（2.3/4）
    C4 开工声明     — 须声明"用 X 平台 / Y 后端"（常驻规则 2）
    C5 安全默认     — 动作清单不得含写入动作（7）

退出码 0=全绿；1=有 FAIL。
"""
import argparse
import re
import sys

WRITE_WORDS = ["发帖", "点赞", "评论", "转发", "私信", "关注", "写入", "发布内容"]

# 请求分类 → 期望的路由决策关键词
ROUTE_EXPECT = {
    "开放式调研": "lhg-deep-research",
    "热点选题": "lhg-trend",
    "写作": "lhg-writing",
}


def parse_record(text: str) -> dict:
    fields = {}
    for key in ["用户请求", "请求分类", "路由决策", "平台",
                "后端链状态", "选择后端", "开工声明", "动作清单"]:
        m = re.search(rf"^[-*][ \t]*{key}[：:][ \t]*(.+)$", text, re.M)
        fields[key] = m.group(1).strip() if m else ""
    return fields


def backend_status(chain: str) -> dict:
    """解析「首选=可用；备选1=失效」为 {后端名: 状态}。"""
    out = {}
    for part in re.split(r"[;；]", chain):
        m = re.match(r"\s*(\S+?)\s*=\s*(\S+)\s*$", part)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def check(f: dict) -> list:
    fails = []
    cat, route = f["请求分类"], f["路由决策"]

    # C1：开放式调研禁止自处理误触发
    if cat == "开放式调研":
        if "lhg-deep-research" not in route:
            fails.append("C1 NOT-for 违规：开放式调研未指路 lhg-deep-research（误触发 lhg-net）")
        if "自处理" in route:
            fails.append("C1 NOT-for 违规：开放式调研被 lhg-net 自处理，应交 lhg-deep-research")
    # C2：其他 NOT-for 分工
    for c, expect in ROUTE_EXPECT.items():
        if c != "开放式调研" and cat == c and expect not in route:
            fails.append(f"C2 分工错误：「{c}」应指路 {expect}，实际路由：{route or '空'}")

    # C3：降级路由——禁止选用失效后端
    chain = backend_status(f["后端链状态"])
    chosen = f["选择后端"]
    if chosen:
        st = chain.get(chosen)
        if st is not None and st.startswith("失效"):
            fails.append(f"C3 降级路由错误：选择了已标记失效的后端「{chosen}」")
        elif st is None and chain:
            fails.append(f"C3 降级路由错误：「{chosen}」不在后端链状态记录中")
        # 未探测允许（SKILL.md 4.4：未探测≠不可用），但必须在开工声明里可追踪
    elif cat == "取数":
        fails.append("C3 缺选择后端：取数任务未声明选用后端")

    # C4：开工声明
    decl = f["开工声明"]
    if cat == "取数":
        if "lhg-net" not in decl:
            fails.append("C4 缺开工声明：未声明使用 lhg-net")
        if not f["平台"] or f["平台"] not in decl:
            fails.append("C4 开工声明不完整：未写明平台")
        if "后端" not in decl and "降级" not in decl:
            fails.append("C4 开工声明不完整：未写明后端/轨道")

    # C5：安全默认
    for w in WRITE_WORDS:
        if w in f["动作清单"]:
            fails.append(f"C5 安全默认违规：动作清单含写入动作「{w}」（只读不发帖）")
            break
    return fails


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("record", help="取数决策记录 markdown 文件")
    args = ap.parse_args()
    with open(args.record, encoding="utf-8") as fh:
        fails = check(parse_record(fh.read()))
    if fails:
        print("FAIL:")
        for x in fails:
            print(" -", x)
        return 1
    print("✅ 冒烟测试全绿")
    return 0


if __name__ == "__main__":
    sys.exit(main())
