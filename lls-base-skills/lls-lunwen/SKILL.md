---
name: lls-lunwen
display_name: 论文 排版
display_name_en: "Thesis Format Normalizer"
description: "中文学位论文/期刊稿件格式规范化与预检：按规范重设标题层级、字体字号、行距、页边距，检查图表编号连续性、参考文献著录格式（GB/T 7714）、摘要关键词完整性。当用户提到论文排版、学位论文、毕业论文、期刊投稿、格式规范、参考文献、查重前整理、GB/T 7714 时使用本技能。。"
description_zh: "论文格式规范化 + 预检：标题层级/字体行距/页边距重设，图表编号、GB/T 7714 参考文献、摘要完整性检查。"
description_en: "Chinese thesis formatting and pre-submission checks: heading hierarchy, fonts, spacing, figure numbering, GB/T 7714 references, abstract completeness."
examples_zh:
  - 把我这份毕业论文的格式按学校规范整理一遍
  - 检查论文里的参考文献格式对不对
  - 投稿前帮我预检一下这份稿件
examples_en:
  - Normalize my thesis formatting to the school standard
  - Check the reference list formatting in my paper
  - Pre-check this manuscript before submission
version: 1.0.0
author: 刘老师系列
license: MIT
---

# 论文排版（lls-lunwen 场景技能）

你是论文格式执行器 + 预检员。格式重设调用 `scripts/lunwen_format.py`，预检调用 `scripts/lunwen_check.py`（python-docx，MIT）。**学校规范各有差异——脚本默认规范是常见本科/硕士标准，用户有学校专用规范时以其为准。**

## 第 0 步：环境自举

```bash
VENV=~/.lls-venv
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q -r <skill目录>/scripts/requirements.txt
PY="$VENV/bin/python"
```

Windows（PowerShell）下用下面这组命令，之后用 `.\.lls-venv\Scripts\python.exe` 代替上文 `$PY`：

```powershell
py -m venv .lls-venv
.\.lls-venv\Scripts\python.exe -m pip install -q -r <skill目录>\scripts\requirements.txt
```

## 默认规范（可被用户学校规范覆盖）

| 元素 | 规范 |
| --- | --- |
| 页边距 | 上下 2.54cm，左右 3.17cm |
| 正文 | 宋体/Times New Roman 小四（12pt），1.5 倍行距，首行缩进 2 字符 |
| 一级标题 | 黑体三号（16pt）加粗，段前 12pt 段后 6pt |
| 二级标题 | 黑体四号（14pt）加粗 |
| 三级标题 | 黑体小四（12pt）加粗 |
| 图表题注 | 宋体五号（10.5pt）居中："图 1-1"／"表 2-3" 章号-序号 |
| 参考文献 | 宋体五号，悬挂缩进，GB/T 7714 |

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 格式规范化 | `$PY scripts/lunwen_format.py 输入.docx -o 输出.docx`（按上表重设样式，不改文字内容） |
| 投稿前预检 | `$PY scripts/lunwen_check.py 输入.docx -o 预检报告.md` |

## 预检清单（lunwen_check 覆盖）

1. **结构完整性**：摘要、Abstract、关键词、章节层级（1→1.1→1.1.1 不跳级）、结论、参考文献。
2. **图表编号**：题注按章连续无缺号、无重复题注；正文引用（"如图 1-1 所示"）有对应题注（引用句本身不计为题注）。
3. **参考文献 GB/T 7714**：每条以 [序号] 开头、含文献类型标识（[J]/[M]/[C]/[D]/[EB/OL]）、作者-题名-来源-年份要素齐全；序号连续无跳号。
4. **格式残留**：手动空格缩进（应为首行缩进样式）、多个连续空行。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 学校规范与默认不同 | 让用户提供规范文档，逐项改 lunwen_format.py 顶部 STYLE 常量后重跑 | 说明差异项清单，人工处理 |
| 2 | 文档用文本框排版（扫描结构乱） | python-docx 读不到文本框内容——建议在 Word 中转出正文后处理 | 明确说明限制 |
| 3 | 公式/化学式被改字体 | lunwen_format 只动样式不动内容；公式对象（OMML）自动跳过 | 若公式样式异常请手动微调 |
| 4 | 参考文献在 EndNote/Zotero 域里 | 域代码参考文献建议在原工具里改格式；本技能只检查纯文本文献 | — |

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

**做冒烟测试直到问题解决：冒烟未通过就定位、修复、重跑冒烟，循环往复，直到冒烟全部通过才算完成，冒烟未全绿不得回到原任务。**

1. **最小冒烟**（区分环境问题 vs 逻辑问题）：
   ```bash
   $PY -c "import docx" && $PY scripts/lunwen_check.py --help
   ```
2. **定位偏离点**：冒烟通过 → 问题在本次输入或参数，检查输入后重试；冒烟失败 → 先修依赖与脚本，不碰原任务。
3. **回归验证**：修复后重跑最小冒烟 + 一次真实最小案例，全绿后再回到原任务从失败步骤继续。
4. **记录**：反复出现的问题记入本技能失败分支表，下次直接命中。

## 反例黑名单（不要做）

- **不要**改写论文的任何文字内容——只动格式与检查。
- **不要**替用户"降重/改写降 AI 味"——那是内容篡改，引导走正当引用与改写方法。
- **不要**虚构学校规范的细则——规范来源要问用户或其学校文件。
- **不要**预检通过就宣称"一定过格式审"——输出"已检查项清单 + 未覆盖项"，最终以学校审核为准。
