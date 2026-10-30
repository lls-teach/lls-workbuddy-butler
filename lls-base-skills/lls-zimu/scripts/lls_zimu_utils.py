"""lls-zimu 共享工具：SRT 解析/写出、口头禅与替换清洗、台词对齐。"""
import difflib
import os
import re
import sys

SRT_TIME = re.compile(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})")
FILLERS = ["嗯", "啊", "呃", "就是说", "然后然后", "这个这个", "对对对", "那个那个"]


def die(msg, code=1):
    print(f"[lls-zimu] 错误: {msg}", file=sys.stderr)
    sys.exit(code)


def ensure_parent(path):
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    return path


def parse_srt(text: str) -> list[dict]:
    """SRT → [{idx, start, end, text}]；容错解析，坏块跳过并计数。"""
    blocks, bad = [], 0
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [l for l in block.split("\n") if l.strip()]
        if len(lines) < 2:
            bad += 1
            continue
        m = SRT_TIME.search(lines[1]) if len(lines) > 1 else None
        if not m and len(lines) > 2:
            m = SRT_TIME.search(lines[0])
            lines = lines[1:]
        if not m:
            bad += 1
            continue
        g = [int(x) for x in m.groups()]
        blocks.append({
            "idx": len(blocks) + 1,
            "start": g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000,
            "end": g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000,
            "text": " ".join(l.strip() for l in lines[2:]).strip(),
        })
    return blocks, bad


def write_srt(blocks: list[dict], path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    out = []
    for i, b in enumerate(blocks, 1):
        def ts(sec):
            # 先换算成总毫秒再拆分，避免 59.9999 秒四舍五入出 “,1000” 这种非法时间码。
            total_ms = int(round(sec * 1000))
            h, rem = divmod(total_ms, 3600000)
            mnt, rem = divmod(rem, 60000)
            s, ms = divmod(rem, 1000)
            return f"{h:02d}:{mnt:02d}:{s:02d},{ms:03d}"
        out.append(str(i))
        out.append(f"{ts(b['start'])} --> {ts(b['end'])}")
        out.append(b["text"])
        out.append("")
    # newline="\n"：钉死 LF，Windows 文本模式不再把换行写成 CRLF，跨平台输出字节一致。
    open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out))


def clean_text(text: str, replacements: dict[str, str] | None = None, dedupe: bool = True,
               do_fillers: bool = True, do_typos: bool = True) -> tuple[str, int, int]:
    """清洗单条字幕：口头禅删除 + 替换表。返回 (新文本, 口头禅数, 替换数)。

    注：dedupe 参数仅为兼容旧调用保留，块级去重（真删块）由调用方做，
    本函数只改单条文本、不删块。do_fillers/do_typos 为各单项的开关。
    """
    filler_n = 0
    if do_fillers:
        for f in FILLERS:
            n = text.count(f)
            if n:
                filler_n += n
                text = text.replace(f, "")
    rep_n = 0
    if do_typos and replacements:
        for old, new in replacements.items():
            n = text.count(old)
            if n:
                rep_n += n
                text = text.replace(old, new)
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text, filler_n, rep_n


def align_script(script: str, subtitles: list[str]) -> list[tuple[str, str, str]]:
    """脚本 vs 实录字幕 对齐：difflib 字符级 diff → (操作, 脚本词, 实录词)。"""
    script_flat = re.sub(r"\s", "", script)
    sub_flat = re.sub(r"\s", "", "".join(subtitles))
    sm = difflib.SequenceMatcher(None, script_flat, sub_flat, autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "replace" and (i2 - i1 >= 2 or j2 - j1 >= 2):
            out.append(("改", script_flat[i1:i2], sub_flat[j1:j2]))
        elif tag == "delete" and i2 - i1 >= 2:
            out.append(("漏", script_flat[i1:i2], ""))
        elif tag == "insert" and j2 - j1 >= 2:
            out.append(("增", "", sub_flat[j1:j2]))
    return out
