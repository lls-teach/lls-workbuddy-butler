#!/usr/bin/env python3
"""出题蓝图：知识点 × 题型 × 难度 的确定性分配矩阵。

用法: python3 timu_blueprint.py --json 考纲.json -o 蓝图.md
JSON: {"exam":"考试名","total":20,
       "topics":[{"name":"章节","weight":0.3}],   # 权重和为 1
       "types":["单选","多选","判断","简答"],       # 可省略，默认均分
       "difficulty":{"easy":0.5,"mid":0.3,"hard":0.2}}
"""
import argparse
import json

from lls_timu_utils import die, ensure_parent

ap = argparse.ArgumentParser()
ap.add_argument("--json", required=True)
ap.add_argument("-o", "--output", required=True)
args = ap.parse_args()

data = json.load(open(args.json, encoding="utf-8"))
total = data.get("total", 20)
topics = data.get("topics", [])
types = data.get("types") or ["单选", "多选", "判断", "简答"]
diff = data.get("difficulty") or {"easy": 0.5, "mid": 0.3, "hard": 0.2}
if not topics:
    die("topics 为空")
wsum = sum(t.get("weight", 0) for t in topics)
if wsum == 0:
    # SKILL.md 失败分支 4：只有章名没有权重时平均分配，而非全补到最后一个知识点
    print("[lls-timu] ⚠️ 权重均缺失或为 0，已平均分配（可再手动调整权重）")
    weights = [1 / len(topics)] * len(topics)
elif abs(wsum - 1) > 0.01:
    print(f"[lls-timu] ⚠️ 权重和为 {wsum:.2f}（非 1），已按比例归一")
    weights = [t.get("weight", 0) / wsum for t in topics]
else:
    weights = [t.get("weight", 0) for t in topics]

lines = [f"# 出题蓝图：{data.get('exam', '试卷')}（共 {total} 题）", "",
         "| 知识点 | 权重 | 题数 |", "|---|---|---|"]
alloc = []
acc = 0
for i, t in enumerate(topics):
    w = weights[i]
    n = round(total * w) if i < len(topics) - 1 else total - acc
    acc += n
    alloc.append((t["name"], w, n))
    lines.append(f"| {t['name']} | {w*100:.0f}% | {n} |")
if acc != total:
    lines.append(f"| （校正） | | {total - acc} |")

lines += ["", "## 每个知识点的题型 × 难度分配（AI 按此出题）", ""]
dsum = sum(diff.values())
if dsum == 0:
    diff = {k: 1 for k in diff}
    dsum = sum(diff.values())
for name, w, n in alloc:
    if n <= 0:
        type_counts = [0] * len(types)
    elif n < len(types):
        # 小题量时旧写法 max(1, n // len) 会让题型数之和超过 n（如 1 题变 3 题）
        type_counts = [1 if ti < n else 0 for ti in range(len(types))]
    else:
        per_type = n // len(types)
        type_counts = [per_type] * len(types)
        type_counts[-1] += n - per_type * len(types)
    talloc = [f"{t}×{cnt}" for t, cnt in zip(types, type_counts)]
    # 难度按本知识点题数 n 分配（旧写法按 total*w 取整，小题量时和为 0 且与 n 脱节）；
    # 最大余数法保证各难度数之和恰好等于 n，且权重和为 1 时与旧输出一致
    raw = [n * v / dsum for v in diff.values()]
    base = [int(x) for x in raw]
    left = n - sum(base)
    order = sorted(range(len(raw)), key=lambda i: (-(raw[i] - base[i]), i))
    for i in order[:left]:
        base[i] += 1
    d = " / ".join(f"{k}×{cnt}" for k, cnt in zip(diff.keys(), base))
    lines.append(f"- **{name}**（{n} 题）：{'、'.join(talloc)}｜难度 {d}")

lines += ["", "## 出题纪律", "- 题干自含完整条件，不引用\"如上题\"；选项同质等长；正确答案位置随机分布不连续三项相同。",
          "- 每题标注：知识点 | 题型 | 难度 | 答案 | 解析（解析必须能从教材定位）。"]
ensure_parent(args.output)
open(args.output, "w", encoding="utf-8").write("\n".join(lines))
print(f"[lls-timu] 蓝图 → {args.output}（{len(topics)} 知识点 / {total} 题）")
