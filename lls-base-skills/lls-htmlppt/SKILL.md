---
name: lls-htmlppt
display_name: "HTML交互演示"
display_name_en: "HTML Interactive Deck"
description: "大纲 → 自包含单文件 HTML 交互演示：键盘/触摸翻页、进度条、全屏（F 键）、零外部依赖离线可用、发链接即看无需 Office。与 .pptx 互补——一份内容两种载体。当用户提到 HTML 演示、网页 PPT、H5 演示、发链接的演示、网页版幻灯、免安装放映时使用本技能。md 大纲语法与底座 lls-pptx 完全兼容，一源两载体。"
description_zh: "大纲 → 单文件 HTML 交互演示：键盘/触摸翻页、进度条、全屏、离线可用、发链接即看。与 .pptx 一源两载体。"
description_en: "Outline to a self-contained single-file HTML deck: keyboard/touch navigation, progress bar, fullscreen, offline-ready. One source, two formats."
examples_zh:
  - 把这份大纲做成发链接就能看的演示
  - md 笔记既要 pptx 又要网页版
  - HTML 演示能在没网的电脑上放吗
examples_en:
  - Turn this outline into a shareable-link deck
  - I need both .pptx and a web version of my notes
  - Will the HTML deck work offline?
version: 1.0.0
author: 刘老师系列
license: MIT
---

# HTML交互演示（lls-htmlppt 场景技能）

你是 HTML 演示构建器。**转换全部交给脚本（单文件、零依赖、离线可用），翻页体验即开即用**。与底座 lls-pptx 一源两载体：`.pptx` 交给要编辑的人，HTML 交给要观看的人。

## 任务路由

| 用户给什么 | 执行 |
| --- | --- |
| 大纲 md（与 lls-pptx 同语法：#/##/-/>） | `$PY scripts/htmlppt_build.py --outline 大纲.md -o 演示.html` |
| md 笔记（非大纲语法） | 先走底座 lls-mdppt 转换 → 再进本技能 |
| 两种载体都要 | 大纲 → lls-pptx 出 .pptx + 本技能出 HTML（一份内容，两种交付） |

## 内置特性（脚本已实现，无需配置）

- 键盘：←→/空格/PgUp/PgDn 翻页，F 全屏
- 触摸：左右滑动翻页（移动端可用）
- 进度条（顶部强调色）+ 页码
- 单文件自包含：无 CDN、无外部字体，**离线可用、可邮件附件发送**
- 中文原生（PingFang/雅黑回退链）

## 处理纪律

1. 🔴 CHECKPOINT：生成前确认大纲结构（页数 + 每页要点）——HTML 翻页改结构比 .pptx 麻烦。
2. 交付时告知用户三个事实：离线可用、发链接即可看、内容如需编辑走 .pptx 载体。
3. 渲染验收：浏览器打开后按 → 翻页确认每页显示正常（可用 ego-browser 实测）。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 大纲为空/无页 | 检查 md 是否有 ## 或 - 行 | 让用户先给层级化内容 |
| 2 | 中文方块 | 已内置 PingFang/雅黑回退链 | 用户系统无中文字体时提示 |
| 3 | 用户要打印成 PDF | 浏览器 Ctrl+P 逐页打印（每页一屏） | — |

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

1. **最小冒烟**（区分环境问题 vs 逻辑问题）：
   ```bash
   $PY -c "import sys" && $PY scripts/htmlppt_build.py --help
   ```
2. **定位偏离点**：冒烟通过 → 问题在本次输入或参数，检查输入后重试；冒烟失败 → 先修依赖与脚本，不碰原任务。
3. **回归验证**：修复后重跑最小冒烟 + 一次真实最小案例，全绿后再回到原任务从失败步骤继续。
4. **记录**：反复出现的问题记入本技能失败分支表，下次直接命中。

## 反例黑名单（不要做）

- **不要**引入 CDN 或外部字体——离线可用是本技能的承诺。
- **不要**加自动播放动画——演示的节奏权在演讲者手里。
- **不要**在 HTML 里塞超过 6 个要点——拆页规则与 lls-pptx 一致。
- **不要**两种载体内容不同步——同一份大纲同时出 .pptx 和 HTML，或者只出一种并说明原因。
