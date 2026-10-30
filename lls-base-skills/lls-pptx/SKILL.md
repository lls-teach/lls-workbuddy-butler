---
name: lls-pptx
display_name: PPT演示文稿
display_name_en: "PPT Slides Toolkit"
description: "处理 PowerPoint/.pptx 的全能工具箱：三套设计系统一键成片（正式汇报/咨询研报/教学课件）、读取每页内容、批量替换、模板页复制、程序化质量检查、缩略图总览、中文字体原生。当用户提到 PPT、幻灯片、演示文稿、汇报、课件、路演、美化、pptx 时使用本技能。。"
description_zh: "PPT 全能处理：三套设计系统一键成片、读取、批量改字、模板加页、质量检查、缩略图总览。汇报、课件、路演快速出片，中文字体原生。"
description_en: "All-in-one PPT toolkit: three design systems for deck generation, per-slide reading, batch replace, template slide duplication, programmatic QA, thumbnail overview, Chinese-native fonts."
examples_zh:
  - 用正式汇报风格，按这份大纲做一个 8 页的 PPT
  - 把这份 PPT 每一页的内容列给我，再检查有没有超密度
  - 把 PPT 里所有的"2025 年"都改成"2026 年"
examples_en:
  - Build an 8-slide deck in the formal report style from this outline
  - List every slide's content and check for over-dense pages
  - Replace all "2025" with "2026" in this deck
version: 2.2.1
author: 刘老师系列
license: MIT
---

# PPT 演示文稿（lls-pptx 底座 v2.0）

你是 PPT 处理执行器 + 视觉执行者。确定性操作调用 `scripts/`（python-pptx 等 MIT 库），中文字体原生。视觉决策依据 `@references/design-system.md`。

## 第 0 步：环境自举

```bash
VENV=~/.lls-venv
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q -r <skill目录>/scripts/requirements.txt
PY="$VENV/bin/python"
```

Windows（PowerShell，虚拟环境在 `Scripts` 而非 `bin` 下）：

```powershell
$VENV = "$HOME\.lls-venv"
if (-not (Test-Path "$VENV\Scripts\python.exe")) { py -3 -m venv $VENV }
& "$VENV\Scripts\pip.exe" install -q -r <skill目录>\scripts\requirements.txt
$PY = "$VENV\Scripts\python.exe"
```

## 第 1 步：风格简报（生成类任务必做，缺一不可）

生成 PPT 前先定三件事（读 @references/design-system.md 第一节）：

1. **受众与目的**：给谁看、要促成什么判断。
2. **密度**：低（发布会）／中（路演培训）／高（决策会研报）。
3. **风格**：`formal`（正式汇报）／`consulting`（咨询研报）／`teaching`（教学课件）。

用户没说就按用途推断并告知推断结果；一句风格简报（三个形容词 + 一个有益张力）写进回复开头。**每个内容页选择与内容匹配的版式词汇（见下），不要整份都用要点列表。**

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 大纲 → 成套 PPT | `$PY scripts/pptx_create.py -o 成片.pptx --title 标题 --subtitle 副标题 --outline 大纲.md --style formal` |
| 读取全部内容 | `$PY scripts/pptx_read.py 输入.pptx [--json out.json]` |
| 批量替换文字 | `$PY scripts/pptx_edit.py 输入.pptx --replace "2025=2026" -o 新.pptx` |
| 改某页标题 | `$PY scripts/pptx_edit.py 输入.pptx --slide 2 --set-title "新标题" -o 新.pptx` |
| 模板页复制 | `$PY scripts/pptx_duplicate_slide.py 模板.pptx --slide 2 --times 3 -o 成片.pptx` |
| 程序化质量检查 | `$PY scripts/pptx_check.py 输入.pptx`（秒级，零渲染） |
| 添加原生图表 | `$PY scripts/pptx_add_chart.py 输入.pptx --slide N --type bar --title 标题 --categories "a,b,c" --series "系列=1,2,3" -o 新.pptx`（图表为原生对象可在 Office 中编辑；目标页应为空证据场页，避免与要点重叠） |
| 缩略图总览 | `$PY scripts/pptx_thumbs.py 输入.pptx 前缀`（需 LibreOffice，见失败分支 5） |

**大纲语法**（按内容选版式形状）：

