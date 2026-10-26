---
name: liulaoshi-chart-visualization
description: 数据可视化选型与生成技能。用户想把一组数据画成图、不知道选什么图，或直接点名某类图（柱/线/饼/散点/热力/桑基/雷达/地图等）时使用。触发词：画个图、可视化、图表、趋势图、占比、分布、画个饼图/柱状图/折线图。
description_zh: "按'先答问题再选图'的原则做可视化：先判断用户要回答的比较/趋势/构成/分布/关系哪类问题，给出选型与替代方案，再用 ECharts 产出可打开的单文件 HTML 图表，数字与源数据逐项对齐。"
description_en: "Question-first data visualization: identify whether the user is asking a comparison, trend, composition, distribution, or relationship question, recommend a chart type (with an alternative), then generate a self-contained ECharts HTML file whose numbers reconcile with the source data."
version: 1.0.0
author: 刘洪光
---

# 刘老师 · 图表选型与生成

## 核心原则：先答问题，再选图

一张图只能回答一类问题。选型前先问自己：用户想从这份数据里**看懂什么**？

| 用户的问题 | 首选 | 备选 | 避免 |
| --- | --- | --- | --- |
| 谁多谁少（分类比较） | 柱状图 | 条形图（类目名长时） | 饼图超过 5 块 |
| 怎么变的（时间趋势） | 折线图 | 面积图（单序列） | 双轴滥用 |
| 由什么组成（构成） | 堆叠柱状图 | 饼图/环形图（≤5 块且合计 100%） | 三维饼图 |
| 散布在哪（分布） | 直方图 / 箱线图 | 小提琴图 | 折线（无时间含义时） |
| 什么相关（关系） | 散点图 | 气泡图（加第三维） | 连线图 |
| 层级在哪（树状结构） | 矩形树图 | 旭日图 | — |
| 怎么流动（流向） | 桑基图 | 弦图 | — |
| 密度在哪（地理） | 地图着色 / 散点地图 | 热力图 | — |
| 指标完成度 | 仪表盘 / 进度条 | — | — |

**两条硬规则**：
1. 饼图块数超过 5 时改用条形图并按值排序——人眼比较长度远准于比较角度
2. 双 Y 轴只在两个量纲确实需要并排对比时使用，且必须在图注里写明左右轴各是什么

## 生成方式：单文件 ECharts HTML

默认产出**一个自包含的 HTML 文件**（内嵌数据与配置，不依赖网络也能打开）：

```html
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
</head><body>
<div id="chart" style="width:100%;height:600px"></div>
<script>
  const chart = echarts.init(document.getElementById('chart'));
  // option 写在这里
  chart.setOption({ /* ... */ });
  window.addEventListener('resize', () => chart.resize());
</script>
</body></html>
```

生成后逐项核对：**图上每个数字必须能在源数据里指出来**；汇总口径（是否含税、是否去重）写在图注里。用户要图片时，打开 HTML 截图导出，不要手画。

## 排版基线（本技能默认审美）

- 标题说结论，不说数据类型：写「华东区贡献 42% 增量」，不写「各地区销售额」
- 序列颜色不超过 6 种；同类序列同色系渐变，重点序列用强调色
- Y 轴从 0 开始（折线图看趋势除外，但要标注截断）
- 数据标签只在关键点标（最大、最小、最新），全部标注等于没标
- 图注三要素：口径、时间窗、数据来源，缺一处都可能被读者挑战

## 环境说明

- ECharts 走 CDN 引入；用户环境离线时，提示"需要联网打开一次"或改用本地 echarts 包
- 用户环境有 Node 且装了 echarts 依赖时，可改用服务端渲染出 PNG（`echarts` SSR 模式），脚本自行编写即可
- 用户点名了具体图型时按用户要求画，但发现更优选型时给一句建议，不擅自替换
