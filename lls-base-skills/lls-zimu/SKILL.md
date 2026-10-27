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

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

1. **最小冒烟**（区分环境问题 vs 逻辑问题）：
   ```bash
   $PY -c "import sys" && $PY scripts/zimu_parse.py --help
   ```
2. **定位偏离点**：冒烟通过 → 问题在本次输入或参数，检查输入后重试；冒烟失败 → 先修依赖与脚本，不碰原任务。
3. **回归验证**：修复后重跑最小冒烟 + 一次真实最小案例，全绿后再回到原任务从失败步骤继续。
4. **记录**：反复出现的问题记入本技能失败分支表，下次直接命中。
