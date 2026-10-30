---
name: lls-pptp
slug: lls-pptp
display_name: "瀑布流演示页面"
displayName: "瀑布流演示页面"
display_name_en: "Vertical Scroll Deck"
description: "生成单文件 HTML 瀑布流演示：幻灯片以单栏卡片竖向排列成可滚动页面，每卡下方配讲者注释，支持卡片间距/注释一键隐藏、全屏键盘放映、可导出 PDF 或 pptx。适合发链接阅读与直播讲解两种场景。当用户提到瀑布流 PPT、网页演示、滚动式幻灯、可滚动 deck、单文件演示页时使用本技能。同一文件覆盖竖滚阅读与全屏放映两种用法。"
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
version: 1.0.1
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
7. **首行与注释**：`<!doctype html>` 必须保持首行，来源注释 `<!-- deck: 标题 -->` 放在 `<head>` 内前部，不要把注释移到 doctype 之前（会触发 quirks 模式、可能破坏布局）。
8. **跨平台路径**：脚本一律用 `node scripts/...` 调用（不要直接执行 `.mjs`）；标题作目录/文件名时去掉 Windows 非法字符 `\ / : * ? " < > |`；含空格或中文的路径调用命令时加引号；HTML 内图片路径一律用正斜杠 `images/...`，不要用反斜杠；导出找不到浏览器时可用 `--browser-executable` 指定 Chrome/Edge，或设 `PLAYWRIGHT_CHROMIUM_EXECUTABLE`。
9. **导出依赖**：导出脚本依赖 npm 包 `playwright` 与 `pdf-lib`，技能包不自带——先 `npm i playwright pdf-lib`，再用 `--node-modules <装依赖的目录>` 指过去（或设 `NODE_PATH`）。playwright 自带浏览器缺失时会自动回退到系统 Chrome/Edge，不必再下载 playwright 浏览器。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 图片路径失效 | 用相对路径 `images/01-cover.jpg`，确认图片在 deck 目录内 | 转 base64 内嵌（体积换可靠） |
| 2 | 导出 pptx 版式错位 | 跑 validate 看结构问题；pptx 导出对复杂布局支持有限 | 建议交付 PDF 或 HTML |
| 3 | 卡片数过多（>30） | 合并章节或拆分多份 deck | — |
| 4 | 注释太长遮挡内容 | 缩短为要点式；完整稿另存讲稿文件 | — |
| 5 | 导出报 `Cannot resolve playwright` / `Cannot resolve pdf-lib` | 导出依赖不在技能包内：`npm i playwright pdf-lib` 后用 `--node-modules <该目录>` 指过去 | 用浏览器"打印为 PDF"兜底交付 |
| 6 | 导出报 `net::ERR_FILE_NOT_FOUND`（且路径很长） | deck 完整路径超过 260 字符时 Chrome 打不开该 `file://` 地址：把 deck 移到更短路径（如 `D:\decks\`）再导出 | `validate` 走 Node 不受此限，可先在原处校验再搬迁 |
| 7 | 导出报 `Cannot resolve @oai/artifact-tool` | pptx 导出依赖私有包，npm 上不可得：改用 PDF 或直接交付 HTML | 需要可编辑 pptx 时手工重建 |

## 反例黑名单（不要做）

- **不要**给 deck 加顶部导航栏或 deck 名称标签。
- **不要**跨 deck 共用图片目录。
- **不要**混搭多套视觉风格。
- **不要**跳过 validate 交付。

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

**做冒烟测试直到问题解决：冒烟未通过就定位、修复、重跑冒烟，循环往复，直到冒烟全部通过才算完成——冒烟未通过时不要交付。**

1. **最小冒烟**：
   ```bash
   node --version && node scripts/validate-waterfall-deck.mjs assets/template.html
   ```
2. **定位偏离点**：模板本身通过校验 → 问题在本次替换的内容；模板不通过 → 先修环境。
3. **回归验证**：用模板原样跑一次校验，再逐步替换内容，每步校验。
4. **记录**：反复出现的问题记入上表。
