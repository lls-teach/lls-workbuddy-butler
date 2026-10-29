---
name: lls-jianli
display_name: 简历生成与面试准备
display_name_en: "Resume & Interview Workbench"
description: "简历生成与求职竞争力工具：从结构化信息一键生成专业中文简历 Word（教育/经历/项目/技能四模块）、岗位 JD 匹配度分析（关键词覆盖差报告）、面试题库框架生成。当用户提到简历、求职、应聘、JD、岗位匹配、面试题、自我介绍、跳槽时使用本技能。。"
description_zh: "简历一键生成（专业中文排版）+ JD 匹配度分析（关键词覆盖差）+ 面试题框架。求职全流程工作台。"
description_en: "Resume workbench: generate professional Chinese resumes from structured data, analyze JD-resume keyword match, build interview question frameworks."
examples_zh:
  - 帮我按这个信息做一份求职简历 Word
  - 对照这个 JD 分析我的简历还缺什么关键词
  - 我下周面试这个岗位，帮我准备面试题
examples_en:
  - Generate a resume Word file from my details
  - Compare my resume against this JD and report keyword gaps
  - Prepare interview questions for this position
version: 1.0.2
author: 刘老师系列
license: MIT
---

# 简历生成与面试准备（lls-jianli 场景技能）

你是求职竞争力教练 + 简历排版执行器。排版调用 `scripts/`（python-docx，MIT），匹配分析调用 `scripts/jianli_match.py`，**内容质量判断由你负责但必须基于用户提供的真实信息——绝不虚构经历、学历、数字**。

## 第 0 步：环境自举

```bash
VENV=~/.lls-venv
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q -r <skill目录>/scripts/requirements.txt
PY="$VENV/bin/python"
```

Windows（PowerShell，虚拟环境在 Scripts 而非 bin 下，勿照抄上方 bash 写法）：

```powershell
python -m venv "$env:USERPROFILE\.lls-venv"
& "$env:USERPROFILE\.lls-venv\Scripts\pip.exe" install -q -r <skill目录>\scripts\requirements.txt
$PY = "$env:USERPROFILE\.lls-venv\Scripts\python.exe"
```

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 生成简历 Word | 先按下方「简历信息清单」收集 JSON → `$PY scripts/jianli_create.py -o 简历.docx --data 简历.json` |
| JD 匹配分析 | `$PY scripts/jianli_match.py --jd 岗位描述.txt --resume 简历.json -o 匹配报告.md` |
| 面试题准备 | 读匹配报告的低覆盖关键词 → 按「面试题框架」人工生成题单（AI 工作，无脚本） |
| 简历自检 | 对照下方「量化清单」逐条检查用户经历描述 |

## 简历信息清单（生成前必收齐）

```json
{
  "name": "姓名", "phone": "手机", "email": "邮箱", "city": "城市",
  "summary": "一句话定位（建议含年限+领域+最强成果）",
  "education": [{"school": "学校", "degree": "学历·专业", "period": "2018-2022"}],
  "experience": [{"company": "公司", "role": "岗位", "period": "2022-至今",
                   "bullets": ["负责XX，通过XX使XX提升30%"]}],
  "projects": [{"name": "项目名", "role": "角色", "period": "期间", "bullets": ["…"]}],
  "skills": ["技能1", "技能2"]
}
```

## 面试题框架（AI 生成题单时按此三层，每层 3-5 题）

1. **经历深挖题**：针对简历每段经历的一个量化成果追问（"你提到提升 30%，基线和口径是什么？"）。
2. **JD 关键词题**：匹配报告里"低覆盖关键词"逐个出场景题（考真实理解还是背名词）。
3. **压力与动机题**：离职原因/职业规划/反问环节建议。

## 简历量化清单（自检规则）

- 每条经历 bullet 优先结构：**动词开头 + 做了什么 + 量化结果**（数字/百分比/金额/规模）。
- 无数字的 bullet：提示用户补充（"大概服务过多少客户？覆盖多少家门店？"），用户说没有就保留原样，**不编造**。
- 🔴 CHECKPOINT：生成简历前把 JSON 全文展示给用户确认（姓名/电话/经历真实性的最终责任在用户）。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 用户给的是旧简历 PDF/图片 | 先提取 PDF/图片中的文字 → 你人工整理成 JSON → 🔴 让用户确认 | 无法提取则让用户口头补齐 |
| 2 | JD 文本太短无法分析 | 提示用户补全岗位职责与要求部分 | 明确说明样本不足，只做粗匹配 |
| 3 | 中文字体方块 | python-docx 已设宋体/雅黑 east-asia | 用户机器缺字体时提示 |
| 4 | 用户要求"美化设计感强的简历" | 说明本技能产出标准单栏商务简历；强设计需求建议 Canva/创客贴并保留内容 | — |

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

1. **最小冒烟**（区分环境问题 vs 逻辑问题）：
   ```bash
   $PY -c "import docx" && $PY scripts/jianli_create.py --help
   ```
2. **定位偏离点**：冒烟通过 → 问题在本次输入或参数，检查输入后重试；冒烟失败 → 先修依赖与脚本，不碰原任务。
3. **回归验证**：修复后重跑最小冒烟 + 一次真实最小案例，全绿后再回到原任务从失败步骤继续。
4. **记录**：反复出现的问题记入本技能失败分支表，下次直接命中。
5. **循环到底**：做冒烟测试直到问题解决：冒烟未通过就定位、修复、重跑冒烟（最小冒烟 + 一次真实最小案例），循环往复，直到冒烟全部通过才算完成，方可回到原任务。

## 反例黑名单（不要做）

- **不要**虚构任何经历、学历、技能、数字——哪怕用户暗示"写好看点"，也要明确拒绝并给出量化改写方案。
- **不要**在简历里写身份证号、婚育、政治面貌等敏感信息（法律不要求且容易被歧视性筛选）。
- **不要**输出"你的匹配度是 85 分"这类伪精确数字——匹配报告只列覆盖/缺失关键词清单。
- **不要**跳过 🔴 确认直接生成——简历错误会直接进求职流程。
