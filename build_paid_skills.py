#!/usr/bin/env python3
"""构建 lhg 四件套的 WorkBuddy 付费版副本。

- 从 ~/.agents/skills 复制（排除 README.md / LICENSE / .github/）
- 删除自更新检查块、一键通知作者、上游同步等开源渠道专属内容
- frontmatter 补 WorkBuddy 必填字段：description_zh / description_en / author，版本升 1.2.0
- 保留借鉴声明（含 AGPL 安全绳）与冒烟测试、fixtures
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path("/Users/kanshan28/.agents/skills")
DST = Path("/Volumes/work/code/LLSStudio/workbuddy_project/wb-paid-skills")

ITEM4_LONG_OLD = (
    '4. 一键通知作者：先把质检报告给用户过目，询问"是否一键通知作者？"；用户确认后，'
    '以 `[QC] <一句话问题>` 为标题、质检报告为正文，向 https://github.com/lhg-skills/{name}/issues '
    '提交 issue。有 gh/API 能力时直接创建；无能力时输出预填好的 issue 文本 + new issue 链接，'
    '由用户手动发布。仓库内备有 `.github/ISSUE_TEMPLATE/qc-report.md` 模板。'
)
ITEM4_LONG_NEW = "4. 问题反馈：质检报告给用户过目后，由用户通过 WorkBuddy 资产页联系作者反馈问题，作者跟进修复。"

ITEM4_SHORT_OLD = "4. **一键通知作者**：报告经用户确认后，按 `.github/ISSUE_TEMPLATE/qc-report.md` 模板以 `[QC]` 为标题前缀提交 issue。"
ITEM4_SHORT_NEW = "4. **问题反馈**：质检报告经用户确认后，由用户通过 WorkBuddy 资产页联系作者反馈问题。"

ITEM5_PR_OLD_TREND = "5. 修复后必须重跑冒烟测试全绿，再开 PR；默认由用户确认合并。"
ITEM5_PR_NEW = "5. 修复后必须重跑冒烟测试全绿，再随更新版本交付。"

ITEM5_PR_OLD_GENERIC = "5. **修复后测试、开 PR**：按用户确认的方案修改，跑冒烟测试全绿后开 PR，默认由用户确认合并。"
ITEM5_PR_NEW_GENERIC = "5. **修复后重测**：按用户确认的方案修改，跑冒烟测试全绿后随更新版本交付。"

SYNC_UPSTREAM_LINES = {
    "lhg-trend": "6. 定期同步上游：方法借鉴的 `mvanhorn/last30days-skill`（MIT）有实质更新时，评估是否同步。\n",
    "lhg-net": "6. **定期同步上游**：能力层方法借鉴的 Panniantong/Agent-Reach（MIT）有更新时，评估是否同步（只同步方法论，不复制原文）。\n",
    "lhg-slides": "6. **定期同步上游**：方法借鉴的三个来源有更新时，评估是否同步（注意 AGPL-3.0 来源只同步思路，不引入其代码与模板资产）。\n",
}
TREND_ITEM7 = ("7. 自检通过时不输出质检报告、不打扰用户。", "6. 自检通过时不输出质检报告、不打扰用户。")

DESCRIPTION_EN = {
    "lhg-writing": (
        "Chinese writing pipeline: genre calibration -> style-fingerprint extraction -> "
        "outline-based section writing (Orwell's six rules enforced) -> AI-flavor diagnosis "
        "(6-dimension checklist) -> minimalist compression -> consistency checks. Produces "
        "natural, opinionated, verifiable Chinese prose."
    ),
    "lhg-trend": (
        "Scan hot topics across the web over the last 30 days: deep-dive cross-platform "
        "discussion for a given topic, or nominate 5-10 topic candidates ranked by real "
        "engagement. Hard 30-day window; honest degradation when sources fail."
    ),
    "lhg-net": (
        "Internet data-fetching layer for AI agents: 14 Chinese-first platforms, each with an "
        "ordered backend chain (preferred -> fallback -> pure-workflow degradation); tool + "
        "workflow dual-track that runs with zero external dependencies; fetches data only, "
        "never analyzes."
    ),
    "lhg-slides": (
        "Single-file HTML presentation generator: style-first (choose from 3 visual thumbnails, "
        "then batch-generate), natively editable in the browser (locked slots preserve "
        "aesthetics; unlocked objects allow drag edits), hard aesthetic guardrails, and a "
        "data-honesty gate that aligns chart numbers with source attachments."
    ),
}

DISPLAY_NAME = {
    "lhg-writing": ("中文写作", "Chinese Writing"),
    "lhg-trend": ("近30天热点扫描", "30-Day Trend Scan"),
    "lhg-net": ("互联网取数层", "Web Fetch Layer"),
    "lhg-slides": ("HTML 演示文稿生成", "HTML Slides"),
}

SKIP = {"README.md", "LICENSE"}
SKIP_DIRS = {".github"}


def replace_exact(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        sys.exit(f"FAIL [{label}]: 未找到待替换文本：\n{old[:120]}")
    return text.replace(old, new)


def remove_self_update_block(text: str, name: str) -> str:
    pattern = re.compile(
        r"## 自更新检查（每次调用时先执行）\n.*?"
        + re.escape(f"4. 用户确认后执行：`npx skills update {name} -y`（当初如用 `-g` 全局安装，可再加 `-g`）。\n\n"),
        re.DOTALL,
    )
    new_text, n = pattern.subn("", text)
    if n != 1:
        sys.exit(f"FAIL [{name}]: 自更新块匹配数 {n} != 1")
    return new_text


def yaml_quote(value: str) -> str:
    """双引号包裹并转义内部双引号，保证 YAML 解析稳健。"""
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def patch_frontmatter(text: str, name: str, old_ver: str) -> str:
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not fm:
        sys.exit(f"FAIL [{name}]: 未找到 frontmatter")
    body = fm.group(1)
    desc = re.search(r'^description: (.+)$', body, re.MULTILINE)
    if not desc:
        sys.exit(f"FAIL [{name}]: frontmatter 无 description")
    desc_val = desc.group(1).strip().strip('"').strip("'")
    # 原始 description 行可能是裸值（含引号会破坏 YAML），统一改为转义加引号
    body = body.replace(
        f"description: {desc.group(1)}",
        f"description: {yaml_quote(desc_val)}",
    )
    if "version:" not in body or f"version: {old_ver}" not in body:
        sys.exit(f"FAIL [{name}]: 版本号与预期 {old_ver} 不符")
    body = body.replace(f"version: {old_ver}", f"version: 1.2.0")
    zh_name, en_name = DISPLAY_NAME[name]
    body += (
        f"\nauthor: 刘洪光"
        f"\ndisplay_name: {yaml_quote(zh_name)}"
        f"\ndisplay_name_en: {yaml_quote(en_name)}"
        f"\ndescription_zh: {yaml_quote(desc_val)}"
        f"\ndescription_en: {yaml_quote(DESCRIPTION_EN[name])}"
    )
    return text[: fm.start(1)] + body + text[fm.end(1):]


def main():
    if DST.exists():
        sys.exit(f"FAIL: {DST} 已存在，避免覆盖请先清理")
    DST.mkdir(parents=True)

    versions = {"lhg-writing": "1.1.1", "lhg-trend": "1.1.0", "lhg-net": "1.1.0", "lhg-slides": "1.1.0"}

    for name, old_ver in versions.items():
        src = SRC / name
        dst = DST / name
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
            *(SKIP | SKIP_DIRS), "README.en.md"))

        skill = dst / "SKILL.md"
        text = skill.read_text(encoding="utf-8")

        text = remove_self_update_block(text, name)
        text = patch_frontmatter(text, name, old_ver)

        if name in ("lhg-writing", "lhg-trend"):
            text = replace_exact(text, ITEM4_LONG_OLD.format(name=name), ITEM4_LONG_NEW, name)
        else:
            text = replace_exact(text, ITEM4_SHORT_OLD, ITEM4_SHORT_NEW, name)

        if name == "lhg-trend":
            text = replace_exact(text, ITEM5_PR_OLD_TREND, ITEM5_PR_NEW, name)
            text = replace_exact(text, SYNC_UPSTREAM_LINES[name], "", name)
            text = replace_exact(text, *TREND_ITEM7, label=name)
        elif name in ("lhg-net", "lhg-slides"):
            text = replace_exact(text, ITEM5_PR_OLD_GENERIC, ITEM5_PR_NEW_GENERIC, name)
            text = replace_exact(text, SYNC_UPSTREAM_LINES[name], "", name)

        old_credit = (
            "## 出品：刘洪光\n\n"
            "本 skill 由真人出镜 IP「刘洪光」（安徽合肥）出品，归属 [lhg-skills](https://github.com/lhg-skills)。\n\n"
            "- GitHub 主页：https://github.com/lhg-skills —— 全部 skill 开源在此，欢迎 star\n"
        )
        text = replace_exact(text, old_credit, "## 出品：刘洪光\n\n本 skill 由真人出镜 IP「刘洪光」（安徽合肥）出品。\n", name)

        skill.write_text(text, encoding="utf-8")

        manifest = dst / "manifest.yaml"
        if manifest.exists():
            m = manifest.read_text(encoding="utf-8")
            m = m.replace(f"version: {old_ver}", "version: 1.2.0")
            manifest.write_text(m, encoding="utf-8")

        print(f"OK [{name}] 改造完成")

    for name in versions:
        subprocess.run(["zip", "-rq", f"{name}.zip", name], cwd=DST, check=True)
        print(f"OK [{name}.zip] 打包完成")


if __name__ == "__main__":
    main()
