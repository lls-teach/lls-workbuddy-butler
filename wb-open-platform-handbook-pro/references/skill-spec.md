# 技能（Skill）开发规范

> 来源：官方文档 /docs/skill ｜ 同步日期：2026-10-24

## 目录结构

```
{skill-name}/
├── SKILL.md          # ★ 必须，YAML frontmatter + Markdown 指令正文
├── references/       # 可选，补充知识文档，AI 执行时作为上下文读取
├── scripts/          # 可选，可执行脚本，AI 通过 Bash 调用
└── templates/        # 可选，可复用模板文件
```

- references 在 SKILL.md 中用 `@references/xxx.md` 引用；适合 API 规范、领域知识、示例数据。
- scripts 存放 JS/Python 等，AI 用 Bash 执行；适合调外部 API、数据处理、批量操作。
- templates 存放标准化流程模板。

## SKILL.md frontmatter 字段

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| name | 否 | 技能标识（kebab-case） |
| description | ✅ | 写清用途和**触发词**（影响 AI 自动触发） |
| description_zh | ✅ | 简短中文介绍 |
| description_en | ✅ | 简短英文介绍 |
| version | ✅ | 版本号，语义化递增 |
| author | ✅ | 合作方/作者名称 |
| allowed-tools | 否 | 工具白名单（逗号分隔） |
| disable-model-invocation | 否 | true 则 AI 不自动触发，仅用户手动调用 |
| user-invocable | 否 | false 则隐藏菜单，仅供 AI 内部使用 |

正文写执行指令：当用户需要做 XX 时按步骤执行（步骤化、可操作）。

## 创建与上传

- 客户端：市场右上角【添加技能 → 创建技能】，对话式补全提示词创建。
- 开放平台：提交 zip 包。zip 解析失败 → 对照上述结构自查（常见：缺 SKILL.md、frontmatter 字段缺失、目录名不符），仍失败发邮件 openworkbuddy@tencent.com 或进官方社群。

## 编写建议

- description 是触发入口：写清"什么场景+解决什么"，附触发词；
- 大块知识放 references 渐进加载，SKILL.md 保持精简路由式写法；
- 需要确定性逻辑用 scripts，别让 AI 现场推理可计算的步骤。
