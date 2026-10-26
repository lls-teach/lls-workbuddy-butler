---
name: liulaoshi-slides-pptx
description: 生成和修改 .pptx 演示文稿的技能。用户要做新 PPT、按截图/大纲/PDF 重做幻灯片、改现有 PPT 内容但保持可编辑、加图表或图片，或反馈版式问题（溢出、重叠、字体被替换）时使用。触发词：做个 PPT、幻灯片、演示文稿、改一下这页、加页、做成 pptx。
description_zh: "用 PptxGenJS 生成结构化 .pptx：先大纲定骨架、母版三件套定版式，再逐页生成，最后用 python-pptx 回读做溢出与字体校验，交付完全可编辑的文稿。"
description_en: "Build structured .pptx decks with PptxGenJS: outline first, define a three-piece master layout, generate page by page, then validate with a python-pptx read-back pass (overflow and font checks) and deliver a fully editable file."
version: 1.0.0
author: 刘洪光
---

# 刘老师 · PPTX 生成与修改

## 交付承诺

产出的 .pptx 必须**完全可编辑**：文字是文本框、图表是原生图表、版式可以在 PowerPoint/WPS 里直接改。不接受"截图拼成的假 PPT"。

## 工作流

### 第 0 步：定骨架（用户没给大纲时必做）

把用户的材料整理成一页一句话的大纲：每页一个论点 + 一行支撑证据。页数守规律——10 分钟演讲 ≤12 页，30 分钟 ≤25 页。大纲给用户过目一次再动手。

### 第 1 步：母版三件套

开工前先定死三件事，之后所有页面遵守，不许页页即兴：

1. **网格**：16:9（13.33×7.5 英寸），页边距 0.6 英寸，标题区固定高度
2. **字体**：中文标题/正文各定一款（如思源黑体/微软雅黑），字号梯度：页标题 28–32pt、正文 16–20pt、注释 12pt
3. **颜色**：主色 1 + 强调色 1 + 灰阶 2，写死 hex 值；图表颜色从中派生

### 第 2 步：用 PptxGenJS 生成

单脚本产出全部页面，常用写法：

```js
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.defineLayout({ name: "W16x9", width: 13.33, height: 7.5 });
pres.layout = "W16x9";

// 文本页
const slide = pres.addSlide();
slide.addText("页标题", { x: 0.6, y: 0.4, w: 12.1, h: 0.8, fontSize: 30, bold: true });
slide.addText("正文要点", { x: 0.6, y: 1.6, w: 7.5, h: 5.2, fontSize: 18 });

// 原生图表
slide.addChart(pres.ChartType.bar, data, { x: 8.4, y: 1.6, w: 4.3, h: 5.2 });

pres.writeFile({ fileName: "deck.pptx" });
```

### 第 3 步：回读校验（交付前必做）

用 python-pptx 把生成的文件读回来检查，两项硬门禁：

- **溢出**：文本框估算行数 × 行高超出框高即报警；表格行数超过版心即报警
- **字体**：检查每个 run 的字体是否为母版规定字体；出现 Calibri/宋体回退即报警

校验不过就改参数重生成，不交付带病文件。需要视觉确认时，用 LibreOffice `soffice --convert-to pdf` 转图抽查关键页。

### 第 4 步：修改已有 PPT

用户给来现成文件要改内容时：用 python-pptx 定位目标页的 shape 直接改文本，**不要整页重做**——保留用户原有的母版、动画和备注。改完同样过第 3 步校验。

## 版式节奏

- 每页一个论点；超过 3 个论点拆页
- 全文字页与全图页交替；连续 3 页同版式时插入一页过渡（大字观点页或章节页）
- 页码 + 章节标记常驻；封面写清标题/副标题/日期/汇报人四件套

## 环境说明

- PptxGenJS 需要 Node 环境 `npm i pptxgenjs`；python-pptx 需要 `pip install python-pptx`
- 两个依赖都不可用时：退级为生成大纲 + 每页文案 + 版式说明的 Markdown，交由用户在 Office 里组装，并说明原因
- 中文字体嵌入：提示用户在 PowerPoint 选项里勾选"嵌入字体"后再分发，避免对方机器缺字体
