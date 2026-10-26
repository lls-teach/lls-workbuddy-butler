---
name: liulaoshi-speed-ratchet
description: 网站或 App 性能优化技能，用"棘轮"纪律让速度只许变好不许回退。用户说网站太慢、加载卡、首屏慢、想提速/秒开/性能优化，或想知道该优化什么时使用。触发词：太慢了、提速、性能优化、首屏、秒开、加载慢、白屏。
description_zh: "以'打开到能用'为唯一北极星的性能优化工作流：先测基线、再证明指标与体感挂钩，逐项优化并用棘轮脚本锁住成果，指标变差即失败，杜绝一次性优化后回潮。"
description_en: "A performance workflow with ratchet discipline: define 'usable on open', measure a baseline, tie metrics to perceived speed, optimize item by item, and lock gains with a ratchet script — any regression fails the build."
version: 1.0.0
author: 刘洪光
---

# 刘老师 · 提速棘轮

> 优化不是一次活动，是一条只进不退的棘轮。齿咬住了，才允许拧下一圈。

## 第 0 步：定义"打开到能用"

先和用户确认一句场景化定义，全流程以此为准：

- 内容站 →「首屏正文可见」
- 后台系统 →「可点击第一项操作」
- 电商详情页 →「主图 + 价格 + 加购按钮可见」

**场景没定义就开测，测出来的都是虚荣指标。**

## 第 1 步：测基线

对目标页面跑 3 次取中位数（控制噪声），记录进 `baseline.json`：

```json
{
  "page": "https://example.com",
  "definition": "首屏正文可见",
  "metrics": { "LCP_ms": 4200, "INP_ms": 380, "CLS": 0.18, "ttfb_ms": 900 },
  "tested_at": "2026-10-24T20:00:00+08:00",
  "runs": 3
}
```

测量环境写清楚（网络制式、设备、是否缓存），否则后面没法对比。

## 第 2 步：指标与体感挂钩

每个想优化的指标，先用一句话证明它影响"打开到能用"，证明不了的不优化：

- LCP 直接对应"主内容什么时候出现" → 优
- JS 包体积本身无体感 → 只在它阻塞可交互时才追
- 找 3 个真实用户/同事的手机实测对照一次，比任何实验室数据都有说服力

## 第 3 步：按性价比排序逐项打

每一轮只打一件事，打完复测。常见性价比排序（从上往下）：

1. 图片：压缩、换 WebP/AVIF、懒加载、正确尺寸（通常是最大头）
2. 缓存：静态资源长缓存 + 文件名指纹；接口响应做合理缓存
3. 阻塞：首屏非关键 JS/CSS 延迟加载；字体 `font-display: swap`
4. 服务端：TTFB——慢查询、缺索引、无 CDN 都在这一层
5. 渲染：CLS 预留图片/广告位尺寸；长任务拆分

## 第 4 步：棘轮锁死

`scripts/ratchet.py` 把基线变成绩效合同：每次改动后重测，**任何核心指标比锁存值差超过容差即报错退出**。

```bash
# 首次：锁存当前基线
python3 scripts/ratchet.py lock --baseline baseline.json --tolerance 5

# 之后每次改动后：新测量值存 new-metrics.json，跑
python3 scripts/ratchet.py check --new new-metrics.json
# 全部不劣于锁存值（容差 5%）→ 退出码 0，并用新值滚动更新锁存
# 任一指标回退 → 退出码 1，打印哪项劣化了多少
```

把 check 挂进发布流程：棘轮没过，不许上线。

## 工作纪律

- 一次只改一类东西，改完立刻复测——一次改五项，好效果坏效果分不清
- 优化成果用"用户的话"汇报：「首屏从 4.2 秒到 1.8 秒」，不用只报得分
- 基线文件进版本库；环境变了（换机器/换网络）要重新锁齿并说明
- 参考事实：Anthropic 2026-09 工程博客记录了用"两周 + 单频道 + 小步合入"的方式把 claude.ai 关键指标提了约 3 倍，方法与本案同源：持续小步、指标挂钩、自动化守护（原文 claude.dev/blog）
