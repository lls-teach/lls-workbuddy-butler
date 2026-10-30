---
name: lls-reportp
display_name: "图文报告页面"
display_name_en: "Source-Backed Report Page"
description: "生成证据型静态 HTML 报告页：叙事章节 + 侧边动态目录 + ECharts 图表 + 表格与图示 + 来源标注，单文件交付可直接编辑。适合研究报告、战略备忘、市场简报、运营更新、技术说明。当用户提到报告页、图文报告、研究报告、市场简报、运营周报页面、带图表的长文时使用本技能。"
description_zh: "证据型 HTML 报告页：叙事章节+动态目录+ECharts 图表+来源标注，单文件可直接编辑。"
description_en: "Source-backed static HTML report: narrative sections, dynamic TOC, ECharts figures, citations — a single editable file."
examples_zh:
  - 把这份数据做成带图表的图文报告页
  - 我需要一份能发链接给老板看的市场简报
  - 报告里要有目录和图表
examples_en:
  - Turn this data into an illustrated report page
  - I need a market brief I can send as a link
  - The report should have a TOC and charts
version: 1.0.1
author: 刘老师系列
license: MIT
---

# 图文报告页面（lls-reportp 场景技能）

你是证据型报告页构建器。**默认手写静态 `index.html`**（配 `assets/doc.css`、`assets/doc.js`，有 Mermaid 图时引 `assets/mermaid.min.js`，有量化图表时引 `assets/echarts.min.js`）——**不要写生成器脚本**，页面本身就是交付物，方便 AI 或人直接改。

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 规划叙事结构 | `@references/story-planning.md` |
| 页面骨架与目录 | `@references/page-structure.md` |
| 选图表类型 | `@references/chart-selection.md` → `@references/data-and-charts.md` |
| 图示与图片 | `@references/media-and-diagrams.md` |
| 交互与输出目录 | `@references/visual-interactions.md`、`@references/output-layout.md` |

## 处理纪律

1. **页面即真相**：不要引入隐藏的生成器/CMS/应用运行时——HTML 文档块直接可读可改。
2. **图表是为结论服务的**：每张 ECharts 图前必须有一句结论句；为配图而配图 = 失败。
3. **来源可查**：引用数据处标来源与时间（报告的可信度全靠这个）。
4. 🔴 CHECKPOINT：报告大纲（章节 + 核心结论 + 图表清单）确认后再生成页面。
5. **体积控制（硬要求）**：`echarts.min.js`(1MB) 随包可用；**Mermaid 图需要时由用户自行下载** `mermaid.min.js` 到 assets/（3.2MB 会超平台包体上限），或改用 echarts/静态 SVG。没图表就不要引入任何库。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 页面过大（>3MB） | 检查是否带了用不到的 mermaid/echarts；图片转 webp | 大图改外链或压缩 |
| 2 | 图表不渲染 | 确认 echarts.min.js 与 html 同目录、初始化在 DOM 后 | 换最小官方示例定位 |
| 3 | 目录不跟随滚动 | 检查 doc.js 是否加载、锚点 id 是否匹配 | 改静态目录列表 |
| 4 | 打印样式差 | 报告以网页为主；需要纸质版时单独排一份适合打印的版本 | — |

## 反例黑名单（不要做）

- **不要**写 Python/JS 生成器来产出这个页面。
- **不要**无来源地写数据（假数据比没数据更糟）。
- **不要**堆砌图表——每张图必须回答一个问题。
- **不要**把报告做成实时数据看板形态。

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

**做冒烟测试直到问题解决：冒烟未通过就定位、修复、重跑冒烟，循环往复，直到冒烟全部通过才算完成。**

1. **最小冒烟**：
   ```bash
   ls assets/echarts.min.js assets/doc.css assets/doc.js 2>/dev/null || echo "缺资源"
   ```
   Windows 下用 PowerShell 等价写法（bash 的 `2>/dev/null` 与 `ls` 在 cmd 下不通用）：
   ```powershell
   Test-Path assets/echarts.min.js, assets/doc.css, assets/doc.js
   ```
   任一结果为 False 即缺资源。另注意：HTML 里 `assets/doc.css` 这类斜杠是 URL 写法，Windows 浏览器同样适用，不要改成反斜杠。
2. **定位偏离点**：资源齐全 → 问题在页面内容/图表配置；资源缺失 → 先补 assets。
3. **回归验证**：浏览器打开最小页面（一段文字 + 一张图）确认渲染，再套用完整内容。
4. **记录**：反复出现的问题记入上表。
