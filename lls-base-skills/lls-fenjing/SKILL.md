---
name: lls-fenjing
display_name: "视频分镜脚本"
display_name_en: "Storyboard Script Builder"
description: "口播稿/要点 → 拍摄级分镜脚本表：镜头号、起点与时长（按 4 字/秒语速校准台词）、景别建议（近景建信任/特写强调数据/中景放缓节奏）、画面描述位，输出 Markdown 表格 + Excel 拍摄版，附分镜 lint（语速/景别词表/总时长上限）。当用户提到分镜、拍摄脚本、镜头、景别、短视频拍摄、口播拍摄时使用本技能。与 lls-koushuo（口播稿）组成短视频前后道工序。"
description_zh: "口播稿 → 分镜脚本表：镜头号/景别建议/画面位/台词/时长（4 字/秒校准），Markdown+Excel 双输出，附语速 lint。"
description_en: "Talking-head script to storyboard table: shot numbers, framing suggestions, durations calibrated at 4 chars/second, Markdown + Excel output with lint."
examples_zh:
  - 把这篇口播稿转成分镜脚本
  - 出一份 Excel 分镜表给拍摄团队
  - 检查分镜表语速会不会念不完
examples_en:
  - Convert this script into a storyboard table
  - Export an Excel storyboard for the shoot crew
  - Check whether the storyboard pacing is speakable
version: 1.0.0
author: 刘老师系列
license: MIT
---

# 视频分镜脚本（lls-fenjing 场景技能）

你是分镜脚本执行器。切分、时长、表格全部交给 `scripts/`（4 字/秒校准），景别与画面的艺术判断可以建议但标注"建议值"。上游来自 lls-koushuo 的口播稿，下游交付拍摄团队。

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 口播稿 → 分镜表 | `$PY scripts/fenjing_make.py 口播稿.md -o 分镜表.md [--xlsx 分镜表.xlsx]` |
| 分镜表 lint | `$PY scripts/fenjing_check.py 分镜表.md --limit 60` |

## 景别建议规则（脚本内置）

- 开场镜头 = **近景**（人物出镜建立信任）
- 含数字/数据的台词 = **特写**（字幕贴图强调）
- 正文论述 = **中景** + B-roll 空镜
- 收尾 CTA = **近景**（回归人物）

## 处理纪律

1. **时长是算出来的不是估的**：台词字数 ÷ 4 = 秒数；lint 会抓">5.5 字/秒"的念不完镜头。
2. 🔴 CHECKPOINT：分镜表确认前，把"镜头数 + 总时长 + 语速最快镜头"三项报给用户——超时是最常见的返工原因。
3. 拍摄团队用 Excel 版（--xlsx），画面列留空位让他们填实际素材。
4. 景别只是建议——标注"建议值，按实际素材调整"。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 单镜头台词 200 字 | 自动按段落切分后仍超长 → 拆成 2-3 个镜头（近景/特写交替） | 提示用户口播稿本身该拆段 |
| 2 | 用户给了视频总时长上限 | --limit 传入，超时列出让用户砍镜头 | 按比例压缩每镜头时长并重新校准语速 |
| 3 | 无口播、纯画面视频 | 分镜表台词列留空，画面列写实拍描述——本技能仍可用 | — |

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

1. **最小冒烟**（区分环境问题 vs 逻辑问题）：
   ```bash
   $PY -c "import sys" && $PY scripts/fenjing_check.py --help
   ```
2. **定位偏离点**：冒烟通过 → 问题在本次输入或参数，检查输入后重试；冒烟失败 → 先修依赖与脚本，不碰原任务。
3. **回归验证**：修复后重跑最小冒烟 + 一次真实最小案例，全绿后再回到原任务从失败步骤继续。
4. **记录**：反复出现的问题记入本技能失败分支表，下次直接命中。

## 反例黑名单（不要做）

- **不要**估时长——必须按字数计算。
- **不要**把景别写成"随便"——给建议值并标注可调。
- **不要**跳过 fenjing_check 交付——念不完的分镜等于白拍。
