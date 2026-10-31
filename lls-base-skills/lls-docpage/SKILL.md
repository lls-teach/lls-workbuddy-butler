---
name: lls-docpage
slug: lls-docpage
display_name: "文档页生成"
displayName: "文档页生成"
display_name_en: "A4 Document Page Builder"
description: "生成 A4 版式的 HTML 文档页：报告/表单/日程/简历/备忘录/记录六类文档形态，屏幕呈现纸张分页效果，浏览器直接打印成 PDF 或导出 docx。当用户提到文档页、A4 排版、可打印文档、表单生成、简历页面、备忘录、纸质感文档时使用本技能。与可编辑 Word 文档 skill 互补：Word 文档要改，文档页要打印。"
description_zh: "A4 版式 HTML 文档页：报告/表单/日程/简历/备忘六形态，屏幕纸张分页、打印成 PDF、可导出 docx。"
description_en: "A4 HTML document pages: report/form/schedule/resume/memo shapes with on-screen paper pagination, print-to-PDF and docx export."
examples_zh:
  - 帮我做一份 A4 版式的简历页面，能直接打印
  - 这个表单做成可打印的文档页
  - 我想要有纸张分页效果的文档
examples_en:
  - Create an A4 resume page I can print directly
  - Turn this form into a printable document page
  - I want a document with paper-like pagination
version: 1.1.1
author: 刘老师系列
license: MIT
---

# 文档页生成（lls-docpage 场景技能）

你是 A4 文档页构建器。**内容与分页分离**是核心原则：写一份连续的语义文档 → 同一份内容生成屏幕分页预览 → 浏览器打印负责最终 A4 切分。**不要手写"第 1 页/第 2 页"**，除非用户明确要求手工排版。

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 选文档形态 | 先读 `@references/document-types.md` 判定是报告/表单/日程/简历/备忘/记录 |
| 定视觉基调 | `python scripts/taste_deal.py --options 3` 发牌 → `python scripts/taste_cards.py --deal 3` 亮牌面图给用户看，用户选牌（绝不代选；不满意说"重发"）；牌面配色见 `@references/taste-palettes.json`，流程见 `@references/taste-deal.md` |
| 报告类配色 | 读 `@references/research-palettes.md`（科研/医疗/政策/工程） |
| 分页与版心 | `@references/pagination.md`、`@references/typography-print.md` |
| 内容块与图片 | `@references/content-blocks.md`、`@references/images-media.md` |
| 导出 | `$PY scripts/export-paper-to-pdf.mjs` 或 `export-paper-to-docx.mjs`（docx 失败用 `export-paper-docx-fallback.py`） |
| 交付前校验 | `@references/validation.md` 逐项过 |

## 处理纪律

1. **先判文档类型再动手**：把表单/简历/日程硬塞进报告模板 = 形态错误，是本技能最常见的失败。
2. **内容与分页分离**：连续语义 HTML → CSS 分页；手工分页只在用户明说时做。
3. **打印优先**：所有排版以浏览器打印结果为准（用 `theme-smoke-test.html` 做打印预检）。
4. 🔴 CHECKPOINT：文档类型与目标读者确认后再选模板。
5. **审美三件套**：文案先过 `python scripts/taste_lint.py`；出图后按 `@references/taste-critique.md` 看图法过一遍；动笔前可按 `@references/taste-brief-template.md` 写一页简报。
6. 交付时说明三种用法：屏幕阅读 / 打印 PDF / 导出 docx。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 打印后分页断裂（标题孤行/表格截断） | 按 `@references/pagination.md` 加 break-inside-avoid | 手工插入分页符并说明是特例 |
| 2 | docx 导出样式丢失 | 用 `export-paper-docx-fallback.py` 降级方案 | 建议用户直接打印 PDF |
| 3 | Mermaid 图不渲染 | `$PY scripts/render-mermaid-to-svg.mjs` 预渲染成 SVG | 改用静态图片 |
| 4 | 中文字体打印异常 | 指定中文 serif/sans 回退链 | 提示用户系统字体情况 |
| 5 | Windows 下找不到 pandoc / pdfinfo / pdftoppm / mmdc | 确认工具已安装并加入 PATH（脚本在 Windows 下用 where 查找），或用 --pandoc / --pdfinfo / --pdftoppm / --mmdc / --chrome 显式传路径 | 校验与 PNG 渲染缺工具时只跳过该步；PDF 导出可用 `--chrome` 指向系统 Chrome/Edge（playwright 自带浏览器缺失时不必额外下载） |
| 6 | PDF 导出报 `Could not load the Playwright Node package` | 导出脚本依赖 npm 包 playwright：`npm i playwright` 后设 `NODE_PATH` 指向其 node_modules，或装进当前项目 | 浏览器本体用 `--chrome` 指向系统 Chrome/Edge |
| 7 | docx 导出报 `Pandoc was not found, and python-docx fallback was unavailable or failed` | 回退走 PATH 上的 `python`：该解释器必须装 `python-docx` + `lxml`（Windows 上 `python3` 常是垫片或另一个解释器），用 `--python <解释器路径>` 明确指向已装依赖的 venv | 装 pandoc 走 pandoc 路线，或直接交付 PDF |

## 反例黑名单（不要做）

- **不要**把所有文档做成研究报告的样子——形态要匹配用途。
- **不要**手写分页号（除用户要求）。
- **不要**用屏幕样式糊弄打印样式——打印稿是交付物。
- **不要**省略打印预检。

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

1. **最小冒烟**：
   ```bash
   node --version && node scripts/export-paper-to-pdf.mjs --help
   ```
   （导出脚本需 Node；docx 路线需 Python 的 python-docx）
2. **定位偏离点**：冒烟通过 → 问题在本次文档内容或样式；冒烟失败 → 先修环境。
3. **回归验证**：用 `theme-smoke-test.html` 打印预览单元格，确认分页与字体后回原任务。

   **做冒烟测试直到问题解决：冒烟未通过就定位、修复、重跑冒烟，循环往复，直到冒烟全部通过。**
4. **记录**：反复出现的问题记入上表。
