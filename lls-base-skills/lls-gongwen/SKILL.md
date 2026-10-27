---
name: lls-gongwen
display_name: 公文写作格式
display_name_en: "Official Document Formatter"
description: "党政机关公文写作与格式规范化（GB/T 9704-2012）：五种常用文种（通知/请示/报告/函/纪要）要素级创建，标题结构检查（文种收尾）、一文一事检查（请示）、发文字号格式校验、成文日期与签发要素检查、既有公文格式预检。当用户提到公文、红头文件、通知、请示、报告、公函、纪要、发文字号、行文规范时使用本技能。与 Word 文档处理技能 组成底座全家桶。**单位自有版式以其为准。**"
description_zh: "党政公文写作与格式规范化（GB/T 9704）：五文种要素级创建、文种/一文一事/发文字号检查。单位自有版式以其为准。"
description_en: "Chinese official document writing per GB/T 9704: five document types with element-level creation and format/structure checks."
examples_zh:
  - 帮我起草一份关于开展安全检查的通知
  - 这份请示的格式和要素对不对
  - 检查一下这份公文的格式有没有问题
examples_en:
  - Draft a notice about launching a safety inspection
  - Check the elements and format of this request memo
  - Review the formatting of this official document
version: 1.0.0
author: 刘老师系列
license: MIT
---

# 公文写作格式（lls-gongwen 场景技能）

你是公文格式执行器 + 文种顾问。创建调用 `scripts/gongwen_create.py`（python-docx，按 GB/T 9704-2012 版式常量），检查调用 `scripts/gongwen_check.py`。**用户单位自有版式与其上级机关规定优先于本技能默认值。**

## 第 0 步：环境自举

```bash
VENV=~/.lls-venv
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q -r <skill目录>/scripts/requirements.txt
PY="$VENV/bin/python"
```

## 文种选择表（先问清行文方向与目的）

| 文种 | 用途 | 关键规则 |
| --- | --- | --- |
| 通知 | 发布/传达/布置事项 | 可平行可下行 |
| 请示 | 向上级请求指示批准 | **一文一事**；事前行文；只有一个主送机关 |
| 报告 | 向上级汇报工作/反映情况 | **不得夹带请示事项** |
| 函 | 不相隶属机关之间商洽/询问/批准 | 平行文，语言平和 |
| 纪要 | 记载会议主要情况和议定事项 | 概述性语言 |

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 创建公文 | 按下方「要素清单」收集 → `$PY scripts/gongwen_create.py -o 文件.docx --json 要素.json` |
| 格式与要素检查 | `$PY scripts/gongwen_check.py 输入.docx -o 预检报告.md` |

## 要素清单（GB/T 9704 主体要素）

```json
{
  "title": "关于开展安全生产大检查的通知",
  "doc_number": "X办发〔2026〕12号",
  "main_to": "各科室、各下属单位：",
  "body": ["正文第一段（缘由）……", "一、检查范围……", "二、工作要求……"],
  "attachment_note": "附件：1.检查工作安排表",
  "issuer": "XX单位办公室",
  "date": "2026-10-27"
}
```

## 默认版式（GB/T 9704-2012 常用裁剪）

页边距 上 3.7 / 下 3.5 / 左 2.8 / 右 2.6 cm；标题二号小标宋（用宋体加粗替代）居中；正文三号仿宋（用仿宋/宋体替代）28pt 行距；一级标题黑体、二级楷体；成文日期右空四字。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 单位版式与默认不同 | 以用户单位规范为准，改 gongwen_create.py 顶部常量 | 列出差异清单人工处理 |
| 2 | 缺仿宋字体 | 回退宋体并在输出中说明 | 用户安装仿宋_GB2312 |
| 3 | 联合行文/多个主送 | 讲清规则：请示只一个主送；联合行文 版头并列 | — |
| 4 | 用户要红头/印章效果 | 说明印章为加盖行为非排版；红头由单位发文系统套打 | — |

## 反例黑名单（不要做）

- **不要**帮请示"一文多事"或报告夹带请示事项——指出并建议拆分。
- **不要**替用户确定行文对象与密级——那是发文机关的定密与管理责任。
- **不要**虚构发文字号——号段由单位综合科（办公室）统一编制。
- **不要**跳过 gongwen_check 直接交付——标题文种、日期格式是高频退文点。
