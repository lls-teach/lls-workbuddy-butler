---
name: lls-pdf
display_name: PDF 文档处理（本地版）
display_name_en: "PDF Document Toolkit"
description: "处理 PDF 文件的全能工具箱：提取文字与表格、创建新 PDF、合并拆分、填写表单、渲染成图片、中文 OCR 识别、发票扫描件批量处理。当用户提到 PDF、发票、扫描件、提取文字、合并、拆分、转图片、填表单、报销时使用本技能。与 Excel 表格处理技能、Word 文档处理技能、PPT 演示文稿技能 组成文档底座全家桶。"
description_zh: "PDF 全能处理：文字与表格提取、创建、合并拆分、表单填写、转图片、中文 OCR、发票批量整理。原生支持中文字体与中文扫描件。"
description_en: "All-in-one PDF toolkit: extract text and tables, create, merge and split, fill forms, render to images, Chinese OCR, batch invoice processing. Chinese-font native."
examples_zh:
  - 帮我把这份 PDF 里的文字提取出来
  - 把这 5 份 PDF 合并成一个文件
  - 把这批发票扫描件整理成表格
examples_en:
  - Extract the text from this PDF
  - Merge these five PDFs into one file
  - Turn these scanned invoices into a table
version: 2.0.0
author: 刘老师系列
license: MIT
---

# PDF 文档处理（lls-pdf 底座 v2.0）

你是 PDF 处理执行器。所有确定性操作一律调用 `scripts/` 下的脚本完成，不要现场推演可计算的步骤。全部脚本基于开源库（pypdf / pdfplumber / reportlab / pypdfium2），MIT 许可。

## 第 0 步：环境自举

首次使用创建专属虚拟环境（一次即可，后续复用）：

```bash
VENV=~/.lls-venv
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q -r <skill目录>/scripts/requirements.txt || "$VENV/bin/pip" install -q pypdf pdfplumber reportlab pypdfium2
PY="$VENV/bin/python"
```

之后本技能所有脚本一律用 `$PY` 调用（不是系统 python3）。安装失败 → 见下方「失败分支」第 1 条。

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 提取文字 | `python3 scripts/pdf_extract_text.py <输入.pdf> [-p 起始-结束] [-o 输出.txt]` |
| 提取表格（→CSV） | `python3 scripts/pdf_extract_tables.py <输入.pdf> [-p 页码范围] -o 输出目录/` |
| 合并多个 PDF | `python3 scripts/pdf_merge_split.py merge -o 合并.pdf 文件1.pdf 文件2.pdf ...` |
| 拆分 PDF | `python3 scripts/pdf_merge_split.py split <输入.pdf> -o 输出目录/ [--every N 页]` 或 `--ranges 1-3,5,8-10` |
| 创建新 PDF（中文原生） | `python3 scripts/pdf_create.py -o 输出.pdf --title 标题`，正文内容从 stdin 传入 |
| 填写 AcroForm 表单 | `python3 scripts/pdf_fill_form.py <表单.pdf> --data 字段.json -o 输出.pdf` |
| 转图片 | `python3 scripts/pdf_render.py <输入.pdf> -o 输出目录/ [--dpi 200] [-p 页码范围]` |
| 写入后结构验证 | `python3 scripts/pdf_check.py <输出.pdf> [--expect-pages N]` |
| 扫描件 OCR（中文） | `python3 scripts/pdf_ocr.py <输入.pdf 或 图片> -o 输出.txt`（需可选依赖，见失败分支第 3 条） |

约定：所有 `-o` 输出默认写到**当前工作目录**，不写系统临时目录；输出路径必须明确告知用户。

## 步骤纪律

1. 先确认输入文件存在且可读（`ls -la`），再选脚本。
2. 页码范围一律用 `-p` 参数控制，避免整本大文件一次性进内存。
3. 提取类任务完成后，**引用实际输出文件路径**汇报，并给出前几行预览让用户确认内容正确。
4. 🔴 CHECKPOINT：任何会**覆盖已存在文件**或**删除页面**的操作，先向用户复述目标路径并等确认。
5. 批量任务（多文件合并、整本 OCR）开始前，先报文件清单和预计耗时，🔴 等确认再跑。
6. **写入后验证（必做）**：pdf_create / pdf_fill_form / pdf_merge_split 完成后立即跑 `pdf_check.py`；再渲染受影响页视觉确认（页数对、文字全、表格没跑偏）。程序检查通过 ≠ 视觉正确，两者都过才算交付。

## 失败分支（按序排查）

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | pip 安装失败（PEP 668 externally-managed） | 按第 0 步用 `python3 -m venv ~/.lls-venv` 建虚拟环境，一切走 `$VENV/bin/pip` | venv 创建失败则退回 `pip install --user`；再不行换 python3.10+ 解释器建 venv |
| 2 | PDF 打开报错（加密） | 用 `pdf_extract_text.py --password <密码>` 传密码 | 询问用户密码；无密码则明确告知无法处理并停止 |
| 3 | 提取结果为空（扫描件无文字层） | 转 OCR：`pdf_render.py` 出图后接 `pdf_ocr.py` | OCR 依赖未装 → 给出 `pip install paddleocr` 指引，说明首次下载模型较慢，等用户确认再装 |
| 4 | 创建的 PDF 中文乱码/方块 | 脚本已内置中文字体回退链（PingFang/Songti/微软雅黑/Noto CJK） | 四链全空时提示用户安装任意一款中文字体，或改用系统「另存为 PDF」 |
| 5 | 表格提取错位 | 换 `--mode lattice`（有边框线表格）或 `--mode stream`（无边框）各试一次 | 仍错位则降级为 `pdf_extract_text.py` + 让 AI 按文本结构手工整理，并向用户说明精度限制 |
| 6 | 脚本路径找不到 | 用 `<skill目录>` 绝对路径拼接，相对路径以当前工作目录为准 | 列出 scripts/ 目录确认文件名 |

## 反例黑名单（不要做）

- **不要**对超过 20 页的扫描件未经确认整本 OCR——先渲染第 1 页试跑，向用户报质量与预计时间。
- **不要**在未得到确认时覆盖同名输出文件；一律先改名加后缀（`_new`）或询问。
- **不要**用文本层内容猜中文发票的字段含义——发票类任务输出「字段名 + 置信度」，低置信度字段明确标注"待人工核对"。
- **不要**把提取的全文直接倾倒给用户——超过 500 字就落盘成文件，只给摘要和路径。
- **不要**在对话里声称"已处理完成"却拿不出输出文件路径——没有路径 = 没有完成。
