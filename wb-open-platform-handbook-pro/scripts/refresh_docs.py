#!/usr/bin/env python3
"""刷新 wb-open-platform-handbook 的官方文档缓存。

用法：python3 scripts/refresh_docs.py
行为：抓取 WorkBuddy 开放平台 16 个官方文档页，剥离脚本/样式后抽取正文，
     写入 references/cache/{slug}.md 并打上抓取日期戳。
     之后由 AI 对照 cache 与各参考文件，把变化蒸馏回 references/*.md 并更新基准日期。

依赖：python3 标准库（urllib/re/html），无需第三方包。需要网络。
文档站为服务端渲染，无需执行 JS。
"""
import html
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

PAGES = [
    "what-is-open-platform", "onboarding", "skill", "expert", "expert-team",
    "connector", "buddy-app", "third-party-app", "openapi", "monetization",
    "operations-data", "developer-profile", "service-categories-individual",
    "service-categories-enterprise", "legal-basis-and-examples", "contact",
]

BASE = Path(__file__).resolve().parent.parent
CACHE = BASE / "references" / "cache"
UA = {"User-Agent": "Mozilla/5.0 (skill: wb-open-platform-handbook doc refresher)"}


def to_text(seg: str) -> str:
    seg = re.sub(r'<img[^>]*alt="([^"]*)"[^>]*>', r'\n![图: \1]\n', seg)
    seg = re.sub(r"<(h[1-6])[^>]*>", lambda m: "\n\n" + "#" * int(m.group(1)[1]) + " ", seg)
    seg = re.sub(r"<li[^>]*>", "\n- ", seg)
    seg = re.sub(r"</(p|div|tr|table|pre|h[1-6]|ul|ol|blockquote)>", "\n", seg)
    seg = re.sub(r"<(p|div|tr|table|pre|br|ul|ol|blockquote)[^>]*>", "\n", seg)
    seg = re.sub(r"<(td|th)[^>]*>", " | ", seg)
    seg = re.sub(r"<[^>]+>", "", seg)
    seg = html.unescape(seg)
    seg = re.sub(r"[ \t]+\n", "\n", seg)
    return re.sub(r"\n{3,}", "\n\n", seg).strip()


def fetch(slug):
    url = f"https://open.workbuddy.cn/docs/{slug}"
    try:
        raw = urllib.request.urlopen(
            urllib.request.Request(url, headers=UA), timeout=30
        ).read().decode("utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"{slug}: FETCH FAILED {exc}")
        return None
    raw = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.S)
    raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.S)
    i = raw.find("prose-docs_root")
    if i < 0:
        print(f"{slug}: no prose content (page layout may have changed)")
        return None
    start = raw.rfind("<div", 0, i)
    end = raw.find("</main>", start)
    header = f"# 官方文档原文：/docs/{slug}\n> 抓取日期：{date.today().isoformat()}\n"
    return header + "\n" + to_text(raw[start : end if end > 0 else len(raw)])


def main() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    ok = 0
    for slug in PAGES:
        text = fetch(slug)
        if text:
            (CACHE / f"{slug}.md").write_text(text, encoding="utf-8")
            ok += 1
            print(f"{slug}: {len(text)} chars -> references/cache/{slug}.md")
    print(f"\nDONE {ok}/{len(PAGES)} pages cached on {date.today().isoformat()}")
    print("Next: distill changes from cache/ back into references/*.md,")
    print("update the knowledge date in SKILL.md, then clear cache/ if desired.")
    return 0 if ok == len(PAGES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
