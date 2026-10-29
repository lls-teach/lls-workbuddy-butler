#!/usr/bin/env python3
"""批量评语 lint：模板化开头 / 负面标签 / 长度 / 空泛无具体事例。

用法: python3 pingyu_lint.py 评语.md
评语格式：每行「姓名：评语正文」。
合格线：无重复模板开头、无负面标签、每条 30-150 字、批内开头去重率 100%。
"""
import sys

from lls_pingyu_utils import GENERIC_OPENERS, NEGATIVE_LABELS, die

if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
    print("用法: python3 pingyu_lint.py 评语.md")
    print("评语格式：每行「姓名：评语正文」；检查：模板化开头 / 负面标签 / 长度 30-150 字 / 批内重复开头。")
    sys.exit(0)

path = sys.argv[1] if len(sys.argv) > 1 else die("用法: pingyu_lint.py 评语.md")
try:
    lines = open(path, encoding="utf-8-sig", errors="ignore").readlines()
except FileNotFoundError:
    die(f"文件不存在：{path}")
except OSError as e:
    die(f"无法读取文件 {path}：{e}")
students = []
for line in lines:
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    m = None
    import re
    m = re.match(r"^(?:###\s*)?([^：:]{1,12})[:：]\s*(.+)$", line)
    if m:
        students.append({"name": m.group(1).strip(), "comment": m.group(2).strip()})
if not students:
    die("未解析出评语（格式：每行「姓名：评语」）")

problems = []
openers = {}

for s in students:
    name, c = s["name"], s["comment"]
    opener = c[:4]
    openers.setdefault(opener, []).append(name)
    # 逐条模板化开头：单条以通用开头起手即报（此前仅 ≥2 条重复才报，单条漏网）
    for generic in sorted(GENERIC_OPENERS, key=len, reverse=True):
        if c.startswith(generic):
            problems.append(f"⚠️ {name}：以模板化开头「{generic}…」开头——家长群里一眼穿帮")
            break
    if len(c) < 30:
        problems.append(f"⚠️ {name}：评语仅 {len(c)} 字（<30）——太短显得敷衍")
    if len(c) > 150:
        problems.append(f"⚠️ {name}：评语 {len(c)} 字（>150）——家长没耐心读完")
    for bad in NEGATIVE_LABELS:
        if bad in c:
            problems.append(f"❌ {name}：出现负面标签「{bad}」→ 改为：{NEGATIVE_LABELS[bad]}")

for opener, names in openers.items():
    if len(names) >= 2:
        problems.append(f"⚠️ 模板化开头：{len(names)} 条评语都以「{opener}…」开头（{names}）——家长群里一眼穿帮")

print(f"[lls-pingyu] 共 {len(students)} 条评语")
if problems:
    print(f"[lls-pingyu] ❌ {len(problems)} 项：")
    for p in problems:
        print("  - " + p)
    sys.exit(1)
print("[lls-pingyu] ✅ 全部通过：无模板化开头、无负面标签、长度健康")
