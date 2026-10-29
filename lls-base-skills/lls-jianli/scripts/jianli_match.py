#!/usr/bin/env python3
"""JD × 简历 关键词匹配分析 → Markdown 报告（覆盖/缺失/建议，不做伪精确打分）。

用法: python3 jianli_match.py --jd 岗位描述.txt --resume 简历.json -o 匹配报告.md
简历侧语料 = summary + 经历/项目 bullets + skills。
"""
import argparse
import json

from lls_jianli_utils import die, ensure_parent, extract_keywords


def resume_text(data: dict) -> str:
    parts = [data.get("summary", ""), " ".join(data.get("skills", []))]
    for block in ("experience", "projects", "education"):
        for item in data.get(block, []):
            parts.append(" ".join(str(v) for v in item.values() if isinstance(v, str)))
            parts.extend(item.get("bullets", []))
    return " ".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jd", required=True)
    ap.add_argument("--resume", required=True, help="简历 JSON")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    try:
        with open(args.jd, encoding="utf-8", errors="ignore") as f:
            jd = f.read()
    except FileNotFoundError:
        die(f"找不到 JD 文件: {args.jd}")
    if len(jd.strip()) < 50:
        die("JD 文本太短（<50 字），无法做有效匹配——请补全岗位职责与任职要求")
    try:
        with open(args.resume, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        die(f"找不到简历 JSON: {args.resume}")
    except json.JSONDecodeError as e:
        die(f"简历 JSON 解析失败: {e}（请检查 JSON 格式）")
    rtext = resume_text(data)

    keywords = extract_keywords(jd)
    covered = [k for k in keywords if k.lower() in rtext.lower()]
    missing = [k for k in keywords if k not in covered]
    ratio = f"{len(covered)}/{len(keywords)}"

    lines = [
        "# JD × 简历 匹配分析",
        "",
        f"- 关键词覆盖：**{ratio}**（只列覆盖/缺失清单，不输出伪精确分数）",
        f"- 简历语料：summary + {len(data.get('experience', []))} 段经历 + {len(data.get('projects', []))} 个项目 + 技能",
        "",
        "## ✅ 已覆盖关键词（面试时可主动展开的证据点）",
        "",
        "，".join(covered) if covered else "（无）",
        "",
        "## ⚠️ 缺失关键词（逐个判断：真缺 → 补课或诚实面对；有相关经验但没写 → 改写简历）",
        "",
    ]
    for k in missing:
        lines.append(f"- **{k}**：简历全文未出现。若有相关经历请改写进对应 bullet（量化）；若确无，面试时准备「学习路径」说法。")
    lines += [
        "",
        "## 面试题框架（按缺失关键词逐个出题，AI 生成题干）",
        "",
        "对每个缺失关键词出 1 道场景题 + 1 道追问题；对每个已覆盖关键词出 1 道深挖题（追问数字口径）。",
    ]
    ensure_parent(args.output)
    open(args.output, "w", encoding="utf-8").write("\n".join(lines))
    print(f"[lls-jianli] 匹配报告 → {args.output}（覆盖 {len(covered)}，缺失 {len(missing)}）")


if __name__ == "__main__":
    main()
