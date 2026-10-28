---
name: lls-pptp
display_name: "瀑布流演示页面"
display_name_en: "Vertical Scroll Deck"
description: "生成单文件 HTML 瀑布流演示：幻灯片以单栏卡片竖向排列成可滚动页面，每卡下方配讲者注释，支持卡片间距/注释一键隐藏、全屏键盘放映、可导出 PDF 或 pptx。适合发链接阅读与直播讲解两种场景。当用户提到瀑布流 PPT、网页演示、滚动式幻灯、可滚动 deck、单文件演示页时使用本技能。与翻页式演示 skill 互补：瀑布流竖滚、翻页式翻页。"
description_zh: "单文件 HTML 瀑布流演示：单栏卡片竖向排列、卡片下注释、间距/注释一键隐藏、全屏放映、可导出 PDF/pptx。"
description_en: "Single-file scrolling deck: one-column slide cards with captions, toggleable gaps/notes, fullscreen keyboard presentation, PDF/pptx export."
examples_zh:
  - 把这个大纲做成可以往下滚的网页演示
  - 我要一个发链接就能看的演示页
  - 演示页要能导出成 PDF
examples_en:
  - Turn this outline into a scrolling web deck
  - I need a shareable-link presentation page
  - The deck should export to PDF
version: 1.0.0
author: 刘老师系列
license: MIT
---

# 瀑布流演示页面（lls-pptp 场景技能）

你是竖滚演示构建器。用 `assets/template.html` 起步，交付前必须跑 `scripts/validate-waterfall-deck.mjs`。

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 新建演示 | `assets/template.html` → 复制为 `output/ppt/<标题>/<标题>.html` → 替换卡片块 |
| 选视觉风格 | 从 `@references/style-presets.md` 选一套（除非用户指定） |
| 版式与图表 | `@references/layout-patterns.md`、`@references/data-analysis-charts.md` |
| 插画与内容 | `@references/illustration-system.md`、`@references/content-patterns.md` |
| 导出 | `node scripts/export-waterfall-to-pdf.mjs` / `export-waterfall-to-pptx.mjs` |
| 校验 | `node scripts/validate-waterfall-deck.mjs 演示.html` |

## 处理纪律

1. **一问结构，不问细节**：只确认会影响结构的输入（受众、语言、素材、卡片数、注释长短），语料够就直接做。
2. **一 deck 一目录**：`output/ppt/<标题>/` 下放 HTML 与 `images/`，**不要跨 deck 共用顶层 images 目录**。
3. **风格只选一套**：从预设里挑一个，不要混搭；无官方品牌色时说明假设。
4. **不加页面级标题/导航**：第一屏就是封面卡片，不要额外的 deck 标题栏（除非用户要求）。
5. 🔴 CHECKPOINT：卡片数与注释构成确认后再生成。
6. 交付前跑 validate，并说明"竖滚阅读 + 全屏放映 + 可导出 PDF/pptx"三种用法。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 图片路径失效 | 用相对路径 `images/01-cover.jpg`，确认图片在 deck 目录内 | 转 base64 内嵌（体积换可靠） |
| 2 | 导出 pptx 版式错位 | 跑 validate 看结构问题；pptx 导出对复杂布局支持有限 | 建议交付 PDF 或 HTML |
| 3 | 卡片数过多（>30） | 合并章节或拆分多份 deck | — |
| 4 | 注释太长遮挡内容 | 缩短为要点式；完整稿另存讲稿文件 | — |

## 反例黑名单（不要做）

- **不要**给 deck 加顶部导航栏或 deck 名称标签。
- **不要**跨 deck 共用图片目录。
- **不要**混搭多套视觉风格。
- **不要**跳过 validate 交付。

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

1. **最小冒烟**：
   ```bash
   node --version && node scripts/validate-waterfall-deck.mjs assets/template.html
   ```
2. **定位偏离点**：模板本身通过校验 → 问题在本次替换的内容；模板不通过 → 先修环境。
3. **回归验证**：用模板原样跑一次校验，再逐步替换内容，每步校验。
4. **记录**：反复出现的问题记入上表。
