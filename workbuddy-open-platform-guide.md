# WorkBuddy 开放平台实战手册

> 基于 open.workbuddy.cn 全部 16 篇官方文档整理（2026-10），面向个体工商户开发者，覆盖入驻 → 开发 → 审核 → 变现 → 运营全链路。

## 0. 平台是什么

- WorkBuddy 是腾讯的 AI Agent 客户端（PC 本地助理 + 云端任务 + 多 Agent 协作）。开放平台让开发者把行业 know-how 做成标准化资产上架市场，触达 WorkBuddy 用户。
- 开发者入口：open.workbuddy.cn（登录 / 立即入驻）
- 联系：openworkbuddy@tencent.com；首页下方有官方社群二维码
- 开发者全流程：注册入驻 → 资质认证 → 创建资产 → 配置调试 → 提交审核 → 发布 → 看运营数据迭代

## 1. 入驻认证（个体工商户走企业认证）

**关键结论：个体工商户属于"持有营业执照的经营主体"，必须走企业认证，不是个人认证。**

| 认证方式 | 适用场景 | 验证方式 |
| --- | --- | --- |
| 企业法人实名认证 | 通用 | 法人本人扫码人脸核身 + 四要素核验 |
| 腾讯云账号快速认证 | 已在腾讯云完成企业实名 | 扫码授权，比对主体一致性 |
| 微信公众号/小程序快速认证 | 已在微信完成企业认证 | 扫码授权，比对主体一致性 |

准备材料：营业执照、管理员（本人）身份证 + 实名手机号 + 邮箱 + 能人脸识别的手机；选法人认证还需法人身份证号。

规则：
- 每账号最多认证 10 个企业主体；同企业最多被 50 个账号认证
- 认证后完成者成为超级管理员；认证只采实名信息，对外展示的头像/昵称/简介在「设置 → 开发者信息」里填
- 组织机构认证仅限无执照单位；个人认证一证一号
- 不支持海外主体

开发者资料规范（审核红线）：
- 头像 512×512px，≤5000KB，JPG/PNG
- 昵称 2–20 字符，全平台唯一；禁纯数字/表情；禁"官方、平台、客服、管理员、admin"；禁仿冒腾讯系品牌；禁"认证、VIP、第一、独家、保证"；禁"测试、test、demo、试用"
- 简介 20–120 字符，不得夸大、虚假、无法验证
- 联系方式 1–5 项：官网 / 邮箱 / 微信公众号 / 自定义平台
- 违规处置：恢复默认头像、兜底文案、隐藏联系方式、限制主页、下架

## 2. 六类资产怎么选

