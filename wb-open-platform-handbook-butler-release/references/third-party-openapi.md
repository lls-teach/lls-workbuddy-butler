# 第三方应用与 Open API

> 来源：官方文档 /docs/third-party-app、/docs/openapi ｜ 同步日期：2026-10-24

## 应用类型

| 类型 | 说明 | 权限 |
| --- | --- | --- |
| 硬件接入 | 硬件设备厂商（智能眼镜、车机等）接入本地助理/云端任务/产物能力 | 全部 Scope 按需申请 |
| 积分兑换 | 通过卡券/兑换码为用户兑换 WorkBuddy 积分（credits） | 仅积分权益类 Scope |
| 分享接入 | 让用户从你的应用一键分享内容到 WorkBuddy（需企业认证） | — |

## OAuth 2.1 授权流程

授权页 `GET https://www.workbuddy.cn/openapi/v2/authorize?response_type=code&client_id=...&redirect_uri=...&scope=...&state=...` → 回调拿 code（10 分钟有效、一次性）→ `POST /openapi/v2/token` 换 access_token（24h）+ refresh_token（60 天）→ 调业务 API。redirect_uri 必须与注册配置完全一致（字节级）；client_secret 严禁暴露在前端。

## Scope 权限列表

user.profile.readable 读取昵称头像｜user.contact.readable 校验手机号一致｜user.credit.exchange 卡券兑换积分｜user.task.invokable 创建执行云端任务｜user.task.readable 读任务列表详情｜user.localassistant.invokable 向 PC 本地助理发消息｜user.localassistant.readable 读本地助理状态与历史。最小权限原则：只申请所需 Scope。

## API 能力域

认证授权、个人资料、本地助理（PC 端消息交互）、云端任务（创建/查询/ACP 连接）、ACP 实时双向通道、会话产物（计划/任务/媒体/总结）、兑换码核销。

## 分享接入要点

- 面向已企业认证开发者；PC 端（Windows/macOS）deeplink 方式，WorkBuddy ≥5.8.0；移动端后续开放。
- 注册：基础配置（名称全平台唯一、logo ≥96×96px ≤100KB、简介、**可访问官网**含协议版权备案）+ 平台信息（Windows 需 exe 代码签名主体+证书指纹；macOS 需 Bundle ID+Team ID）→ 审核 7 个工作日内，结果三渠道通知。
- 密钥：审核通过后在详情页本地生成 RSA-2048 密钥对（私钥仅展示一次，存服务端；最多 10 对按 kid 轮换）。
- 签名：RS256，message 为 UTF-8 JSON 的 Base64（≤16384 字节），待签名串按 appId→kid→message→nonce→timestamp 顺序拼接；timestamp 秒级，时效 -30~300s；同 appId+nonce 最多验签 3 次。
- 品牌规范：必须展示 WorkBuddy 标识（按品牌中心素材原样使用），统一驼峰写作 WorkBuddy；不得用于自己应用图标/广告；视觉显著性不得高于自己品牌；不得自称"官方/授权/合作伙伴"。
