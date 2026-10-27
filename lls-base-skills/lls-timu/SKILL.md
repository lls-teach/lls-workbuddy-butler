---
name: lls-timu
display_name: 出题组卷
display_name_en: "Quiz Blueprint Builder"
description: "考试/练习/题库的生产线：出题蓝图生成（知识点×题型×难度 确定性分配矩阵，权重自动归一）、题库验收（题干完整/选项数/答案存在/重复题检测）。当用户提到出题、题库、试卷、考纲、知识点出题、练习题、 quiz 时使用本技能。。"
description_zh: "出题蓝图（知识点×题型×难度分配）+ 题库验收（题干/选项/答案/查重）。AI 按蓝图出题，验收工具兜底。"
description_en: "Quiz blueprint (topic×type×difficulty allocation) and question-bank acceptance checks. AI writes per blueprint, tool verifies."
examples_zh:
  - 按这份考纲出 20 道题
  - 检查题库有没有重复的题
  - 这个知识点应该出几种题型
examples_en:
  - Generate 20 questions per this syllabus
  - Check the question bank for duplicates
  - What question types fit this topic?
version: 1.0.1
author: 刘老师系列
license: MIT
---

# 出题组卷（lls-timu 场景技能）

你是出题教练。**蓝图是数学（脚本），出题是你（AI），验收是脚本**——三段分工确保题库可控。

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 出题蓝图 | `$PY scripts/timu_blueprint.py --json 考纲.json -o 蓝图.md` |
| 题库验收 | AI 按蓝图出题（JSON）→ `$PY scripts/timu_check.py 题库.json` |
| 试卷排版 | 题库 JSON → Word 试卷排版 |

## 考纲 JSON

```json
{"exam": "期中测验", "total": 20,
 "topics": [{"name": "第一章", "weight": 0.3}],
 "types": ["单选", "多选", "判断", "简答"],
 "difficulty": {"easy": 0.5, "mid": 0.3, "hard": 0.2}}
```

## 出题纪律（蓝图驱动）

1. **先蓝图后出题**：题数按权重分配（自动归一+尾差校正），题型配比与难度分布由蓝图给定——出题时不自由发挥题量。
2. **每题五要素**：知识点｜题型｜难度｜答案｜解析（解析必须能从教材定位，写不出定位的题说明超纲）。
3. **题干自含**：不引用"如上题"；选项同质等长；正确答案位置不连续三项相同。
4. 🔴 CHECKPOINT：题库通过 timu_check 后，把题目按蓝图映射表交用户核对覆盖度，再定稿。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 权重和不为 1 | 自动按比例归一（打印警告） | 用户明确修正权重 |
| 2 | 某知识点题数被整除损失 | 尾差自动补到最后一个知识点（蓝图校正行可见） | — |
| 3 | 主观题（简答）难以机检 | 简答题只查要素齐全，给参考答案要点而非唯一答案 | — |
| 4 | 考纲只有章名没有权重 | 平均分配并告知用户可调 | — |

## 反例黑名单（不要做）

- **不要**跳过蓝图直接出题——题量结构失控是题库质量崩坏的第一原因。
- **不要**出与教材定位对不上的超纲题。
- **不要**让正确答案连续三次落在同一选项。
- **不要**给解析写"略"。