| 资产 | 形态 | 适合做什么 | 能否付费 |
| --- | --- | --- | --- |
| 技能 Skill | SKILL.md（YAML frontmatter + 正文）+ references/ + scripts/ + templates/ | 可复用的任务指令、工作流 | ✅ 买断/按月 |
| 专家 | .codebuddy-plugin/plugin.json + agents/*.md + 头像 | 单角色 AI 顾问（人设化） | ✅ 买断/按月 |
| 专家团 | expertType=team，主理人 + 多成员 + 可共享 skills | 多角色 SOP 协作（演示效果最强） | ✅ 买断/按月 |
| 连接器 | MCP + Skill（推荐）或 CLI + Skill | 接第三方服务/自有 API | ❌（暂仅免费） |
| Buddy 应用 | 平台表单配置的"行业 AI Harness" | 垂直行业工作台（要企业主体） | 企业单授权（B2B） |
| 第三方应用 | OAuth 2.1 + Open API / 分享 SDK | 硬件接入、积分兑换、分享回跳 | 积分核销等 |

### 2.1 技能（Skill）

```
{skill-name}/
├── SKILL.md          # 必须，YAML frontmatter + Markdown 指令正文
├── references/       # 可选，补充知识（@references/xxx.md 引用）
├── scripts/          # 可选，可执行脚本（AI 用 Bash 调）
└── templates/        # 可选，模板文件
```

Frontmatter 必填：`description`（写清用途和触发词）、`description_zh`、`description_en`、`version`、`author`。常用可选：`allowed-tools`（工具白名单）、`disable-model-invocation: true`（仅手动触发）、`user-invocable: false`（隐藏菜单仅 AI 内部用）。

创建方式：客户端市场【添加技能 → 创建技能】对话式创建，或开放平台上传 zip。解析失败先对照结构自查，再发邮件/进社群。

### 2.2 专家（plugin.json 关键硬性要求）

目录：`.codebuddy-plugin/plugin.json` + `agents/{name}.md`（frontmatter：name/description/displayName/profession/maxTurns 默认 50）+ `avatars/expert.png`。

- 展示字段全是 {zh, en} 双语，缺气回退 zh → en
- `displayDescription` 中文必须 40–50 字
- `tags` 恰好 3 个；`quickPrompts` 恰好 3 个，且第一条必须与 `defaultInitPrompt` 完全一致
- `categoryId` 从 15 个行业分类选（01-ProductDesign … 15-Education，13-TencentZone 是腾讯内部专用）
- 头像 512×512，≤500KB，统一漫画/插画风格
- **不可自定义 tools**：工具由系统分配（Read/Write/Grep/Glob/Bash/WebSearch/WebFetch；主理人另有 AgentTool/SendMessage）
- 可声明 `dependencies`：内置 MCP（.mcp.json，支持 OAuth/Token 表单 x-workbuddy 元信息）或已上架连接器 ID；用户召唤时内联引导连接
- 严禁硬编码任何真实 Token/密钥

### 2.3 专家团（在专家基础上的增量要求）

- `expertType: "team"` + `teamInfo: {leadAgent, memberAgents}`
- 主理人 agent 文件名必须带团队专属前缀（不可通用 `team-lead`），如 `trading-team-lead.md`
- `profession` 必须与 `displayName` 一致
- `members` 数组列出全员（含主理人 role: "lead"/"member"），每人独立头像
- 主理人系统提示词铁律：TeamCreate 只能主理人执行；成员产出必须由成员输出，主理人只编排；跨成员信息流经主理人中转；禁止代写、禁止跳阶段、禁止 spawn 自己
- 官方模板：design-experts.zip、trading-team.zip（文档页有 COS 下载链接）

### 2.4 连接器

两种方案二选一（不可混用）：**MCP + Skill**（推荐，远程用 HTTPS SSE/streamableHttp）或 **CLI + Skill**（已有成熟 CLI）。

MCP 要求：遵循 MCP 稳定协议、HTTPS、单次请求 30s 内、可用性 ≥99.9%、最小权限、一个连接器一个 Server、错误信息可读。auth_mode：省略（自带 OAuth/无认证）/ server-side / gateway（需与团队确认）/ token（用户自填 Token，4.23.0+，配 token-schema.json 表单）。

CLI 要求：auth 10s 内输出完整 https:// 认证 URL（前后空白分隔，不带引号）、status 幂等无副作用、unAuth 清理凭证、登录态跨重启有效、不依赖用户预装 Node/Python（声明 runtime）。回调接收推荐 Device Code Flow (RFC 8628)。

提交前 12 条检查清单见官方文档；审核通过后更新通常 10–15 分钟内同步生效。icon 64×64 透明底 SVG。

### 2.5 Buddy 应用（垂直行业 AI Harness）

定位："伙伴不造产品，造配置"。六大自定义维度：工作模式（System Prompt + 绑定 Skill）、场景胶囊（快捷任务模板）、模型配置（平台模型池 HY/GLM 等选配排序）、垂直行业市场（精选 Skill/专家/连接器/灵感案例）、内嵌已有功能（MCP Apps）。

流程：创建应用（拿 Client ID/Secret，Secret 仅展示一次）→ 创建审核通过成草稿 → 分模块配置（可跳步、可导出 JSON 本地预览）→ 预览调试 → 配置审核 → 上线；改配置需重提审。

企业单管理（B2B）：授权给购买企业版 WorkBuddy 的企业，全员制/席位制，时长 3 个月/半年/1 年；授权链接长期有效但一次性使用；同一应用对同一企业暂只能发一次企业单。分发范围需勾选"发布到企业"。

### 2.6 第三方应用接入

- 硬件接入：全部 Scope（本地助理对话、云端任务、产物管理、兑换码核销）
- 积分兑换：user.credit.exchange 等部分 Scope，可给用户充积分
- 分享接入：PC 端 deeplink（WorkBuddy ≥5.8.0），RSA-2048 服务端签名，审核 7 个工作日；Windows 需 OV/EV 代码签名证书，macOS 需 Team ID
- Open API：OAuth 2.1 授权码 + PKCE，access_token 24h，refresh_token 60 天

## 3. 收入变现（内测中）

**当前仅支持付费的技能和专家**（连接器、Buddy 应用 C 端付费未开）。两种模式：

| 模式 | 规则 | 适用 |
| --- | --- | --- |
| 一次性付费（买断） | 固定价格，买断永久使用权 | 功能稳定、一次交付长期用 |
| 按月付费（订阅） | 按月价格，到期需续费 | 持续更新维护的资产 |

开通流程：「收入变现」入口 → 填资料（个人：姓名/证件/手机/收款信息；企业：企业名称/信用代码/执照/法人/对公收款信息）→ 资料审核 → **跳转微信签约**（24h 内出结果）→ 开通。

收入管理：收入结构 + 账单明细；收款账户可查改；提现跳转微信完成。

关键规则：
- **免费不能转付费**：发布时一次定死，付费版需单独发布（规划定价要提前）
- 付费资产加密防护 + 云端运行，购买者也无法轻易复制/蒸馏；发现盗版反馈平台维权
- 付费方式发布后暂不支持修改
- 审核卡住按提示改了重提，微信侧最迟 24h

## 4. 审核标准自检清单

发布前逐条过：

- [ ] 目录结构与官方完全一致（SKILL.md / plugin.json / connector-meta.json）
- [ ] 必填字段全填，中英双语都写（zh/en），语义化版本号递增
- [ ] displayDescription 中文 40–50 字；tags×3；quickPrompts×3 且第一条 = defaultInitPrompt
- [ ] categoryId 选对；专家团主理人文件名带团队前缀
- [ ] 头像：512×512、≤500KB（专家）/≤5000KB（开发者）、统一插画风格、无违规内容
- [ ] 无硬编码 Token/密钥/真实凭证；${VAR} 占位符与表单 key 一一对应
- [ ] 无夸大宣传词（保证/第一/独家/认证）；名称无 test/demo/官方仿冒
- [ ] 连接器：单 MCP Server、HTTPS、超时/错误处理、OAuth PKCE 或 token-schema 正确
- [ ] 本地/预览环境完整跑通；配置导出 JSON 备份
- [ ] 免费 or 付费一次定死，定价想清楚再发

驳回处理：页面提示原因 → 修改 → 重新提交；解析失败 → 邮件 openworkbuddy@tencent.com 或官方社群。

## 5. 服务类目（涉及"应用"类产品时）

纯技能/专家/连接器上架不涉及服务类目；做第三方应用/Buddy 应用等业务时需按主体选类目。

- **个人主体类目极少**：教育仅"教育信息展示"（明确禁止卖课、教育视频/直播）→ 别用个人主体做教育业务
- **企业主体（含个体工商户）教育类目**：
  - 课程销售：ICP 备案核准/许可证 + 执照含"教育咨询服务" + 盖章的纠纷处理机制
  - 在线视频课程：办学许可证等 5 选 1（门槛高）
  - 成人技能培训：办学许可证 / 人社部门培训备案 / 事业单位证书（3 选 1）
  - 结论：**在平台上"卖 skill"远比"卖网课"轻**——卖课资质门槛高，卖技能资产无类目要求，这是产品路线的决策依据
- 法规依据及示例文档给出每类资质对应的政策条文，可作资质办理参考

## 6. 运营数据指标

| 指标 | 口径 |
| --- | --- |
| 安装量 | 召唤专家/技能、成功连接连接器计 1 次，不去重 |
| 调用量 | 技能/专家：读取 skill.md/agent.md 计 1 次；连接器：使用工具计 1 次 |
| 留存率 | T 日与 T+7 日都产生调用的用户数 / T 日调用用户数 |

T+1 更新。专家错误率高 → 本地试用复现失败重试，定位后优化。**免费资产的留存/调用量 = 付费版需求验证数据。**

## 7. 联系渠道

- 邮箱：openworkbuddy@tencent.com（解析失败、标识申诉等均走邮件）
- 官方社群：开放平台首页下方二维码
- 企业版管理后台：www.workbuddy.cn/admin
