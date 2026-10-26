# 标准冒烟测试（skill 自检用）

> 触发时机：SKILL.md「自检与反馈」命中疑似自身缺陷时运行。
> 说明：`scripts/smoke_test.py` 校验「取数决策记录」是否符合本 skill 硬性规则
> （NOT-for 收窄、分工指路、降级路由、开工声明、安全默认）；
> 以下用例用最小 fixture 反向验证脚本本身的检查能力，属于 skill 级冒烟。
> 以下全部用例已于 2026-09-29 实测通过。

## S-1 纯取数全绿

- fixture：`references/fixtures/fixture-decision-good.md`（B 站取数，首选可用，开工声明完整，动作只读）
- ```bash
  python3 scripts/smoke_test.py references/fixtures/fixture-decision-good.md
  ```
  → 退出码 0，`✅ 冒烟测试全绿`

## S-2 后端失效时降级路由选择正确

- fixture：`references/fixtures/fixture-decision-degrade.md`（微博首选探针超时，备选1可用，决策选备选1）
- ```bash
  python3 scripts/smoke_test.py references/fixtures/fixture-decision-degrade.md
  ```
  → 退出码 0，`✅ 冒烟测试全绿`

## S-3 后端失效仍选首选（反例）

- fixture：`references/fixtures/fixture-decision-degrade-bad.md`（同场景但决策仍选失效的首选）
- ```bash
  python3 scripts/smoke_test.py references/fixtures/fixture-decision-degrade-bad.md
  ```
  → 退出码 1，FAIL 含 `C3 降级路由错误`

## S-4 开放式调研被正确指路到 lhg-deep-research

- fixture：`references/fixtures/fixture-decision-research.md`（"研究产业链来龙去脉"，指路 lhg-deep-research）
- ```bash
  python3 scripts/smoke_test.py references/fixtures/fixture-decision-research.md
  ```
  → 退出码 0，`✅ 冒烟测试全绿`

## S-5 开放式调研被误触发（反例）

- fixture：`references/fixtures/fixture-decision-research-bad.md`（同请求但 lhg-net 自处理）
- ```bash
  python3 scripts/smoke_test.py references/fixtures/fixture-decision-research-bad.md
  ```
  → 退出码 1，FAIL 含 `C1 NOT-for 违规`

## S-6 工具轨全挂走纯流程降级

- fixture：`references/fixtures/fixture-decision-flow.md`（公众号 RSS/网页版均失效，选纯流程降级）
- ```bash
  python3 scripts/smoke_test.py references/fixtures/fixture-decision-flow.md
  ```
  → 退出码 0，`✅ 冒烟测试全绿`

## S-7 动作清单含写入动作（反例）

- fixture：`references/fixtures/fixture-decision-write-action.md`（动作含"评论区留言互动"）
- ```bash
  python3 scripts/smoke_test.py references/fixtures/fixture-decision-write-action.md
  ```
  → 退出码 1，FAIL 含 `C5 安全默认违规`

## S-8 热点选题指路 lhg-trend

- fixture：`references/fixtures/fixture-decision-trend.md`（"最近有什么热点适合写选题"，指路 lhg-trend）
- ```bash
  python3 scripts/smoke_test.py references/fixtures/fixture-decision-trend.md
  ```
  → 退出码 0，`✅ 冒烟测试全绿`

## S-9 人工检查项（脚本扫不到的）

- [ ] 体检真实性抽查：最近一次"能力体检"是否真发了探针，而非凭感觉假设后端可用
- [ ] 降级声明抽查：走纯流程降级/覆盖不全备选时，交付物是否写清了覆盖范围
- [ ] 分工抽查：取数交付物里是否混入了"这说明…"类分析结论（应留给调用方）
- [ ] 并行收集抽查：多平台任务是否独立收集后再汇总，而非边抓边下结论
- [ ] Cookie 抽查：登录态文件是否只存本地、未进仓库
