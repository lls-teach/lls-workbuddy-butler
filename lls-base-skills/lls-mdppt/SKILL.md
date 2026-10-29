---
name: lls-mdppt
display_name: "Markdown转PPT"
display_name_en: "Markdown to Slides"
description: "通用 Markdown 一键转演示大纲：# 章节 / ## 内容页 / - 要点 / > 结论 / 代码块 / 表格全部映射，超 4 条要点自动拆页，长段落自动标 AI 提炼位，产出直接渲染成 PPT。当用户提到 markdown 转 PPT、笔记转演示、md 转幻灯片、把文档做成 PPT、大纲转演示时使用本技能。与其他大纲类能力生态互通。"
description_zh: "通用 Markdown 一键转演示大纲：章节/要点/代码/表格全映射，超 4 条自动拆页，长段落标 AI 提炼位，直通 PPT 渲染。"
description_en: "Generic Markdown to slide outline: headings, bullets, code blocks and tables mapped with auto page splitting; feeds the PPT engine directly."
examples_zh:
  - 把这份 markdown 笔记转成 PPT
  - 这篇长文档帮我做成演示
  - md 里的代码块和表格能放进 PPT 吗
examples_en:
  - Convert this markdown note into slides
  - Turn this long document into a presentation
  - Can code blocks and tables go into the deck?
version: 1.0.2
author: 刘老师系列
license: MIT
---

# Markdown转PPT（lls-mdppt 场景技能）

你是 md → 演示的转换执行器。**结构映射交给脚本（拆页/预算是数学），长段落提炼与风格判断由你完成**。产出直接渲染成 PPT。

## 任务路由

| 用户给什么 | 执行 |
| --- | --- |
| 大纲式 md（#/##/- 结构清晰） | `$PY scripts/mdppt_convert.py 笔记.md -o 大纲.md` → 再按大纲渲染成 PPT |
| 文档式 md（长段落） | 同上 → 大纲中 🔶 提炼位由你提炼成要点 → 🔴 用户确认提炼结果 → 再渲染 |

## 映射规则（脚本内置）

| md 语法 | 映射 |
| --- | --- |
| 第一个 `# 标题` | 封面（--title） |
| 其余 `# 标题` | 章节分隔页 |
| `## 标题` | 内容页标题 |
| `- 要点` | 要点行（>4 条自动拆页，标题带序号） |
| `> 引用` | 结论带（蓝色强调） |
| ``` 代码块 | 代码页（等宽字体，≤14 行/页） |
| `\| a \| b \|` 表格 | 表格页 |
| 普通长段落（>80 字） | 🔶 AI 提炼位（提炼成 ≤4 条要点） |

## 处理纪律

1. 🔴 CHECKPOINT：转换后把「页数预算 + AI 提炼位清单」展示给用户，提炼结果经确认再渲染。
2. **提炼忠实原文**：要点必须能回溯到原段落——转写不是创作。
3. 代码页 ≤14 行/页，超出拆页；表格 ≤8 行/页。
4. 渲染后重新验收。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | md 是 PPT 大纲语法 | 已兼容（#/##/-/> 原样通过）——无需转换可直接渲染 | — |
| 2 | 无任何标题层级 | 全部按长段落 AI 提炼位处理，量大时先与用户确认提纲 | 让用户先补层级 |
| 3 | 表格列数不齐 | 自动补空单元格；错位严重提示人工核对 | — |
| 4 | md 里有 HTML 标签 | 剥离标签取纯文本 | 提示用户清理 |

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

1. **最小冒烟**（区分环境问题 vs 逻辑问题）：
   ```bash
   $PY -c "import sys" && $PY scripts/mdppt_convert.py --help
   ```
2. **定位偏离点**：冒烟通过 → 问题在本次输入或参数，检查输入后重试；冒烟失败 → 先修依赖与脚本，不碰原任务。
3. **回归验证**：修复后重跑最小冒烟 + 一次真实最小案例，全绿后再回到原任务从失败步骤继续。
4. **记录**：反复出现的问题记入本技能失败分支表，下次直接命中。

## 反例黑名单（不要做）

- **不要**在提炼时加入原文没有的信息。
- **不要**把代码页做成截图——代码保持可编辑文本。
- **不要**跳过 🔶 提炼位的用户确认。
- **不要**对 lls 大纲语法的输入重复转换——识别后直接渲染。
