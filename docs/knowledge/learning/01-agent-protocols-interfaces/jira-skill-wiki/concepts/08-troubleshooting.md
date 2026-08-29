---
type: Concept
title: "故障排查"
description: "Jira 集成插件故障排查指南，涵盖 uv 未安装、环境文件缺失、认证失败、导入错误、resolution 字段无法设置等常见问题与解决步骤。"
tags: ["jira", "troubleshooting", "authentication", "errors", "resolution", "import"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T00:00:00Z" }
status: stable
stale_after: "2027-08-29T00:00:00Z"
sources:
  - resource: "/references/source-code.md"
    type: "source-code"
    trust: high
  - resource: "/references/official-docs.md"
    type: "official-docs"
    trust: high
---
# 第 8 章：故障排查

本章汇总使用 jira-skill 时的常见问题与解决步骤。

## 8.1 "uv not found"

**原因**：未安装 `uv`。

**解决**：

```bash
pip install uv
```

## 8.2 "Environment file not found"

**原因**：缺少凭证配置文件。

**解决**：创建 `~/.env.jira` 并填入凭证（参见第 2 章）。

## 8.3 "Authentication failed"（认证失败）

**排查步骤**：

1. 确认 `JIRA_URL` 正确。
2. Cloud 场景：`JIRA_USERNAME` 是邮箱。
3. Server/DC 场景：使用 `JIRA_PERSONAL_TOKEN` 而非 API Token。
4. API Token 过期则重新生成。

## 8.4 运行脚本时报导入错误

**原因**：脚本在错误的目录下运行，导致共享库 `lib/` 未被正确解析。

**解决**：从技能目录运行：

```bash
cd skills/jira-communication
uv run scripts/core/jira-issue.py get PROJ-123
```

## 8.5 "Field 'resolution' cannot be set"

**原因**：当前流转屏（或编辑屏）未配置 `resolution` 字段，却显式传入了 `--resolution`。

**解决**（按顺序处理）：

1. 用 `jira-transition.py list KEY` 查看是否有其他终态流转的屏包含 `resolution`，优先选用。
2. 无则去掉 `--resolution` 重试，让工单以空 resolution 落库（部分工作流由 post-function 在后续步骤补填）。
3. 工作流到达真正终态后，用 JQL 验证而非假设：

```bash
jira-search.py query "key = PROJ-123 AND resolution is EMPTY"
jira-search.py query "project = PROJ AND statusCategory = Done AND resolution is EMPTY" -f key,status
```

命中即说明 resolution 确实缺失，应向用户如实说明，而非把第 2 步当作成功。

## 8.6 技能未激活

**排查步骤**：

1. 验证安装：`/plugin list` 应显示 `jira-integration`。
2. 检查两个技能目录存在：`ls skills/jira-communication/` 与 `ls skills/jira-syntax/`。
3. 必要时重装：`/plugin uninstall jira-integration` 后 `/plugin install jira-integration`。

## 8.7 JQL 查询无结果

**排查步骤**：

1. 确认字段名拼写与实例一致（自定义字段名可能不同）。
2. 含空格的字符串值需加引号（`project = "My Project"`）。
3. 参考第 6 章的引号规则与操作符用法。

## 8.8 认证通道自查

若 MCP 连接器看似无权访问，不要据此断定"无 Jira 访问"——该连接器与脚本是两套独立系统。运行 `jira-setup.py` 检查配置，并向用户**立即、明确**说明状态，而非将问题埋进选项里。

## 相关概念

- [安装与配置](/concepts/02-installation.md)：环境文件与凭证设置
- [jira-communication 技能](/concepts/04-jira-communication.md)：脚本运行方式与目录结构
- [JQL 查询语言](/concepts/06-jql.md)：查询语法与字段引用
- [最佳实践与反模式](/concepts/07-best-practices.md)：resolution 字段处理与 dry-run 规范