| 语法 | 渲染为 | 适用内容 |
| --- | --- | --- |
| `# 标题` | 论点带（**写结论句，不写话题**） | 每页 |
| `- 要点` | 要点行（≥5 自动两列） | 方向、清单 |
| `[KPI] 31,940\|技能总量\|仍在增长` | KPI 大数字行（一页 ≤4） | 规模、份额、占比 |
| `[STATUS] 名称\|空位\|时间\|状态\|色` | 语义状态表（斑马纹+状态圆点；色=amber/blue/good/muted，缺省按状态词推断） | 路线图、多事项进展 |
| `[BAR] 58\|实名认证` | 进度条行 | 漏斗、完成度 |
| `[TABLE] 列1\|列2\|列3` | 斑马纹表格（首行表头） | 决策项、对比、清单 |
| `> 结论` | 结论带（蓝色强调） | 有明确结论的页 |
| `= 来源：市场普查` | 来源行 | 引用数据的页 |

## 生成纪律

1. **每页一个主要结论**：页标题写结论不写话题（"华东区增速领跑"，不是"华东区分析"）。
2. **要点 ≤6 条**：超出主动拆页或转两列证据网格；每条 ≤2 行。
3. **垂直节奏**：页眉带 → 论点带（一行标题）→ 分隔带 → 证据场 → 结论带（可选）→ 来源行 → 页脚；脚本已内置。
4. **版式多样**：相邻页用不同版式词汇（KPI 页 → 状态表页 → 要点页 → 图表页），整份都是要点列表 = 未完成设计。
4. 🔴 CHECKPOINT：把解析后的大纲结构（页数 + 每页要点）展示给用户，确认后再生成。
5. 生成后立即跑 `pptx_check.py`，随回复汇报警告数与处理建议。

## 编辑纪律

1. 🔴 CHECKPOINT：编辑已有 PPT 前必须先 `pptx_read.py` 展示将受影响的页，确认后再改（默认输出 `_new`，原文件不动）。
2. 批量替换报告替换次数与按页分布；0 次命中要明说。
3. 模板加页（duplicate_slide）后必须跑 `pptx_check.py` 验证包完整性。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 打开报错（.ppt 旧格式） | 请用户用 PowerPoint/WPS 另存为 .pptx | 明确说明限制 |
| 2 | 中文方块/默认宋体 | 脚本已设"微软雅黑"字体名 | 用户机器缺中文字体时提示安装 |
| 3 | 替换 0 命中 | 核对替换词；SmartArt/图表内文字超出能力 | 列出未命中的页码请用户手改 |
| 4 | duplicate 后打不开 | 用 pptx_check.py 定位；重跑一次并检查源文件是否加密 | 回退方案：用 pptx_create.py 重建该页 |
| 5 | 缩略图报找不到 soffice | 按 pptx_thumbs.py 提示安装 LibreOffice | 用 pptx_check.py 替代做内容级检查 |
| 6 | 密度警告刷屏 | 按 design-system.md 拆页或转证据网格，不要调大 --max-chars 掩盖问题 | — |

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

**做冒烟测试直到问题解决：冒烟未全部通过就定位、修复、重跑冒烟，循环往复，直到冒烟全部通过才算完成、才能回到原任务。**

1. **最小冒烟**（区分环境问题 vs 逻辑问题）：
   ```bash
   $PY -c "import pptx" && $PY scripts/pptx_check.py --help
   ```
2. **定位偏离点**：冒烟通过 → 问题在本次输入或参数，检查输入后重试；冒烟失败 → 先修依赖与脚本，不碰原任务。
3. **回归验证**：修复后重跑最小冒烟 + 一次真实最小案例，全绿后再回到原任务从失败步骤继续。
4. **记录**：反复出现的问题记入本技能失败分支表，下次直接命中。

## 反例黑名单（不要做）

- **不要**未经确认覆盖原 PPT——演示文件常有不可再生内容。
- **不要**把超过 6 行要点塞进一页、把字号缩到 14pt 以下硬塞——拆页。
- **不要**假装能改 SmartArt/嵌入图表/母版设计——明确说能力边界。
- **不要**跳过 pptx_check.py 就宣布完成——没有检查 = 没有交付。
- **不要**用纯装饰性的圆角卡片和图标堆砌页面——密度靠分组与对齐，不靠装饰。
