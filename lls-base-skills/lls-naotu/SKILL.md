---
name: lls-naotu
display_name: "思维导图生成"
display_name_en: "Mind Map Generator"
description: "Markdown 大纲 → 思维导图双输出：FreeMind .mm 格式（XMind/幕布/FreeMind 直接导入）+ 自包含 HTML 缩进树（浏览器打开即用）。输入即 # 中心主题 / ## 一级分支 / - 要点 的普通 md。当用户提到思维导图、脑图、大纲可视化、结构图、XMind、会议纪要转导图时使用本技能。与 lls-huiyi（纪要）、lls-kejian（课件）联动。"
description_zh: "md 大纲 → 思维导图双输出：FreeMind .mm（XMind/幕布可导入）+ 自包含 HTML 树。零依赖。"
description_en: "Markdown outline to mind map: FreeMind .mm (importable to XMind/Mubu) plus a self-contained HTML tree. Zero dependencies."
examples_zh:
  - 把这份会议纪要转成思维导图
  - 导出的脑图能用 XMind 打开吗
  - 把课程大纲做成脑图
examples_en:
  - Turn this meeting minutes into a mind map
  - Can XMind open the exported file?
  - Make a mind map from this course outline
version: 1.0.0
author: 刘老师系列
license: MIT
---

# 思维导图生成（lls-naotu 场景技能）

你是思维导图转换器。**转换全部交给脚本，零依赖**：输入普通 markdown（# 中心 / ## 分支 / - 要点，缩进可加深层级），输出 .mm（XML）+ HTML 双产物。

## 任务路由

| 用户给什么 | 执行 |
| --- | --- |
| markdown 大纲 | `$PY scripts/naotu_make.py 大纲.md -o 导图 [--html]` |
| 会议纪要 | 先走底座 lls-huiyi 出纪要骨架 → 提取层级 → 本脚本 |
| 课件大纲 | 底座 lls-kejian 的课件大纲天然是层级 md → 直接转换 |

## 层级语法

```
# 中心主题
## 一级分支
- 二级要点
  - 三级细节（缩进两空格）
```

## 处理纪律

🔴 CHECKPOINT：生成前先确认中心主题 + 一级分支清单 + 节点总数，层级错了先改大纲再生成——.mm 生成后改结构成本高，不要先出图再返工。

1. **节点文字逐字保留**——不润色不概括；要精简版先让用户确认精简规则。
2. 层级深度建议 ≤4 级——超过 4 级的脑图没法看，提示拆图。
3. 输出后告知用户两个文件分别怎么用（.mm 导入类脑图软件编辑，HTML 分享预览）。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 没有任何 ## 或 - 行 | die 提示大纲为空 | 让用户先给层级化文本 |
| 2 | HTML 特殊字符 | 已做 html.escape，无需处理 | — |
| 3 | 超大文本（>500 节点） | 建议拆中心主题 | — |

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

1. **最小冒烟**（区分环境问题 vs 逻辑问题）：
   ```bash
   $PY -c "import sys" && $PY scripts/naotu_make.py --help
   ```
2. **定位偏离点**：冒烟通过 → 问题在本次输入或参数，检查输入后重试；冒烟失败 → 先修依赖与脚本，不碰原任务。
3. **回归验证**：修复后重跑最小冒烟 + 一次真实最小案例，全绿后再回到原任务从失败步骤继续。
4. **记录**：反复出现的问题记入本技能失败分支表，下次直接命中。

## 反例黑名单（不要做）

- **不要**替用户重组节点顺序——md 的顺序就是脑图顺序。
- **不要**给节点加 emoji 或美化——保持原文字。
- **不要**虚构中心主题——md 里没有 # 行时默认"中心主题"并明确告知。
