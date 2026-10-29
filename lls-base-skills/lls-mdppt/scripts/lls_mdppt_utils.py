"""lls-mdppt 共享工具：通用 markdown → 演示大纲的解析与拆页。

本模块只用 Python 标准库，不调用外部命令、不读写固定路径，
路径处理一律走 os.path，因此在 Windows / macOS / Linux 上行为一致。
换行由 open() 的通用换行模式处理，CRLF 输入与 LF 输入解析结果相同。
"""
import re


def die(msg, code=1):
    import sys
    print(f"[lls-mdppt] 错误: {msg}", file=sys.stderr)
    sys.exit(code)


def ensure_parent(path):
    import os
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path


def _is_separator_row(cells):
    """表格分隔行：每个单元格都是 - / : 的组合，如 ---、:---、---:、:---:。"""
    return bool(cells) and all(re.match(r"^:?-+:?$", c) for c in cells)


def _normalize_table(rows):
    """列数不齐时补空单元格到最宽行的列数（不丢数据、不截断超长行）。"""
    if not rows:
        return rows
    width = max(len(r) for r in rows)
    return [list(r) + [""] * (width - len(r)) for r in rows]


def _chunks(seq, size):
    size = max(1, int(size))
    return [list(seq[i:i + size]) for i in range(0, len(seq), size)]


def _suffixed(title, index, total):
    if total > 1:
        return f"{title}（{index + 1}/{total}）"
    return title


def parse_md(md_text: str) -> dict:
    """通用 md → 结构。

    # 一级标题     → 章节分隔页 / deck 标题（首个）
    ## 二级标题    → 内容页标题
    - 要点         → 要点（自动拆页：每页 ≤4 条）
    > 引用         → 结论带
    ``` 代码块 ``` → 代码页
    | a | b |      → 表格页（连续行，分隔行剥离）
    普通段落       → 段落页（长段落标 AI 提炼位）
    """
    slides = []
    cur = None
    in_code = False
    code_buf, code_lang = [], ""
    table_buf = []

    def flush_table():
        nonlocal table_buf
        if table_buf:
            table = _normalize_table(table_buf)
            cur_slide = slides[-1] if slides else None
            if cur_slide and cur_slide.get("kind") == "bullets" and not cur_slide["bullets"]:
                # 表格紧跟 ## 标题：把该空标题页转为表格页，标题继承该标题。
                cur_slide.update(kind="table", table=table)
            else:
                # 表格不跟在空标题页后时用通用标题“表格”，绝不借用上一页
                #（如代码页）的标题——此前 bug 会把表格标成“## 代码”。
                slides.append({"kind": "table", "title": "表格", "table": table})
            table_buf = []

    def new_slide(kind, title=""):
        flush_table()
        cur = {"kind": kind, "title": title, "bullets": [], "takeaway": None, "code": None, "table": [], "para": None}
        slides.append(cur)
        return cur

    for raw in md_text.split("\n"):
        line = raw.rstrip()
        if line.strip().startswith("```"):
            flush_table()
            if in_code:
                cur = slides[-1] if slides else None
                if cur and cur.get("kind") == "code":
                    cur["code"] = code_lang, "\n".join(code_buf)
                in_code, code_buf = False, []
            else:
                flush_table()
                cur = new_slide("code", "代码")
                in_code, code_lang, code_buf = True, line.strip("`").strip(), []
            continue
        if in_code:
            code_buf.append(raw)
            continue
        if not line.strip():
            flush_table()
            continue
        sline = line.strip()
        if sline.startswith("|") and sline.endswith("|"):
            cells = [c.strip() for c in sline.strip("|").split("|")]
            if not _is_separator_row(cells):
                table_buf.append(cells)
            continue
        flush_table()
        if line.startswith("# ") and not any(s["kind"] == "cover" for s in slides):
            slides.append({"kind": "cover", "title": line[2:].strip()})
        elif line.startswith("# "):
            slides.append({"kind": "section", "title": line[2:].strip()})
        elif line.startswith("## "):
            cur = new_slide("bullets", line[3:].strip())
        elif line.startswith("### "):
            cur = new_slide("bullets", line[4:].strip())
        elif line.startswith("- ") or line.startswith("* "):
            if cur is None:
                cur = new_slide("bullets", "")
            cur["bullets"].append(line[2:].strip())
        elif line.startswith("> "):
            if cur is None:
                cur = new_slide("bullets", "")
            cur["takeaway"] = line[2:].strip()
        else:
            if cur is None or cur.get("kind") not in ("para", "bullets"):
                cur = new_slide("para", "")
                cur["para"] = line.strip()
            elif cur.get("kind") == "para":
                cur["para"] += " " + line.strip()
            else:
                cur["bullets"].append(line.strip())
    flush_table()
    if in_code:
        # 未闭合代码块：把内容填回打开时已建的代码页，不再另起一页
        #（此前 bug 会多出一张空白代码页 + 一张重复代码页）。
        target = cur if cur and cur.get("kind") == "code" else None
        if target is None and slides and slides[-1].get("kind") == "code":
            target = slides[-1]
        if target is not None:
            target["code"] = code_lang, "\n".join(code_buf)
        elif code_buf:
            slides.append({"kind": "code", "title": "代码", "code": (code_lang, "\n".join(code_buf))})
    return {"slides": slides}


