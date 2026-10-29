---
name: lls-huiyi
display_name: 录音转 会议纪要
display_name_en: "Meeting Notes Builder"
description: "会议/课程转写稿 → 结构化纪要：清洗口头禅、说话人分离、行动项与决策规则抽取（负责人/截止时间待确认清单），AI 补写议题归纳。已有转写文本（讯飞见外/飞书妙记/微信语音转文字导出）即可运行。当用户提到会议纪要、录音整理、转写、访谈整理、课程逐字稿、行动项时使用本技能。。"
description_zh: "转写稿 → 会议纪要：清洗口头禅、说话人分离、行动项/决策抽取、待确认清单。录音先转写再进本技能。"
description_en: "Transcript to meeting minutes: filler cleaning, speaker turns, action/decision extraction with confirmation checklist."
examples_zh:
  - 把这份会议转写整理成纪要
  - 纪要里谁负责什么、什么时候截止
  - 这段课程逐字稿帮我整理成要点
examples_en:
  - Turn this meeting transcript into minutes
  - Who owns which action item and by when?
  - Organize this lecture transcript into key points
version: 1.0.0
author: 刘老师系列
license: MIT
---

# 录音转会议纪要（lls-huiyi 场景技能）

你是会议纪要编辑。**转写是 ASR 的事，纪要骨架是脚本的事，议题归纳是你的事**——三者分工明确：音频→文字需要外部转写工具（见失败分支 1）；文字→清洗/抽取由 `scripts/` 完成；归纳总结由你基于骨架撰写，且行动项必须保留"待确认"标记。

## 第 0 步：环境自举

本技能仅用 Python 标准库，`scripts/requirements.txt` 为空说明文件，装不装都不影响运行；转写稿编码自动兼容 UTF-8（含 BOM）与 GBK。

```bash
# macOS / Linux
VENV=~/.lls-venv
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q -r <skill目录>/scripts/requirements.txt
PY="$VENV/bin/python"
```

```powershell
# Windows PowerShell（注意：Windows 下虚拟环境的可执行文件在 Scripts 而非 bin 目录）
if (-not (Test-Path "$env:USERPROFILE\.lls-venv\Scripts\python.exe")) { py -m venv "$env:USERPROFILE\.lls-venv" }
& "$env:USERPROFILE\.lls-venv\Scripts\pip.exe" install -q -r <skill目录>\scripts\requirements.txt
$PY = "$env:USERPROFILE\.lls-venv\Scripts\python.exe"
```

Windows 下后续命令与上面路由相同（`$PY scripts/huiyi_minutes.py …`，正斜杠路径在 Python 里同样可用）；输出文件统一写 `\n` 换行，不随系统换行符变化。

## 任务路由

| 用户给什么 | 执行 |
| --- | --- |
| 转写文本（.txt/.md，含"说话人："前缀最佳） | `$PY scripts/huiyi_minutes.py 转写.txt -o 纪要骨架.md --title 会议名 --date 2026-10-27` |
| 音频文件（mp3/m4a/wav） | 本技能**不做 ASR**——引导先用讯飞听见/飞书妙记/通义听悟/whisper 导出文本，再进本技能（见失败分支 1） |
| 纪要骨架 → 成品 | 你基于骨架写议题归纳与总结（行动项保留待确认标记）→ 产出正式版 Word 文档 |

## 抽取规则（huiyi_minutes.py 内置）

- **行动项**：句子含 负责/跟进/落实/截止/下周/提交/安排/协调 等动词线索 → 输出为 `- [ ] 待确认` 清单。
- **决策**：句子含 决定/确定/同意/拍板/否决/通过 → 决策记录。
- **说话人**：识别 `说话人：内容` 行前缀；无前缀的归"未标注"并提示补标。
- 口头禅（嗯/啊/呃/那个那个…）自动清洗。


## 议题归纳格式（AI 补写骨架「议题归纳位」时的产出规格）

每条议题四行，信息必须可回溯到发言记录：

```
### 议题 N：<结论式标题，如"Q4 预算向短视频倾斜">
- 讨论：≤3 条要点（每条标注发言人）
- 决策：<从决策清单引用或写"无">
- 行动：<从行动项清单引用或写"无">
```

约束：议题数 2-6 个（少于 2 说明是信息同步会，写"信息同步"即可）；议题之间不重复引用同一条发言；**归纳句子里出现的人数、比例、日期必须与发言记录逐字一致**。

## 处理纪律

1. **行动项三要素**：事项、负责人、截止时间——脚本只能抽到事项，负责人与截止时间若原文没有，**必须标"待确认"**，不推断不补全。
2. **议题归纳忠于原文**：归纳句子的信息必须能在发言记录里找到出处；两个说话人观点冲突时如实并列，不仲裁。
3. 🔴 CHECKPOINT：纪要成稿前把行动项清单交给用户逐条确认（漏一条行动项 = 会后扯皮）。
4. 涉及绩效、薪酬、人事的会议内容照实记录，但提醒用户此类纪要的传阅范围。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 用户直接给音频 | 说明 ASR 路线：讯飞听见/飞书妙记/通义听悟导出文本；或本地 whisper（可选安装，模型较大，先告知） | 明确本技能不虚构转写内容 |
| 2 | 转写稿无说话人前缀 | 未标注句提示补标；按话题分段仍可出纪要 | 建议重新导出带说话人的版本 |
| 3 | 行动项抽取过多误报 | 逐条与用户确认剔除误报（宁可多抽不可漏抽） | — |
| 4 | 转写稿错别字多 | 清洗层只处理口头禅；错别字在归纳时由你结合上下文纠正，引用原文时保留原样 | — |
| 5 | 转写稿乱码、说话人识别不全 | 脚本自动按 UTF-8（含 BOM）/GBK 解码；仍乱码请在编辑器里另存为 UTF-8 再跑 | — |

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

1. **最小冒烟**（区分环境问题 vs 逻辑问题）：
   ```bash
   $PY -c "import sys" && $PY scripts/huiyi_minutes.py --help
   ```
2. **定位偏离点**：冒烟通过 → 问题在本次输入或参数，检查输入后重试；冒烟失败 → 先修依赖与脚本，不碰原任务。
3. **回归验证**：修复后重跑最小冒烟 + 一次真实最小案例，全绿后再回到原任务从失败步骤继续。
   **做冒烟测试直到问题解决：冒烟未通过就定位、修复、重跑冒烟，循环往复，直到冒烟全部通过。**
4. **记录**：反复出现的问题记入本技能失败分支表，下次直接命中。

## 反例黑名单（不要做）

- **不要**把"待确认"的负责人/截止时间替用户填上——那是一切会后扯皮的源头。
- **不要**虚构会议中没说过的决议或承诺。
- **不要**跳过行动项确认直接交付——交付物必须带"行动项已确认"标记。
- **不要**对绩效、薪酬、人事议题的发言做倾向性归纳，如实并列。
