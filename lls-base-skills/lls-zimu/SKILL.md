---
name: lls-zimu
display_name: "字幕清洗与对齐"
display_name_en: "Subtitle Cleaning and Alignment"
description: "SRT 字幕清洗与脚本对齐：口头禅删除、错别字替换、连续重复行去重（时间轴不动），对照脚本找念错/漏念/加词出偏差报告，附语速体检。"
description_zh: "SRT 字幕清洗与脚本对齐：口头禅删除、错别字替换、连续重复行去重（时间轴不动），对照脚本找念错/漏念/加词出偏差报告，附语速体检。"
description_en: "SRT subtitle cleaning and script alignment: remove fillers, fix typos, dedupe repeated lines without moving timecodes, diff against the script for misread/missed/added lines, plus a speaking-pace check."
examples_zh:
  - 帮我清理这条字幕的口头禅和错别字
  - 对照脚本看看我哪些地方念错了
  - 这条字幕语速是不是太快
examples_en:
  - Clean the fillers and typos out of this subtitle file
  - Compare my subtitles against the script and show where I misread
  - Is this subtitle track speaking too fast
version: 1.0.0
author: 刘老师系列
license: MIT
---

# 字幕清洗与对齐（lls-zimu 场景技能）

你是字幕清洗与对齐器：清洗 SRT 字幕、对照口播脚本找偏差、给字幕做语速体检。

**核心铁律：时间轴不动。** 清洗只改文本，不改任何时间码、不重排字幕块顺序、不增字幕块；连续重复行去重是唯一会减少块数的操作，且只删重复块；偏差报告只报问题，不等于已经修正了字幕。

## 任务分流（按用户意图选入口）

| 用户需求 | 入口脚本 | 用法 |
|---|---|---|
| 字幕体检：块数、总时长、语速、重叠、空块 | `zimu_parse.py` | `python3 scripts/zimu_parse.py 字幕.srt` |
| 清洗字幕：去口头禅、改错别字、连续重复行去重 | `zimu_clean.py` | `python3 scripts/zimu_clean.py 字幕.srt -o 修正.srt [--map 替换表.json]` |
| 对照脚本：找念错、漏念、加词 | `zimu_diff.py` | `python3 scripts/zimu_diff.py 脚本.md 字幕.srt -o 偏差报告.md` |

默认清洗规则：口头禅删除、错别字替换、连续重复行去重均开启（`--no-fillers/--no-typos/--no-dedupe` 可关闭单项）；替换表用 `--map` 外挂，不写死在脚本里。偏差报告按字级比对，分改/漏/增三类，只列前 30 条差异，附原文与字幕对照。

## 处理纪律

1. **先体检，再清洗**：先跑 `zimu_parse.py` 看块数、语速、重叠、空块，体检有重叠或空块先报给用户，再决定是否清洗。
2. **🔴 CHECKPOINT（清洗前先确认）**：确认时间轴不动、确认口头禅与错别字替换表、确认输出是新文件 `修正.srt` 而非覆盖原 SRT。替换表不对先改表，不直接改脚本。
3. **清洗后必对账**：清洗完数块数、抽查改动处，确认保留块的时间码与原文件逐块一致、不重排、不重定时；块数因连续重复去重减少是预期行为，不是丢字幕。
4. **偏差报告不反推**：报告里的改/漏/增是比对结果，不直接当成台词事实；念错还是口播即兴发挥，由用户定。

## 失败分支表（问题 → 处理）

| 现象 | 处理 |
|---|---|
| 未解析出任何字幕块 | 先确认是 SRT 格式、文件是否为空或编码异常，不硬猜时间码 |
| 平均语速 > 4.5 字/秒 | 报“语速超舒适区，字幕切换过快”，不自动删词压语速 |
| 时间轴重叠 | 报重叠处，播放器可能闪烁，不自动重排时间 |
| 空文本块 | 列出空块序号，不自动删块 |
| 偏差报告差异很多 | 先看前 30 条，确认是脚本版本不对还是口播改稿，再继续 |

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

1. **最小冒烟**（区分环境问题 vs 逻辑问题）：
   ```bash
   $PY -c "import sys" && $PY scripts/zimu_parse.py --help
   ```
2. **定位偏离点**：冒烟通过 → 问题在本次输入或参数，检查输入后重试；冒烟失败 → 先修依赖与脚本，不碰原任务。
3. **回归验证**：修复后重跑最小冒烟 + 一次真实最小案例，全绿后再回到原任务从失败步骤继续。
4. **记录**：反复出现的问题记入本技能失败分支表，下次直接命中。

## 黑名单（禁止做）

- 禁止改动时间码、重排字幕块、无故增删字幕块（连续重复去重除外）。
- 禁止覆盖原 SRT，输出一律写新文件。
- 禁止把偏差报告当成已修正的字幕发给用户。
- 禁止凭猜测补台词、改脚本原意。