def iter_pages(slides, max_bullets=4):
    """把解析出的结构块展开为逐页数据。

    转换器（mdppt_convert.py）与渲染器（mdppt_render.py）共用本函数，
    因此大纲的页数预算与 .pptx 的内容页数必然一致（另加封面 1 页）。
    拆页规则：要点 ≤max_bullets 条/页、代码 ≤14 行/页、表格 ≤8 行/页，
    超出拆页（不再截断），多页时标题带（i/n）后缀。
    """
    pages = []
    for sl in slides:
        kind = sl["kind"]
        if kind == "cover":
            pages.append({"kind": "cover", "title": sl["title"]})
            continue
        if kind == "section":
            pages.append({"kind": "section", "title": sl["title"]})
            continue
        if kind == "code":
            lang, code = sl.get("code") or ("", "")
            lines = code.split("\n") if code else []
            chunks = _chunks(lines, 14) if lines else [[]]
            title = sl["title"] or "代码"
            for ci, chunk in enumerate(chunks):
                pages.append({"kind": "code", "title": _suffixed(title, ci, len(chunks)),
                              "lines": chunk, "lang": lang})
            continue
        if kind == "table":
            rows = _normalize_table(sl["table"])
            chunks = _chunks(rows, 8) if rows else [[]]
            title = sl["title"] or "表格"
            for ci, chunk in enumerate(chunks):
                pages.append({"kind": "table", "title": _suffixed(title, ci, len(chunks)),
                              "rows": chunk, "chunk_index": ci})
            continue
        if kind == "para":
            text = sl.get("para", "") or ""
            if len(text) > 80:
                pages.append({"kind": "para", "title": f"🔶 提炼：{text[:40]}…",
                              "bullets": [f"（AI 提炼位）将以下段落提炼为 ≤{max_bullets} 条要点：",
                                          f"原文：{text[:200]}"],
                              "para": text, "ai_spot": True})
            else:
                pages.append({"kind": "para", "title": text[:40],
                              "bullets": [], "para": text, "ai_spot": False})
            continue
        # bullets 页（自动拆页）
        title = sl.get("title", "")
        bullets = sl.get("bullets", [])
        take = sl.get("takeaway")
        chunks = _chunks(bullets, max_bullets) if bullets else [[]]
        for ci, chunk in enumerate(chunks):
            pages.append({"kind": "bullets", "title": _suffixed(title, ci, len(chunks)),
                          "bullets": chunk,
                          "takeaway": take if ci == len(chunks) - 1 else None})
    return pages
