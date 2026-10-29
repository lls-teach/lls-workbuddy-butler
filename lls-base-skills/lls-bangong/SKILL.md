---
name: lls-bangong
display_name: 打工人四件套
display_name_en: "Office Suite for Workers"
description: "办公四件套：Word、Excel、PPT、PDF 一个下载全搞定，格式转换与批量处理一站式。处理 Word 文档创建/读取/批量替换、Excel 表格创建/读取/公式重算、PPT 演示文稿三套设计系统一键成片、PDF 文字表格提取/合并拆分/表单填写/中文 OCR，78 种格式互转（PDF 与 Markdown 双中枢），同一操作可对文件夹内全部文件批量执行。当用户提到办公、文档、表格、幻灯片、Word、Excel、PPT、PDF、格式转换、批量处理、打工人、四件套、公文、报告、报表、汇报、课件、发票、报销时使用本技能。"
description_zh: "办公四件套：Word、Excel、PPT、PDF 一个下载全搞定。文档创建读取批量替换、表格公式图表、PPT 三套设计系统成片、PDF 提取合并拆分 OCR，78 种格式互转，文件夹级批量处理。中文字体原生。"
description_en: "Office suite in one download: Word docs, Excel sheets, PPT decks, and PDF files, plus 78-format conversion and folder-level batch processing. Chinese-font native."
examples_zh:
  - 写一份 Word 版的通知，要有标题和落款
  - 把这份 CSV 转成 Excel，加上表头样式和求和公式
  - 按这份大纲做一个 8 页的 PPT，用正式汇报风格
examples_en:
  - Write a Word notice with title and signature block
  - Convert this CSV to Excel with styled headers and a SUM formula
  - Build an 8-slide deck from this outline in formal report style
version: 1.0.1
author: lhg
---

# 打工人四件套（lls-bangong 底座 v1.0.0）

Word、Excel、PPT、PDF 四组能力 + 格式转换中枢，一个下载全搞定。**不改动原文件**：凡是编辑/转换类操作一律用 `-o` 输出新文件，原文件只读。

## 第 0 步：环境自举

```bash
VENV=~/.lls-venv
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q -r <skill目录>/scripts/requirements.txt
PY="$VENV/bin/python"
```

Windows（PowerShell，命令与上面等价，不要用 bash 写法）：

```powershell
py -m venv $env:USERPROFILE\.lls-venv
$env:USERPROFILE\.lls-venv\Scripts\pip.exe install -q -r <skill目录>\scripts\requirements.txt
$PY = "$env:USERPROFILE\.lls-venv\Scripts\python.exe"
```

Windows 上 LibreOffice 若未加入 PATH，转换类脚本会按默认安装路径
`C:\Program Files\LibreOffice\program\soffice.exe` 查找；未安装则如实报缺，不假装能转。

转换类操作另需系统工具：LibreOffice（soffice）、ffmpeg/ffprobe。先跑一次环境自检，缺哪样先补装再转，补不上就如实报缺哪样，不假装能转：

```bash
$PY scripts/check_env.py
```

## 任务路由

按用户给的文件类型 / 任务分流。先看扩展名定组，再看动作定脚本：

| 用户要什么 | 执行 |
|---|---|
| Word 创建（公文/报告/通知，标题层级、表格、页眉） | `$PY scripts/docx_create.py -o 输出.docx --title 标题 --header 页眉`，正文走 `--stdin-file` 或 stdin |
| Word 读取全文结构 | `$PY scripts/docx_read.py 输入.docx [--json]` |
| Word 批量替换 / 文末追加段落 | `$PY scripts/docx_edit.py 输入.docx --replace 旧=新（可多次） [--append 段落] -o 输出.docx` |
| Word 修订记录 | `$PY scripts/docx_revisions.py 输入.docx` |
| Excel 创建（公式/图表/中文列宽自适应） | `$PY scripts/xlsx_create.py -o 输出.xlsx [--from-csv 输入.csv] [--from-json 数据] [--sum-col 列名]` |
| Excel 读取 / 转 CSV / 转 JSON | `$PY scripts/xlsx_read.py 输入.xlsx [--sheet 表名] [--to-csv 输出.csv] [--json 输出.json]` |
| Excel 批量改单元格 / 追加行 | `$PY scripts/xlsx_edit.py 输入.xlsx --set 表!单元格=值（可多次） [--append-sheet 表名 --row-json 行] -o 输出.xlsx` |
| Excel 公式重算 | `$PY scripts/xlsx_recalc.py 输入.xlsx` |
| PPT 生成（三套设计系统：正式汇报/咨询研报/教学课件） | `$PY scripts/pptx_create.py -o 输出.pptx --title 标题 --outline 大纲文件 [--style formal]`（`--outline` 传大纲文件路径，每页以 `# 标题` 开头；也可直接传多行大纲文本），设计系统见 `references/design-system.md` |
| PPT 读取每页内容 | `$PY scripts/pptx_read.py 输入.pptx [--json]` |
| PPT 批量替换 / 改标题 | `$PY scripts/pptx_edit.py 输入.pptx --replace 旧=新（可多次） [--slide 页码 --set-title 标题]` |
| PPT 加图表 / 复制页 / 质量检查 / 缩略图 | `$PY scripts/pptx_add_chart.py` / `pptx_duplicate_slide.py` / `pptx_check.py` / `pptx_thumbs.py` |
| PDF 创建（中文 PDF） | `$PY scripts/pdf_create.py -o 输出.pdf --title 标题 --stdin-file 正文` |
| PDF 提取文字 / 表格 | `$PY scripts/pdf_extract_text.py 输入.pdf [-p 页码范围] [-o 输出.txt]` / `pdf_extract_tables.py 输入.pdf -o 输出目录` |
| PDF 合并拆分 | `$PY scripts/pdf_merge_split.py merge 输入1.pdf 输入2.pdf -o 输出.pdf`（拆分见脚本子命令） |
| PDF 填表单 / 列字段 | `$PY scripts/pdf_fill_form.py 输入.pdf [--list] [--data 字段.json -o 输出.pdf]` |
| PDF 扫描件 OCR（中英混合） | `$PY scripts/pdf_ocr.py 输入.pdf -o 输出.txt [--lang ch]` |
| PDF 渲染成图片 / 页数校验 | `$PY scripts/pdf_render.py 输入.pdf -o 输出目录 [--dpi 200]` / `pdf_check.py 输入.pdf [--expect-pages N]` |
| 格式转换（78 种，PDF 与 Markdown 双中枢） | `$PY scripts/convert.py 输入 目标扩展名 [-o 输出目录]`；同名目标会自动改名为 `名字-1.ext`，要覆盖加 `--force`。支持矩阵见 `references/supported-matrix.md` |
| 批量模式（同一操作对文件夹内全部文件） | shell 循环：`for f in 文件夹/*.docx; do $PY scripts/convert.py "$f" pdf -o 输出目录; done`（默认不覆盖，重名自动加序号） |

