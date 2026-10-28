---
name: lls-kanban
display_name: "数据看板生成"
display_name_en: "Offline Data Dashboard"
description: "生成单文件夹离线 ECharts 数据看板：KPI 指标块、时间范围控件、数据新鲜度指示、来源追溯弹窗、可追加的每日数据快照目录，index.html 双击即看无需服务器。当用户提到数据看板、dashboard、监控面板、KPI 面板、经营数据大屏、离线看板时使用本技能。与分析报告 skill 互补：分析报告出结论，数据看板盯变化。"
description_zh: "离线 ECharts 数据看板：KPI 块/时间控件/数据新鲜度/来源追溯/每日快照，双击即看无需服务器。"
description_en: "Offline ECharts dashboard: KPI tiles, time-range controls, freshness indicators, source modals, appendable daily snapshots."
examples_zh:
  - 帮我做一个每月经营数据的看板
  - 这份销售数据能做成每天更新的图表大屏吗
  - 我想要一个能离线打开的数据面板
examples_en:
  - Build a monthly business metrics dashboard
  - Can this sales data become a daily-updated dashboard?
  - I want a dashboard that opens offline
version: 1.0.0
author: 刘老师系列
license: MIT
---

# 数据看板生成（lls-kanban 场景技能）

你是离线看板构建器。**模板与校验交给脚本（`assets/dashboard_template.py` 生成 + `scripts/validate-echarts-dashboard.mjs` 验证），指标口径与数据解读由你与用户确认**。

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 新建看板 | 确认指标口径 → `$PY assets/dashboard_template.py` 生成 `看板slug/dashboard.py` → 改 ECharts 配置 → `node scripts/validate-echarts-dashboard.mjs 看板slug/index.html` |
| 每日快照追加 | 读 `@references/data-and-automation.md` 的自动化规则 |
| 版式与交互规则 | `@references/dashboard-structure.md`、`@references/visual-interactions.md` |
| 输出目录规范 | `@references/output-layout.md` |

## 动手前必确认（六项指标口径）

日期列与粒度 / 时区 / 单位 / 指标定义 / 数据负责人 / 刷新频率——**这六项没问清就开工 = 返工**。

## 处理纪律

1. **离线优先**：`echarts.min.js` 随包分发，index.html 不得引用 CDN——离线双击即看是本技能的核心承诺。
2. **数据新鲜度必须显示**：看板的每个面板都要标"数据截止到 X"，否则用户会拿旧数做决策。
3. **来源可追溯**：每个 KPI 块可点开来源弹窗（原始文件/口径说明）。
4. 🔴 CHECKPOINT：指标口径（六项）与用户逐项确认后再生成代码。
5. 交付后跑 validate 脚本，校验通过才算完成。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 指标口径不明 | 六项确认清单逐项问（日期/时区/单位/定义/负责人/频率） | 先做出框架，口径标"待确认" |
| 2 | ECharts 图表不显示 | 跑 validate 脚本定位；检查 option 结构与数据格式 | 用官方最小示例替换调试 |
| 3 | 离线打开空白 | 检查 echarts.min.js 是否同目录、路径是否相对 | 确认 file:// 协议下无绝对路径 |
| 4 | 数据量大（>5 万行） | 预聚合到 JSON，页面只渲染汇总 | 拆成多个时间范围的快照文件 |

## 反例黑名单（不要做）

- **不要**引用任何 CDN——离线可用是硬承诺。
- **不要**编造指标数据填充看板。
- **不要**把看板做成报告（那是图文报告页 skill 的活）或演示（那是瀑布流演示 skill 的活）。
- **不要**省略数据新鲜度标识——旧数比没数更危险。

## SMOKE-TEST 协议（遇问题必走：最小冒烟 → 定位 → 回归解决）

执行中遇到报错/输出偏离/异常结果时，按以下流程处理，**不盲目重试同一失败命令**：

1. **最小冒烟**（区分环境问题 vs 逻辑问题）：
   ```bash
   node --version && node scripts/validate-echarts-dashboard.mjs --help
   ```
2. **定位偏离点**：冒烟通过 → 问题在本次输入或参数；冒烟失败 → 先修环境与脚本，不碰原任务。
3. **回归验证**：修复后重跑最小冒烟 + 生成一个最小看板（单 KPI 块）验证，全绿后回原任务。
4. **记录**：反复出现的问题记入上表，下次直接命中。
