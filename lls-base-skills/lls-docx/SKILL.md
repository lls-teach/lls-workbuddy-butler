---
name: lls-docx
display_name: Word文档处理
display_name_en: "Word Document Toolkit"
description: "处理 Word/.docx 的全能工具箱：创建中文公文/报告/通知（标题层级、列表、表格、页眉）、读取全文结构、批量替换文字、追加段落。当用户提到 Word、docx、文档、公文、通知、报告、合同文本、红头文件时使用本技能。。"
description_zh: "Word 全能处理：中文公文/报告/通知创建（标题层级、表格、页眉）、读取、批量替换、追加段落。中文字体原生。"
description_en: "All-in-one Word toolkit: create Chinese documents with headings, tables and headers, read structure, batch replace, append paragraphs."
examples_zh:
  - 写一份 Word 版的通知，要有标题和落款
  - 读一下这份合同的内容，列出所有条款
  - 把文档里所有的"甲方"替换成"委托方"
examples_en:
  - Draft a Word notice with title and signature block
  - Read this contract and list all clauses
  - Replace every "Party A" with "the Client" in this doc
version: 2.0.2
author: 刘老师系列
license: MIT
---

# Word 文档处理（lls-docx 底座 v2.0）

你是 Word 处理执行器。确定性操作调用 `scripts/`（python-docx，MIT），中文原生。

## 第 0 步：环境自举

```bash
VENV=~/.lls-venv
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q -r <skill目录>/scripts/requirements.txt
PY="$VENV/bin/python"
```

Windows（PowerShell，bash 写法不适用，`$VENV/bin/python` 路径在 Windows 下不存在）：

```powershell
py -m venv $env:USERPROFILE\.lls-venv
$env:USERPROFILE\.lls-venv\Scripts\pip install -q -r <skill目录>\scripts\requirements.txt
$PY = "$env:USERPROFILE\.lls-venv\Scripts\python.exe"
```

Windows 下没有 `printf` 管道写法时，把正文存为 UTF-8 文本文件后用 `--stdin-file 正文.txt` 代替 stdin 管道。

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 创建文档 | `$PY scripts/docx_create.py -o 输出.docx --title 标题 --stdin`（正文语法同下） |
| 读取全文 | `$PY scripts/docx_read.py 输入.docx [--json out.json]` |
| 批量替换 | `$PY scripts/docx_edit.py 输入.docx --replace "甲方=委托方" -o 新.docx` |
| 追加段落/表格 | `$PY scripts/docx_edit.py 输入.docx --append "补充：本协议自签订之日起生效。" -o 新.docx` |
| 检测修订痕迹 | `$PY scripts/docx_revisions.py 输入.docx`（插入/删除/作者，只读） |
| 转 PDF / 旧格式迁移 | `$PY scripts/docx_convert.py 输入.docx --to pdf`；`.doc → --to docx` |

**创建正文语法**（纯文本标记）：

```
# 一级标题        ## 二级标题
- 列表项          > 引用/条款
[TABLE]           下一行起每行一个制表符分隔的行，空行结束表格
普通行为正文段落，连续两行空行结束正文
```

## 步骤纪律

1. 🔴 CHECKPOINT：编辑已有文档前先 `docx_read.py` 展示将受影响的段落，确认后再改（默认输出 `_new`）。
2. 批量替换报告替换次数，0 次命中要明说；🔴 CHECKPOINT：替换预计影响 ≥20 处或整份文档时，先列出受影响段落清单，等用户确认再执行。
3. **写入后验证（必做）**：docx_create / docx_edit 完成后跑 `docx_revisions.py`（确认没留下意外修订）+ `docx_convert.py --to pdf` 转 PDF 后渲染成图抽查关键页。
4. **修订边界**：`docx_revisions.py` 能检测别人留下的修订（谁改的、改了什么），但接受/拒绝是文档所有者的裁决——不代做，明确引导到 Word/WPS。
5. 公文类请求按用户要求的格式要素逐项确认（标题、主送、正文、落款、日期）。


## 公文格式速查（要素级具体规格）

中国公文/商务函件的标准要素与 lls-docx 的对应写法（按 GB/T 9704 习惯裁剪）：

| 要素 | 写法 | 说明 |
| --- | --- | --- |
| 页眉 | `--header "单位名称 · 文件"` | 置中 9pt，可作版头 |
| 标题 | `--title "关于印发 XX 方案的通知"` | 居中 18pt；标题不带书名号、以"的通知/的函/的决定"结尾 |
| 主送 | 首行 `主送单位名称：` | 顶格，冒号结尾 |
| 正文 | 每段一行，空行分段 | 首行缩进由模板控制 |
| 附件说明 | `- 附件：1. XX 表 2. XX 清单` | 正文后、落款前 |
| 落款 | 末两行单位名 + 日期 | ⚠️ 当前仅支持左对齐；需右对齐请用户在 Word 中选中后按 Cmd/Ctrl+R |

完整可执行示例（一条命令产出合规通知）：

```bash
printf '各部门：\n\n现将有关事项通知如下：\n\n- 事项一……\n- 事项二……\n\n特此通知。\n\nXX 部门\n2026 年 10 月 27 日\n' | \
  $PY scripts/docx_create.py -o 通知.docx --title "关于 XX 的通知" --header "刘老师系列 · 内部文件"
```

写完必跑：docx_revisions.py → docx_convert.py --to pdf → 渲染核对标题居中、表格边框、落款。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 打开报错（.doc 旧格式） | 请用户另存为 .docx | 明确说明限制 |
| 2 | 中文显示为默认西文字体 | 脚本已设宋体/微软雅黑 east-asia 字体 | 用户模板字体缺失时提示 |
| 3 | 替换后个别地方没变 | 文字在文本框/页眉/批注中（python-docx 不覆盖页眉外的 story 之外的容器）→ 告知页码范围手动改 | — |
| 4 | 文档加密 | 请求用户解锁后重试 | — |

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

**做冒烟测试直到问题解决：冒烟未通过就定位、修复、重跑冒烟，循环往复，直到冒烟全部通过才算完成。**

1. **最小冒烟**（区分环境问题 vs 逻辑问题）：
   ```bash
   $PY -c "import docx" && $PY scripts/docx_create.py --help
   ```
2. **定位偏离点**：冒烟通过 → 问题在本次输入或参数，检查输入后重试；冒烟失败 → 先修依赖与脚本，不碰原任务。
3. **回归验证**：修复后重跑最小冒烟 + 一次真实最小案例，全绿后再回到原任务从失败步骤继续。
4. **记录**：反复出现的问题记入本技能失败分支表，下次直接命中。

## 反例黑名单（不要做）

- **不要**未经确认覆盖原文档。
- **不要**虚构"文档里的内容"——一切以 docx_read.py 输出为准。
- **不要**在合同/公文类任务里替用户做法律判断——只做文本处理，法务判断明确建议咨询专业人士。
- **不要**生成后不报文件路径。