## 步骤纪律

1. **先定组再动手**：扩展名定组（.docx→Word 组、.xlsx→表格组、.pptx→演示组、.pdf→PDF 组），跨格式走转换中枢，不跨组硬套脚本。
2. **转换矩阵**（高频链路；完整矩阵见 `references/supported-matrix.md`）：
   - Word↔PDF：`docx_convert.py --to pdf` 或 `convert.py 输入 pdf`；PDF→Word 走转换中枢（文字层提取 + 重排版）。
   - Word→PPT：先 `docx_read.py` 读出标题层级大纲，再 `pptx_create.py --outline 大纲` 成片。
   - PPT→Word：先 `pptx_read.py` 读每页内容，再 `docx_create.py` 写成讲稿文档。
   - Excel↔CSV：`xlsx_create.py --from-csv` / `xlsx_read.py --to-csv`。
   - PDF→Excel：先 `pdf_extract_tables.py` 提表格，再 `xlsx_create.py --from-csv` 落表。
   - 批量转格式：同一转换对文件夹内全部文件循环执行，逐个报告成功/失败，不因单个失败中断整批。
3. **中文字体原生**：创建类操作默认中文字体（宋体/黑体/楷体），渲染与 OCR 默认中英混合，出现方块字先查字体再查内容。
4. **输出纪律**：编辑/转换一律 `-o` 写新文件；目标已存在时先确认或改名，不静默覆盖（批量模式先报同名清单再确认）。
5. **校验闭环**：合并后必跑 `pdf_check.py --expect-pages` 核页数；PPT 生成后必跑 `pptx_check.py` 核单页密度；Excel 写公式后必跑 `xlsx_recalc.py`。

## 失败分支（按序排查）

1. 脚本报缺少依赖 → 回第 0 步重装 requirements，转换类另查 soffice/ffmpeg 是否在 PATH。
2. 中文显示方块 → 查中文字体是否安装，创建类操作确认字体参数。
3. 转换失败 → 先跑 `check_env.py` 看缺哪样；缺系统工具如实报，缺 Python 包按提示补装；不承诺未测过的转换对。
4. 批量中途单个失败 → 记录失败文件继续跑完整批，最后汇总失败清单，不丢已成功的结果。
5. 目标文件已存在 → 先确认或改名，不静默覆盖。

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

- 最小冒烟：Word 创建一页通知 → Excel 读一张表 → PPT 生成 2 页 → PDF 合并 2 份 → 转换 1 个文件，四组 + 中枢各跑通一条最小链路。
- 定位：冒烟通过 → 问题在本次输入或参数，检查输入后重试；冒烟失败 → 先修依赖与脚本，不碰原任务。
- 回归解决：修脚本后用 test-prompts.json 6 条全跑一遍，产出路径与校验结果须与 expected 一致。
- 做冒烟测试直到问题解决：冒烟未通过就定位、修复、重跑冒烟，循环往复，直到冒烟全部通过。

## 反例黑名单（不要做）

- 不要改动原文件：编辑/转换必须 `-o` 输出新文件。
- 不要静默覆盖：目标已存在必须先确认或改名，批量模式先报同名清单。
- 不要承诺未测过的转换对：支持矩阵以外的转换先查 `references/supported-matrix.md`，没有就明说不支持。
- 不要把扫描件当文字层：无文字层的 PDF 先走 OCR 路线，不直接提取出空文本交差。
- 不要跳过校验闭环：合并、成片、写公式后必须跑对应的检查脚本。
- 不要用其他 skill 的名字指代能力：路由只写能力名词（Word 文档处理、Excel 表格处理、PPT 演示、PDF 文档处理、格式转换）。
