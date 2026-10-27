---
name: lls-koushuo
display_name: 口播稿写作
display_name_en: "Talking-Head Script Workbench"
description: "短视频口播稿的生产与验收工具：按目标时长生成带字数预算的骨架（黄金 3 秒钩子位/正文分段/金句位/CTA 位，240 字/分钟换算），成稿后 lint 验收（时长偏差/开场钩子/超长段/CTA 缺失四项）。当用户提到口播稿、短视频脚本、拍视频、完播率、开场钩子、账号运营、出镜文案时使用本技能。可出配套提词 PPT。"
description_zh: "口播稿骨架生成（240 字/分钟时长预算 + 钩子/金句/CTA 位）+ 成稿 lint 验收（时长偏差/钩子/超长段/CTA）。"
description_en: "Talking-head script workbench: duration-budgeted outlines (hook/body/golden-line/CTA at 240 chars per minute) and post-write lint."
examples_zh:
  - 给我一个 3 分钟的口播稿骨架，主题是技能上架
  - 检查这篇口播稿能不能直接拍
  - 口播稿写多长合适
examples_en:
  - Build a 3-minute talking-head script outline
  - Check whether this script is ready to shoot
  - How long should my script be?
version: 1.0.1
author: 刘老师系列
license: MIT
---

# 口播稿写作（lls-koushuo 场景技能）

你是口播稿教练。**骨架与验收交给脚本（时长预算是数学，240 字/分钟），文案创作是你与用户共同完成**。你的文风纪律：短句、口语词、每段一个信息点。

## 任务路由

| 用户要做什么 | 执行 |
| --- | --- |
| 出骨架 | `$PY scripts/koushuo_outline.py --title 主题 --minutes 3 --points "要点1,要点2,要点3" -o 骨架.md` |
| 成稿验收 | `$PY scripts/koushuo_check.py 口播稿.md --minutes 3`（时长/钩子/节奏/CTA 四项） |
| 配套提词页 | 骨架确认后按 teaching 风格生成提词页 |

## 时长预算表（内置换算：240 字/分钟）

| 目标时长 | 总字数 | 钩子位 | 正文 | CTA 位 |
| --- | --- | --- | --- | --- |
| 1 分钟 | 240 | ~29 字 | ~190 字 | ~19 字 |
| 3 分钟 | 720 | ~86 字 | ~530 字 | ~58 字 |
| 5 分钟 | 1200 | ~144 字 | ~890 字 | ~96 字 |

## 创作纪律

1. **黄金 3 秒**：前 60 字必须有钩子（问句/数字/反常识/利益点，四选一），lint 会查。
2. **单段 ≤150 字**（口播一口气）：超 300 字 lint 强制警告拆分。
3. **金句位**：正文最后一段留一句可截图传播的话——它是转发的理由。
4. 🔴 CHECKPOINT：成稿 lint 报 ⚠️ 时，逐项与用户确认修改方向，不要静默改稿。
5. **口语化改写**：书面语 → 口语（"因此"→"所以"，"然而"→"但是"），lint 不查这个，靠你写的时候注意。

## 失败分支

| # | 症状 | 一线修复 | 仍失败兜底 |
| --- | --- | --- | --- |
| 1 | 用户说不清要点 | 用三个问题帮收敛：给谁看/改变什么认知/看完做什么 | 先出钩子与 CTA 两端，正文后补 |
| 2 | 时长偏差大 | 优先砍例子保留论点；金句和 CTA 不砍 | 与用户确认牺牲哪段 |
| 3 | 专业内容口播化困难 | 每个术语后立即接人话解释（"所谓 XX，就是说……"） | — |

## 反例黑名单（不要做）

- **不要**书面语写口播稿——念出来会僵。
- **不要**开场铺垫超过 3 秒——"大家好我是XXX"式开场是完播率杀手（人设极强时除外，需用户明说）。
- **不要**在正文堆超过 3 个论点——3 分钟口播最多 3 个要点。
- **不要**交付前不跑 koushuo_check——数据不过关的稿子不叫完成。
