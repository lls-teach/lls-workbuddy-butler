# 专家与专家团规范

> 来源：官方文档 /docs/expert、/docs/expert-team ｜ 同步日期：2026-10-24

## 专家基础结构

```
my-expert/
├── .codebuddy-plugin/plugin.json   # ★ 核心配置
├── avatars/expert.png              # ★ 头像
├── agents/my-expert.md             # ★ Agent 定义（frontmatter + 系统提示词）
└── README.md
```

Agent 定义文件 frontmatter：`name`（与文件名一致）、`description`（英文，AI 判断何时激活）、`displayName`{en,zh}、`profession`{en,zh}、`maxTurns`（默认 50）。

**工具由系统统一分配**（Read/Write/Grep/Glob/Bash/WebSearch/WebFetch；主理人另有 AgentTool/SendMessage），开发者不可自行添加 tools。

## plugin.json 硬性要求（过审关键）

| 字段 | 要求 |
| --- | --- |
| name / version / description / author / agents / agentName | 必填，name 用小写字母+连字符 |
| expertType | "agent"（专家）或 "team"（专家团） |
| displayName / profession / displayDescription / defaultInitPrompt / tags / quickPrompts | 必填，全部 {en, zh} 双语 |
| displayDescription | **中文必须 40–50 字**，突出核心能力 |
| tags | **恰好 3 个** |
| quickPrompts | **恰好 3 个**，第一条必须与 defaultInitPrompt 完全一致 |
| categoryId | 15 个行业分类之一（见下） |
| avatar | 相对路径 avatars/expert.png |

## 头像规范

PNG/JPG，512×512 正方形，单张 ≤500KB，统一漫画/插画风格，专业自然，符合角色定位。

## 行业分类 categoryId

01-ProductDesign 产品设计｜02-Engineering 技术工程｜03-GameSpatial 游戏空间｜04-DataAI 数据智能｜05-MarketingGrowth 营销增长｜06-ContentCreative 内容创作｜07-SalesCommerce 销售商务｜08-FinanceInvestment 金融投资｜09-OperationsHR 运营人力｜10-ProjectQuality 项目质量｜11-SecurityCompliance 法务安全｜12-IndustryConsultant 行业顾问｜13-TencentZone 腾讯专家（内部专用）｜14-WorldWise 全球发展｜15-Education 教育学习

## 专家团增量要求

- `expertType: "team"` + `teamInfo: {leadAgent, memberAgents[]}` + `members[]`（含 role: "lead"/"member"，每人独立头像与双语 name/profession）。
- 主理人 agent 文件名必须带团队专属前缀（如 `trading-team-lead.md`，不可通用 team-lead）。
- `profession` 必须与 `displayName` 一致。
- 可选 `skills/` 共享技能目录。
- 主理人提示词铁律（官方模板口径）：TeamCreate 只能主理人执行；专业产出必须由对应成员输出、主理人只编排汇编；跨成员信息流必须经主理人中转；禁止代写成员产出、禁止跳阶段、禁止 spawn 自己。建议在提示词中写明分阶段 SOP 与成员职责表。

## 内置 MCP / 连接器依赖（可选）

仅当专家必须调外部 MCP 或已上架连接器时声明：plugin.json 的 `dependencies`（mcpServers 指向 .mcp.json；connectors 填连接器 ID 如 "tencent-docs"）。用户召唤时弹出内联引导卡逐个连接。x-workbuddy 元信息支持 OAuth/Token 表单（tokenSchema 定义字段，值回填 headers 的 ${VAR} 占位）。**包内严禁硬编码真实 Token/密钥**。

官方模板下载：design-experts.zip（专家）、trading-team.zip（专家团），见文档页链接。
