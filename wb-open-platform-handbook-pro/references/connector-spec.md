# 连接器开发规范

> 来源：官方文档 /docs/connector ｜ 同步日期：2026-10-24

连接器 = WorkBuddy 的能力扩展接口，用户安装后自然语言调用第三方服务。两种方案**二选一不可混用**：MCP+Skill（推荐；远程用 HTTPS SSE/streamableHttp）或 CLI+Skill（已有成熟跨平台 CLI 时）。

## MCP 方案

结构：`connector-meta.json`（必须）+ `mcp.json`（必须，仅 1 个 Server）+ `icon.svg`（必须）+ `skills/{skill-name}/SKILL.md`（可选）。

MCP Server 要求：遵循 MCP 稳定协议；远程 HTTPS；单次请求 30s 内响应；可用性 ≥99.9%；错误信息可读；用户数据必须认证鉴权、最小权限。

mcp.json 常用字段：type（sse/streamableHttp/stdio）、url、headers/env（${VAR} 占位，不得写真实凭证）、timeout（默认 30000ms）、stdio 的 command/args/runtime（node/python）、npmRegistry。使用新字段须在 connector-meta.json 声明 minWorkbuddyVersion。

connector-meta.json：name/name_zh/name_en、description 三语（20–100 字）、source（全局唯一 kebab-case）、type（mcp/cli/skill-only）、version、examples_zh/en（各 2–5 条自然语言示例，必填 4.24.0+）、auth_mode（省略=自带OAuth或无认证 / server-side / gateway / token）。

## 鉴权四模式

| 模式 | 说明 |
| --- | --- |
| 省略 | MCP 自带 OAuth（平台内置 OAuth 管理器走 OAuth2.1+PKCE）或无需认证 |
| server-side / gateway | WorkBuddy 云端托管 OAuth，接入前与官方确认 |
| token | 用户自填 API Key/Token（4.23.0+）：token-schema.json 描述表单，${VAR} 与字段 key 一一对应区分大小写，敏感字段 type: password |
| CLI 登录 | cli.json 的 auth/status/unAuth 管理 |

OAuth 服务端须实现：元数据发现（/.well-known/oauth-protected-resource 与 oauth-authorization-server）、动态注册（RFC 7591，回显 redirect_uris）、authorize 支持 PKCE S256、token 支持 refresh_token；access_token 建议 1h、refresh_token ≥30 天；回调优先 workbuddy:// 私有协议，回退 127.0.0.1 动态端口。

## CLI 方案

cli.json：init/auth/unAuth/status 按 darwin/linux/win32 配置。硬性要求：auth 10s 内在 stdout/stderr 输出完整 https:// 认证 URL（前后空白分隔、不能带引号、不进交互等待）；status 幂等无副作用，退出码 0 且匹配 statusMatch 视为已登录；unAuth 清理凭证且未登录也正常返回；登录态跨进程重启有效；不依赖用户预装 Node/Python（声明 runtime 由平台托管，npm/pip 装在平台管理目录）。认证回调推荐 Device Code Flow（RFC 8628，5.0.0+）。

超时：init 5 分钟 / auth 10 秒 / status 10 秒 / unAuth 30 秒 / 认证轮询 5 分钟（每 3 秒）。

## 提交前检查（官方清单摘要）

接入方案选定且结构规范｜source kebab-case 唯一｜中英文名称/描述/示例完整｜MCP 单 Server 且 HTTPS（或 CLI 全平台验证）｜OAuth 端点齐备或 token-schema 与 ${VAR} 一致｜Skill 能指导 AI 调用全部核心能力｜无硬编码凭证｜icon 清晰（SVG 推荐/PNG 64×64 透明底）｜版本与 minWorkbuddyVersion 正确｜覆盖超时/授权失效/参数错误异常。

打包目录提交审核；通过后进连接器市场，更新重提审，通常 10–15 分钟内同步生效。同一服务要同时提供 OAuth 与 Token 两种方式，须用两个不同 source 分别提交。
