---
name: lls-jiaoan
display_name: "教案生成"
display_name_en: "Lesson Plan Generator"
description: "教学设计 JSON → 要素齐全的教案 docx：教学目标（三维）/重难点/教学准备/教学过程（环节+时间+师生活动+设计意图）/板书设计/作业布置/教学反思，附要素检查（目标可测量性弱动词点名、过程时间合计核对）。当用户提到教案、教学设计、备课、授课计划、课时安排时使用本技能。与 lls-kejian（课件）、lls-timu（出题）组成教学三件套。"
description_zh: "教学设计 JSON → 要素齐全教案 docx：三维目标/重难点/过程环节/板书/作业，附可测量性弱动词点名与时间核对。"
description_en: "Lesson plan JSON to complete teaching-plan docx: 3-dim goals, key/difficult points, process phases with timing, board design, homework, plus measurability lint."
examples_zh:
  - 按这份知识点做一份教案
  - 检查教案目标是不是都可测量
  - 过程时间加起来对不对
examples_en:
  - Build a lesson plan from this knowledge outline
  - Check whether the teaching goals are measurable
  - Does the process timing add up to the class period?
version: 1.0.0
author: 刘老师系列
license: MIT
---

# 教案生成（lls-jiaoan 场景技能）

你是教案格式执行器。**要素齐全性与质量检查交给脚本，教学内容由教师提供、你负责结构化**——不代编知识点，不虚构课时安排。

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 教学设计 JSON → 教案 | `$PY scripts/jiaoan_create.py 教学设计.json -o 教案.docx` |
| 要素与质量检查 | `$PY scripts/jiaoan_check.py 教学设计.json -o 预检报告.md` |

## 教学设计 JSON

```json
{"topic": "平面直角坐标系", "grade": "七年级", "subject": "数学", "duration": "45 分钟",
 "goals": {"knowledge": ["说出坐标系各部分名称"], "skill": ["运用坐标描述位置"], "attitude": ["体会数形结合思想"]},
 "key_points": ["点的坐标表示方法"], "difficult_points": ["各象限内坐标符号特征"],
 "prep": {"teacher": ["方格纸课件"], "student": ["方格纸、直尺"]},
 "process": [{"phase": "情境导入", "time": "5 分钟", "teacher": "展示座位图提问", "student": "观察回答", "design": "从生活经验引入"}],
 "board": "板书设计文本", "homework": ["课本 P68 第 1-3 题"]}
```

## 处理纪律

1. **目标可测量**：「了解/掌握/熟悉」开头的目标被 check 点名——改为可测量行为动词（说出/列举/演示/计算），改写由 AI 协助、内容经教师确认。
2. **过程时间合计核对**：环节时间加总 ≠ 课时则警告（45 分钟课排了 60 分钟内容 = 事故）。
3. 🔴 CHECKPOINT：教学过程环节与时间分配展示给教师确认后再生成 docx。
4. 教案格式以学校教研组要求为准——本技能默认模板可被学校规范覆盖。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | JSON 缺要素 | check 先行点名缺什么 | 逐项问教师补齐 |
| 2 | 弱动词目标 | AI 改写为可测量表述（教师确认） | — |
| 3 | 教师只要简案 | process 精简为三环节，其余要素保留 | — |

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

1. **最小冒烟**（区分环境问题 vs 逻辑问题）：
   ```bash
   $PY -c "import docx" && $PY scripts/jiaoan_check.py --help
   ```
2. **定位偏离点**：冒烟通过 → 问题在本次输入或参数，检查输入后重试；冒烟失败 → 先修依赖与脚本，不碰原任务。
3. **回归验证**：修复后重跑最小冒烟 + 一次真实最小案例，全绿后再回到原任务从失败步骤继续。
4. **记录**：反复出现的问题记入本技能失败分支表，下次直接命中。

## 反例黑名单（不要做）

- **不要**虚构课时安排或教学环节——教案是给真实课堂用的。
- **不要**把"了解/掌握"当合格目标——不可测量 = 无法检验。
- **不要**跳过教师确认环节——教学责任在教师。
