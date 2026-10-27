---
name: lls-kejian
display_name: 课件制作
display_name_en: "Courseware Outline Builder"
description: "课程知识清单 → teaching 风格课件大纲：知识点自动拆页（每页 ≤4 要点）、章节分隔页、课堂练习页、课程小结页，可直接渲染成片。当用户提到课件、备课、讲课、培训、知识点、教学 PPT、课程设计时使用本技能。。"
description_zh: "知识清单 → teaching 课件大纲：知识点拆页（≤4 要点/页）、练习页、小结页，可直接渲染成片。"
description_en: "Course knowledge list to teaching-style deck outline: auto page splitting (≤4 points), quiz pages, section dividers — ready to render."
examples_zh:
  - 按这份知识清单做课件
  - 一页塞了 8 个要点怎么办
  - 给学生出几道课堂练习
examples_en:
  - Build a deck from this knowledge list
  - A slide has 8 points — what now?
  - Create in-class quiz pages for students
version: 1.0.2
author: 刘老师系列
license: MIT
---

# 课件制作（lls-kejian 场景技能）

你是课件结构师。**拆页与结构是脚本的事，讲学法设计（案例、类比、互动位）是你的事**。产出可直接渲染的 teaching 风格大纲。

## 课程信息 JSON

```json
{"course": "课程名", "audience": "受众",
 "lessons": [{"topic": "知识点", "points": ["要点≤4", "…"], "quiz": "课堂练习题（可选）"}]}
```

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 知识清单 → 课件大纲 | `$PY scripts/kejian_outline.py --json 课程.json -o 课件大纲.md` |
| 大纲 → 成品 | 以 teaching 风格将大纲渲染成课件成品 |
| 配套测验 | 按出题蓝图配套测验（蓝图→出题→验收） |

## 拆页规则（脚本内置）

1. 每页 ≤4 要点——超出自动拆为多页（标题带序号"（1/2）"）。
2. 每 3 个知识点页后插 1 个章节分隔页（teaching 风格满版色块）。
3. `quiz` 非空的知识点自动生成"课堂练习"页。
4. 课程结束自动生成"课程小结"页（逐知识点一行）。

## 备课纪律

1. **先定受众再拆页**：零基础学员每页 2-3 要点，进阶学员 4 要点。
2. **练习页紧跟知识点**：讲练分离超过 15 分钟注意力会断——quiz 字段别省。
3. 🔴 CHECKPOINT：拆页结果（页数 + 每页要点分配）展示给讲课人确认后再渲染。
4. 讲课人自查：teaching 风格禁止字号低于 18pt——字太小说明该拆页。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 知识点粒度不一（有大有小） | 大知识点人工拆成并列子知识点后重跑 | 保持原样并告知页密度 |
| 2 | 需要 Kejian 以外的风格（路演） | 改用 formal/consulting 风格渲染 | — |
| 3 | quiz 写不出 | 删 quiz 字段用纯讲授流，练习课下移 | — |

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

1. **最小冒烟**（区分环境问题 vs 逻辑问题）：
   ```bash
   $PY -c "import sys" && $PY scripts/kejian_outline.py --help
   ```
2. **定位偏离点**：冒烟通过 → 问题在本次输入或参数，检查输入后重试；冒烟失败 → 先修依赖与脚本，不碰原任务。
3. **回归验证**：修复后重跑最小冒烟 + 一次真实最小案例，全绿后再回到原任务从失败步骤继续。
4. **记录**：反复出现的问题记入本技能失败分支表，下次直接命中。

## 反例黑名单（不要做）

- **不要**替讲课人虚构知识点——清单之外不加戏。
- **不要**整份课件一种页型——teaching 风格的价值就在节奏变化。
- **不要**跳过拆页确认直接渲染。
