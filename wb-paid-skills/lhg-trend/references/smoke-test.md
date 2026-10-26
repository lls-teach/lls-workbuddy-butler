# 标准冒烟测试（skill 自检用）

> 触发时机：SKILL.md「自检与反馈」命中疑似自身缺陷时运行。
> 说明：`scripts/smoke_test.py` 校验 skill **产出物**（热点扫描报告）是否遵守
> Phase 3 纪律（30 天窗口、热度数字可查、信源失效诚实降级、热点三件套）；
> 以下用例用最小 fixture 反向验证脚本本身的检查能力。
> 以下全部用例已于 2026-09-29 实测通过。

## S-1 诚实降级（核心场景）

- 目的：健康检查已标某信源"不可用/未采用"，报告正文就不得再归因该信源的热度数字——这是本 skill区别于"硬凑数"的关键纪律。
- fixture：`references/fixtures/fixture-fabricated.md`（健康检查标 X平台 ❌ 不可用，但关键事实里写了"X平台 相关推文转推 5.2 万"）
- 期望 FAIL：
  ```bash
  python3 scripts/smoke_test.py references/fixtures/fixture-fabricated.md
  ```
  → 退出码 1，FAIL 含 `W-3 诚实降级失败`
- 反向期望 PASS（证明 W-3 是"归因行为"在触发，而非信源名本身误伤）：
  ```bash
  python3 scripts/smoke_test.py references/fixtures/fixture-honest.md
  ```
  → 退出码 0，`✅ 冒烟测试全绿`（honest 版同样提到 X平台，但只出现在"跟进查询建议信源"中，未归因热度数字）

## S-2 30 天窗口声明

- fixture：`references/fixtures/fixture-missing-window.md`（标题无起止日期）
- ```bash
  python3 scripts/smoke_test.py references/fixtures/fixture-missing-window.md
  ```
  → 退出码 1，FAIL 含 `W-1 窗口声明缺失`

## S-3 热点三件套完整性

- fixture：`references/fixtures/fixture-missing-triple.md`（第 1 个候选缺"建议切入角度"）
- ```bash
  python3 scripts/smoke_test.py references/fixtures/fixture-missing-triple.md
  ```
  → 退出码 1，FAIL 含 `W-4` 与 `切入角度`

## S-4 人工检查项（脚本扫不到的）

- [ ] 抽查 3 个热度数字：出处链接是否真实可打开，平台+日期是否对得上
- [ ] 健康检查节抽查：标 ✅ 的信源是否真的可达，有无把"没去查"写成"正常"
- [ ] 发现模式候选排序抽查：榜单顺序是否真按跨平台热度排，有无把编辑精选当热度
- [ ] 多方观点对照抽查：看空/看多双方是否都有真实出处，有无只找一面
- [ ] 动量判断抽查："升温/见顶"是否有热度曲线依据，还是拍脑袋
- [ ] 全文 grep 平台专有工具名（如 WebSearch/WebFetch/subagent_type/TodoWrite）：必须零残留
