# 发布审核自检清单

> 来源：整理自官方文档各资产规范页（skill/expert/expert-team/connector/buddy-app/monetization/developer-profile）｜同步日期：2026-10-24

## ⚡ 解析器实测规则（2026-10-24 发布实测，比官方文档严格）

- zip ≤3MB；**仅支持两级目录**（根目录/二级目录/文件）——`.github` 等三层嵌套直接报"目录层级超限"
- frontmatter **必含 `display_name`（中文）与 `display_name_en`（英文）**
- frontmatter 值含"英文冒号+空格"必须整体加引号，否则 YAML 解析失败（报 mapping values are not allowed）
- 上传解析通过即生成技能 ID（os_xxx）；审核中可撤回回草稿；向导中途离开自动存草稿（zip/分类回填）
- 头像需走过"继续"才落库；发布表单的"试试这样问我"来自 frontmatter examples_zh

提交审核前逐项自检，可显著降低驳回率。

## 通用项（所有资产）

- [ ] 目录结构与官方规范完全一致（SKILL.md / .codebuddy-plugin/plugin.json / connector-meta.json 位置正确）
- [ ] 必填字段全部填写；中英双语字段（{en,zh}）两种语言都写
- [ ] 版本号语义化且相对上一版递增
- [ ] 无任何硬编码 Token/密钥/真实凭证（${VAR} 占位符与表单 key 一一对应、区分大小写）
- [ ] 文案无"保证/第一/独家/认证/VIP/官方"等违规词；名称无 test/demo/试用字样；不仿冒腾讯系品牌
- [ ] 本地/预览环境完整跑通全部核心流程
- [ ] 免费 or 付费已想清楚（**免费发布后不能转付费**）；定价已确定
- [ ] 开发者资料（昵称/头像/简介/联系方式）已按规范填好

## 技能 Skill

- [ ] SKILL.md frontmatter：description / description_zh / description_en / version / author 齐备
- [ ] description 写清用途与触发词（利于自动触发与搜索）
- [ ] references/scripts/templates 目录用途正确，SKILL.md 内正确引用

## 专家 / 专家团

- [ ] displayDescription **中文 40–50 字**
- [ ] tags **恰好 3 个**；quickPrompts **恰好 3 个**且第一条 = defaultInitPrompt
- [ ] categoryId 选对（13-TencentZone 腾讯内部专用）
- [ ] 头像 512×512、≤500KB、统一漫画/插画风格
- [ ] 未自行添加 tools（系统统一分配）
- [ ] 专家团：主理人文件名带团队前缀；teamInfo/members 完整；profession 与 displayName 一致；主理人提示词含协作铁律（不代写、不跳阶段、信息经主理人中转）

## 连接器

- [ ] source kebab-case 全局唯一；MCP 仅 1 个 Server；远程 HTTPS
- [ ] 中英文名称/描述/示例（各 2–5 条）完整
- [ ] 使用新字段时 minWorkbuddyVersion 声明正确
- [ ] OAuth 端点齐备（发现/动态注册/PKCE）或 token-schema 正确
- [ ] 覆盖超时、授权失效、参数错误等异常处理

## Buddy 应用

- [ ] 两轮审核：创建审核 → 草稿 → 配置审核
- [ ] 每次退出配置前导出配置 JSON 备份
- [ ] 提交前用预览链接在对应版本客户端真机验证
- [ ] icon 与背景图符合设计规范（16px 线宽 1.2 断口；1000×910 日夜两套）

## 🚫 强制下架红线（发布后巡查，2026-10-26 实锤）

依据《开发者公约》第 2.8.3 条「服务安全与接口使用」，以下类型即使过审也会被**强制下架**：

- ❌ 以自动化方式替代用户真实操作，**获取平台活动权益**（自动签到领积分、自动领取活动奖励、刷权益类功能）
- ❌ 绕过平台接口或活动规则获取权益的功能设计

**实例**：WorkBuddy 签到助手 v3.3.0（os_cbec45dcae805e36）过审并发布后，2026-10-26 被强制下架，官方理由即上述条款。下架卡片提供「下架原因」与「联系运营」入口。

**关键教训**：**审核通过 ≠ 长久安全**——平台有发布后巡查。体检时对"自动签到/自动领取/批量获取权益"类功能要直接预判强制下架，建议改为提醒用户手动领取等不触碰权益发放秩序的设计。

## 驳回后处理

按页面提示原因修改 → 重新提交（应用 ID 不变）。zip 解析失败：对照结构自查 → 仍失败邮件 openworkbuddy@tencent.com 或官方社群。审核期间的资产状态：审核中/已启用/已驳回。
