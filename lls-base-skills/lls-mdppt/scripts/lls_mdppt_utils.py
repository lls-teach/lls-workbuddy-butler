"""lls-mdppt 共享工具：通用 markdown → 演示大纲的解析与拆页。"""
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


def parse_md(md_text: str) -> dict:
    """通用 md → 结构。

    # 一级标题     → 章节分隔页 / deck 标题（首个）
    ## 二级标题    → 内容页标题
    - 要点         → 要点（自动拆页：每页 ≤4 条）
    > 引用         → 结论带
    ``` 代码块 ``` → 代码页
    | a | b |      → 表格页（连续行）
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
            cur_slide = slides[-1] if slides else None
            if cur_slide and cur_slide.get("kind") == "bullets" and not cur_slide["bullets"]:
                cur_slide.update(kind="table", table=table_buf)
            else:
                slides.append({"kind": "table", "title": cur_slide["title"] if cur_slide else "表格",
                               "table": table_buf})
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
        if line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not re.match(r"^[-: ]+$", line.strip("|")):
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
    if in_code and code_buf:
        slides.append({"kind": "code", "title": "代码", "code": (code_lang, "\n".join(code_buf))})
    return {"slides": slides}
