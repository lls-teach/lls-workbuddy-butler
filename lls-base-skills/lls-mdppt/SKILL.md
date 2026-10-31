---
name: lls-mdppt
slug: lls-mdppt
display_name: "Markdown转PPT"
displayName: "Markdown转PPT"
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
version: 1.1.0
author: 刘老师系列
license: MIT
---

# Markdown转PPT（lls-mdppt 场景技能）

你是 md → 演示的转换执行器。**结构映射交给脚本（拆页/预算是数学），长段落提炼与风格判断由你完成**。产出直接渲染成 PPT。

## 任务路由

| 用户给什么 | 执行 |
| --- | --- |
| 大纲式 md（#/##/- 结构清晰） | `$PY scripts/mdppt_convert.py 笔记.md -o 大纲.md` → `$PY scripts/mdppt_render.py 笔记.md -o 演示.pptx` |
| 文档式 md（长段落） | 同上 → 大纲中 🔶 提炼位由你提炼成要点 → 🔴 用户确认提炼结果并写回源文档对应位置 → 再用渲染脚本出 .pptx |

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

## 渲染

- 渲染脚本：`$PY scripts/mdppt_render.py 笔记.md -o 演示.pptx`（可选 `--title 封面标题` 覆盖第一个 `#` 标题；无 `#` 首行时封面默认为“演示”）。
- 页数口径：`.pptx` 内容页数 = 转换大纲的页数预算，另加封面 1 页；转换与渲染共用同一分页逻辑（要点 ≤4 条/页、代码 ≤14 行/页、表格 ≤8 行/页，超出拆页不截断）。
- 依赖：渲染需 python-pptx，未装时在虚拟环境内执行 `pip install -r scripts/requirements.txt`；转换本身无第三方依赖。
- Windows 说明：脚本只用标准库（渲染另需 python-pptx 纯 Python 包），路径走 os.path，命令中的 `$PY` 在 Windows 上换成 `python` / `python.exe`；字体只用 Windows 原生字体名（微软雅黑 / Consolas），生成时不依赖本机字体。

## 处理纪律

1. 🔴 CHECKPOINT：转换后把「页数预算 + AI 提炼位清单」展示给用户，提炼结果经确认再渲染。
2. **文案过 lint**：标题与要点先过 `python scripts/taste_lint.py`（tells 见 `references/taste-tells.md`），再渲染。
3. **提炼忠实原文**：要点必须能回溯到原段落——转写不是创作。
4. 代码页 ≤14 行/页，超出拆页；表格 ≤8 行/页。
5. 渲染后重新验收。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | md 是 PPT 大纲语法 | 已兼容（#/##/-/> 原样通过）——无需转换可直接渲染 | — |
| 2 | 无任何标题层级 | 全部按长段落 AI 提炼位处理，量大时先与用户确认提纲 | 让用户先补层级 |
| 3 | 表格列数不齐 | 自动补空单元格；错位严重提示人工核对 | — |
| 4 | md 里有 HTML 标签 | 剥离标签取纯文本 | 提示用户清理 |
| 5 | 渲染报未装 python-pptx | 虚拟环境内 `pip install -r scripts/requirements.txt` 后重跑渲染 | 确认解释器与虚拟环境一致 |

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

**做冒烟测试直到问题解决：冒烟未通过就定位、修复、重跑冒烟，循环往复，直到冒烟全部通过才算完成。**

1. **最小冒烟**（区分环境问题 vs 逻辑问题）：
   ```bash
   $PY -c "import sys" && $PY scripts/mdppt_convert.py --help && $PY scripts/mdppt_render.py --help
   ```
2. **定位偏离点**：冒烟通过 → 问题在本次输入或参数，检查输入后重试；冒烟失败 → 先修依赖与脚本，不碰原任务。
3. **回归验证**：修复后重跑最小冒烟 + 一次真实最小案例，全绿后再回到原任务从失败步骤继续。
4. **记录**：反复出现的问题记入本技能失败分支表，下次直接命中。

## 反例黑名单（不要做）

- **不要**在提炼时加入原文没有的信息。
- **不要**把代码页做成截图——代码保持可编辑文本。
- **不要**跳过 🔶 提炼位的用户确认。
- **不要**对大纲语法的输入重复转换——识别后直接渲染。
