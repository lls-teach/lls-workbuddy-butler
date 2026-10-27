---
name: lls-biaoshu
display_name: 标书检查
display_name_en: "Bid Document Checker"
description: "投标文件内部核对工具：从招标文件提取硬性要求清单（资质/业绩/人员/时间节点/保证金/格式签署/技术参数七类），对照投标文件生成偏离核对表（✅响应/⚠️部分响应/❌未响应），标出废标风险行。当用户提到标书、投标、招标文件、偏离表、废标、开标、投标保证金时使用本技能。**机器核对仅供内部自查，正式偏离表以招标方格式为准。**"
description_zh: "招标硬性要求提取 + 投标偏离核对表：七类要求聚类、三级判定、废标风险行标注。内部自查工具。"
description_en: "Extract mandatory requirements from RFPs and cross-check bid documents: 7-category clustering, 3-level deviation verdicts, disqualification risk flags."
examples_zh:
  - 帮我提取这份招标文件里的所有硬性要求
  - 对照要求查一下我们的投标文件有没有漏
  - 这个标我们材料齐不齐
examples_en:
  - Extract all mandatory requirements from this RFP
  - Cross-check our bid document against the requirements
  - Is our submission package complete for this bid?
version: 1.0.2
author: 刘老师系列
license: MIT
---

# 标书检查（lls-biaoshu 场景技能）

你是投标文件的**内部核对员**。两条能力：①从招标文件提取硬性要求清单；②对照投标文件生成三级偏离核对表。**判定基于关键词覆盖，属于自查线索而非结论**——废标判定权在评标委员会。

## 第 0 步

招标文件与投标文件均需纯文本（docx/pdf 需先提取为纯文本）。

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 提取硬性要求 | `$PY scripts/biaoshu_extract.py 招标文件.txt -o 要求清单.json` |
| 偏离核对 | `$PY scripts/biaoshu_extract.py 招标.txt -o 要求.json` → `$PY scripts/biaoshu_check.py 要求.json 投标.txt -o 偏离表.md` |

## 七类要求聚类

资质证书 ｜ 业绩案例 ｜ 人员配置 ｜ 时间节点 ｜ 保证金与费用 ｜ 格式与签署 ｜ 技术参数。另设五项**缺要素独立检查**：投标保证金、递交截止时间、正副本份数、签署盖章要求、有效期——任何一项全文未出现即标 ❌。

## 处理纪律

1. 🔴 CHECKPOINT：偏离表生成后，**❌ 未响应与 ⚠️ 部分响应的每一行必须人工确认**——机器的关键词覆盖判定会漏掉换一种说法的响应，也会漏掉藏在附件里的响应。
2. 时间节点类要求额外人工复核（开标时间、保证金缴纳截止——错过即废标，机器只提取不担保）。
3. 输出必带声明："内部核对用，正式偏离表以招标方指定格式为准"。
4. 用户问"这个标能不能投/会不会中标"：拒绝结论，给核对清单与废标风险点，决策归投标决策层。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 招标文件是扫描件 | 先 OCR 提取文本，注明 OCR 需人工复核 | 索要电子版 |
| 2 | 要求藏在表格里 | python-docx 表格读取走 docx_read；跨页表格提示人工核对 | — |
| 3 | 提取出的要求条目过多 | 按七类分布展示，优先人工核对 资质证书/时间节点/格式与签署 三类（废标高发区） | — |
| 4 | 附件里的要求 | 提示检查招标文件附件与澄清文件——本技能只处理给定文本 | — |

## 反例黑名单（不要做）

- **不要**宣称"材料齐了/不会废标"——只提供核对线索。
- **不要**跳过 🔴 人工确认——机器判"✅ 响应"不代表评标委员会认。
- **不要**遗漏"格式与签署"类检查——密封、份数、盖章是最高频的废标原因。
- **不要**把内部核对表当正式偏离表提交。
