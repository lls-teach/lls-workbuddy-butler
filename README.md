# lls-workbuddy-butler

WorkBuddy 开放平台上架管家 skill（刘老师系列）｜ 体检修复 → 引导式全自动代上架 → 收官推广物料 ｜ 一键安装：`npx skills add lls-teach/lls-workbuddy-butler`

## 这是什么

「Workbuddy开放平台上架管家」是一个面向 WorkBuddy 开放平台开发者的**代上架**技能：

- **先体检**：对技能/专家/连接器/Buddy 应用包做上架前体检（✅⚠️❌ 三级报告 + 驳回风险预判），内置 2026-10 真实提交验证过的平台解析规则（仅两级目录、display_name 双语必填、frontmatter 引号规则、3MB 上限、撤回版本号占用……）
- **再代做**：缺什么装什么（自动引导安装 ego lite 浏览器），替你完成上传 → 表单 → 头像 → 提交审核的全流程；需要你的只有两次：**扫码登录自己的账号** 和 **最终确认提交**
- **收官送物料**：上架完带你到开放平台「推广管理」生成分享链接/小程序码，推广帖文案直接发你
- **前置拦截**：没头像、没开收款账户、版本号被占用，开工前就提醒
- **SMOKE-TEST 协议**：执行遇问题先跑最小冒烟定位偏离点，修复验证后再回原任务，不反复重试同一失败动作

免费入门版：[lls-teach/lls-workbuddy-bluebook](https://github.com/lls-teach/lls-workbuddy-bluebook)（WorkBuddy 实战蓝皮书）+ 平台上的「Workbuddy开放平台上架规范」（纯规则知识库）。

## 目录结构

```
wb-open-platform-handbook-pro/
├── SKILL.md                        # 主入口：双模式（问知识/跑工作流）+ 路由表 + SMOKE-TEST 协议
├── references/
│   ├── pro-publishing.md           # ★ 管家核心：D 适配器 / A 体检 / B 类目 / C 文案 / E-0 环境自举 / E 代上架
│   ├── windows-smoke-test.md       # Windows 兼容性分流（4 处）+ 模拟冒烟记录
│   ├── skill-spec.md / expert-spec.md / connector-spec.md / buddy-app.md
│   ├── review-checklist.md / service-categories.md / monetization.md / monetization-playbook.md
│   ├── onboarding.md / overview.md / operations-profile.md / third-party-openapi.md
│   ├── market-insight.md           # 市场洞察：技能爆量五机制 + 选位/命名/时机/冷启动规则（2026-10 全量普查，数据见 skill-market-research/）
│   └── ...                         # 官方文档蒸馏知识库（16 篇官方文档）
├── scripts/refresh_docs.py         # 知识库自更新脚本（抓取官方文档到 cache，蒸馏回 references）
└── test-prompts.json               # 5 条验收测试集（darwin-skill Phase 0.5）
```

## 质量记录（darwin-skill 2.0 流程）

| 阶段 | 结果 |
| --- | --- |
| 独立 judge 基线 | 76.2 / 100（dry_run；短板：dim4 无显性检查点标记、dim8 两处断链、dim2/7 顺序颠倒） |
| 优化 | 修 E-1 悬空引用、补 macOS 安装源、3 处 🔴CHECKPOINT、Windows 引导转换规则、重排执行依赖序 |
| paired 评审 | 3-0 **better / clear**（棘轮保留） |

## 使用

在 WorkBuddy 中安装后，对它说：

- “帮我把这个技能包上架到 WorkBuddy 市场”
- “帮我体检这个技能包，看看能不能过审”
- “给我的技能写一套上架推广文案”

## 免责

社区维护、非官方。平台规则以 [open.workbuddy.cn/docs](https://open.workbuddy.cn/docs) 为准；技能内置更新协议（`scripts/refresh_docs.py` + 新鲜度检查）会随官方文档同步。
