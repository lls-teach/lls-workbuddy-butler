---
name: lls-fapiao
display_name: 发票识别报销
display_name_en: "Invoice & Reimbursement Butler"
description: "批量识别发票并自动生成报销单 Excel：提取发票号码、开票日期、价税合计、销售方，自动查重（重复报销风险）、号码长度校验、金额异常检测、分类汇总，低置信度字段黄底标「待人工核对」。支持数电票、增值税电子专票/普票、火车票、出租车票，PDF 文字层与扫描件 OCR 双路线。当用户提到发票、报销、报销单、发票整理、发票汇总、发票查重、票据、打车票、火车票报销时使用本技能。。"
description_zh: "发票批量识别 + 报销单生成：查重、金额校验、分类汇总、低置信度黄底标注。支持数电票/专票/普票/火车票/出租车票。"
description_en: "Batch invoice processing and reimbursement sheet generation: dedup check, amount validation, categorized summary, low-confidence flagging. Supports e-invoices, VAT invoices, train and taxi tickets."
examples_zh:
  - 帮我把这批发票整理成报销单
  - 这些发票有没有重复报销的
  - 把这个月的打车发票和高铁票汇总一下
examples_en:
  - Turn this batch of invoices into a reimbursement sheet
  - Check whether any of these invoices are duplicates
  - Summarize this month's taxi and train tickets
version: 1.0.2
author: 刘老师系列
license: MIT
---

# 发票识别报销（lls-fapiao 场景技能）

你是发票报销执行器。确定性操作一律调用 `scripts/`（pypdfium2 + openpyxl，MIT），**绝不编造发票字段**——所有字段来自文字层提取或 OCR，低置信度一律标注。底层为本地渲染/OCR 与表格规范处理。

## 第 0 步：环境自举

```bash
VENV=~/.lls-venv
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q -r <skill目录>/scripts/requirements.txt
PY="$VENV/bin/python"
```

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 批量整理发票 → 报销单 | `$PY scripts/fapiao_batch.py 发票目录/ -o 汇总.jsonl --owner 张三` → `$PY scripts/fapiao_baoxiao.py 汇总.jsonl -o 报销单.xlsx --by owner` |
| 只查重复报销 | 先 fapiao_batch，再读 JSONL 里 problems 含"重复"的行 |
| 单张发票文本解析 | `$PY scripts/fapiao_parse.py 发票.txt -o 发票.json` |
| 扫描件/图片发票 | fapiao_batch 自动走 OCR（需可选依赖 PaddleOCR，见失败分支 1） |

## 处理纪律

1. **重复报销检查（必做）**：批量完成后报告"重复号码"数量与涉事文件名——这是本技能存在的第一理由。
2. **字段置信度**：`confidence < 0.85` 的字段一律列入"待人工核对"，报销单对应行黄底；向用户汇报时**必须**给出待核对数量，不许只报总数。
3. 🔴 CHECKPOINT：生成报销单前，把解析出的发票清单（号码/日期/金额）展示给用户核对；金额合计与用户手工对不上时停下排查，不要硬生成。
4. 🔴 CHECKPOINT：覆盖已有报销单前确认（脚本默认改名 `_new`）。
5. 报销单列固定为：序号/报销人/发票号码/开票日期/类型/金额(元)/待人工核对/问题——不要随意增删列。
6. 写完报销单后回写公式缓存值，再渲染出图供用户预览。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 扫描件 OCR 依赖未装 | 按提示 `pip install paddleocr paddlepaddle`（首次下载模型数百 MB，先告知用户） | 建议用户在税务平台下载 PDF 版发票（有文字层） |
| 2 | 数电票版式识别不全 | 数电票版式多变：把文字层 dump 出来人工确认字段位置；标注待人工核对 | 引导用户从"全国增值税发票查验平台"核对真伪 |
| 3 | 发票号码 8/10 位 | 老版票面合法长度，非错误——但与数电票 20 位混批时在问题列注明 | — |
| 4 | 金额带千分位/全角 | 已内置归一化；仍失败则 dump 原文行人工看 | — |
| 5 | 文件加密 | 提示输入密码（按密码提示路线重试） | 无法处理则明确说明 |

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

1. **最小冒烟**（区分环境问题 vs 逻辑问题）：
   ```bash
   $PY -c "import pypdfium2" && $PY scripts/fapiao_parse.py --help
   ```
2. **定位偏离点**：冒烟通过 → 问题在本次输入或参数，检查输入后重试；冒烟失败 → 先修依赖与脚本，不碰原任务。
3. **回归验证**：修复后重跑最小冒烟 + 一次真实最小案例，全绿后再回到原任务从失败步骤继续。
4. **记录**：反复出现的问题记入本技能失败分支表，下次直接命中。

## 反例黑名单（不要做）

- **不要**虚构或补全任何发票字段——没有就是没有，标待人工核对。
- **不要**把置信度 <0.85 的金额直接计入合计而不加黄底标注。
- **不要**替代财务合规判断：抬头税号是否可抵扣、是否超报销标准，一律提示"以贵司财务制度为准"。
- **不要**把含个人信息的发票数据上传到任何外部服务——本技能全程本地处理。
- **不要**漏报重复号码——查重是本技能的底线功能，宁可多报不可漏报。
