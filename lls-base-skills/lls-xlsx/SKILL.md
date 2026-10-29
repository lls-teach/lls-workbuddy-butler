---
name: lls-xlsx
display_name: Excel 表
display_name_en: "Excel Spreadsheet Toolkit"
description: "处理 Excel/xlsx 表格的全能工具箱：创建带公式与图表的工作簿、读取数据、批量修改单元格、CSV 与 Excel 互转、中文列宽自适应。当用户提到 Excel、表格、xlsx、报表、透视、求和公式、CSV 转换、报销单、成绩单时使用本技能。。"
description_zh: "Excel 全能处理：创建（公式/图表/中文列宽自适应）、读取、批量修改、CSV 互转。报销单、成绩单、数据汇总一站搞定。"
description_en: "All-in-one Excel toolkit: create workbooks with formulas and charts, read data, batch cell edits, CSV conversion, CJK-aware column widths."
examples_zh:
  - 帮我把这份 CSV 转成 Excel，加上表头样式
  - 读取这个表格，算一下每组的合计
  - 给这张报销单加一列金额小计和求和公式
examples_en:
  - Convert this CSV to Excel with header styling
  - Read this spreadsheet and total each group
  - Add a subtotal column and SUM formula to this sheet
version: 2.0.0
author: 刘老师系列
license: MIT
---

# Excel 表格处理（lls-xlsx 底座 v2.0）

你是 Excel 处理执行器。确定性操作一律调用 `scripts/` 脚本（openpyxl，MIT），不要手推可计算步骤。

## 第 0 步：环境自举

macOS/Linux（bash）：

```bash
VENV=~/.lls-venv
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q -r <skill目录>/scripts/requirements.txt
PY="$VENV/bin/python"
```

Windows（PowerShell；不要用上面 bash 的 `[ -x … ]` 与 `bin/python` 写法，Windows 虚拟环境在 `Scripts` 目录下）：

```powershell
python -m venv .lls-venv
.\.lls-venv\Scripts\pip install -q -r <skill目录>\scripts\requirements.txt
$PY = ".\.lls-venv\Scripts\python.exe"
```

此后命令中的 `$PY scripts/…` 在 Windows 下对应 `$PY scripts\…`，其余参数不变。

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 读取表格（→JSON/CSV 预览） | `$PY scripts/xlsx_read.py 输入.xlsx [--sheet Sheet1] [--json]` |
| 从 CSV/JSON 创建工作簿 | `$PY scripts/xlsx_create.py -o 新表.xlsx --from-csv 数据.csv [--title 标题]` |
| 创建带公式的报表 | `$PY scripts/xlsx_create.py -o 报表.xlsx --from-json 数据.json --sum-col 金额 [--chart bar]` |
| 批量改单元格 | `$PY scripts/xlsx_edit.py 输入.xlsx --set "Sheet1!B2=已审核" --set "Sheet1!C2=100"` |
| 追加行 | `$PY scripts/xlsx_edit.py 输入.xlsx --append-sheet Sheet1 --row-json '["张三","市场部",3000]'` |
| CSV→Excel / Excel→CSV | 用 xlsx_create.py --from-csv / xlsx_read.py --to-csv |
| 公式重算（写完公式必跑） | `$PY scripts/xlsx_recalc.py 输出.xlsx` |

## 步骤纪律

1. 改已有文件前先 `xlsx_read.py` 看结构（表头、行数、数据形状），🔴 CHECKPOINT：**覆盖已有文件前必须向用户复述并确认**（脚本默认改名 `_new`）。
2. 公式一律用 Excel 公式字符串（如 `=SUM(D2:D10)`）由脚本写入，不要预计算后填死数值——用户改数后公式要能联动。用批量改单元格脚本写公式时，`--set` 里第一个 `=` 是分隔符，公式本身的 `=` 要再写一个，即写两个 `=`，如 `--set "Sheet1!E2==C2+D2"`。
3. **公式重算（必做）**：openpyxl 写的公式没有缓存值，不重算的话所有读取器里公式格都是空的。凡写了公式，最后必须 `$PY scripts/xlsx_recalc.py 输出.xlsx`（需 LibreOffice）。**重算通过只证明公式算得通，不证明算得对**——范围差一行照样零报错，结果要抽查一行人工核对。
4. 大于 5,000 行的数据先报行数再处理。
5. 输出完成后引用实际文件路径 + 前 3 行预览。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 打开报错（.xls 旧格式） | 提示用户另存为 .xlsx；或 `pip install xlrd` 后告知仅支持读 | 明确说明格式限制 |
| 2 | 读取乱码 CSV | `--encoding gbk` 重试（国内 Excel 导出常为 GBK） | 让用户用文本编辑器确认编码 |
| 3 | 单元格是图片/合并单元格读不出 | 合并单元格自动取左上值并标注；图片需先做 OCR 识别 | 告知限制 |
| 4 | 公式写入后打开是 0 | openpyxl 不计算公式：跑 `xlsx_recalc.py`（需 LibreOffice）回写缓存值；无 LibreOffice 则告知用户在 Excel/WPS 中打开即自动重算 | — |

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

1. **最小冒烟**（区分环境问题 vs 逻辑问题）：
   ```bash
   $PY -c "import openpyxl" && $PY scripts/xlsx_create.py --help
   ```
2. **定位偏离点**：冒烟通过 → 问题在本次输入或参数，检查输入后重试；冒烟失败 → 先修依赖与脚本，不碰原任务。
3. **回归验证**：修复后重跑最小冒烟 + 一次真实最小案例，全绿后再回到原任务从失败步骤继续。
**做冒烟测试直到问题解决**：冒烟未通过就定位、修复、重跑冒烟，循环往复，直到冒烟全部通过才算完成；未全绿不得回到原任务。
4. **记录**：反复出现的问题记入本技能失败分支表，下次直接命中。

## 反例黑名单（不要做）

- **不要**在未读取原表结构前直接写入——列位对错是最常见事故。
- **不要**把用户数据落盘到系统临时目录之外的新路径却不告知。
- **不要**用 AI 现场心算合计——一律写 Excel 公式。
- **不要**对含宏（.xlsm）的文件改后缀；保持原扩展名。
