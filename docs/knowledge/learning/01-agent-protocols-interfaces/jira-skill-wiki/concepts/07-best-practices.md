---
type: Concept
title: "最佳实践与反模式"
description: "Jira 集成插件最佳实践与反模式汇总，涵盖意图动词优先、dry-run 预览、无编辑化、精确流转名、resolution 字段处理与多阶段工作流 walk。"
tags: ["jira", "best-practices", "anti-patterns", "dry-run", "intent-verbs", "resolution"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T00:00:00Z" }
status: stable
stale_after: "2027-08-29T00:00:00Z"
sources:
  - resource: "/references/source-code.md"
    type: "source-code"
    trust: high
  - resource: "/references/api-reference.md"
    type: "source-code"
    trust: high
---
# 第 7 章：最佳实践与反模式

本章提炼使用 jira-skill 的工程经验，列出推荐做法与应避免的反模式。

## 7.1 用意图动词替代 get + list

**反模式**：用 `get` + `comment list` 的组合来分诊或处理工单，需要多次调用拼凑上下文。

**推荐**：使用匹配意图的动词，一次调用拿到完整上下文包：

```bash
jira-issue.py work PROJ-123     # 代替 get + 多次 comment list + attachments
jira-issue.py qa PROJ-123       # 代替手动查找转交评论
jira-issue.py qa-fail PROJ-123  # 代替 6 次调用拼凑驳回上下文
```

## 7.2 破坏性操作先 dry-run

写操作（更新、流转、创建、链接）均支持 `--dry-run`，先预览再执行：

```bash
jira-issue.py update PROJ-123 --labels "urgent,backend" --dry-run
jira-transition.py do PROJ-123 "In Progress" --dry-run
```

## 7.3 全局标志置于子命令之前

`--json`、`--quiet`、`--debug` 等全局标志位于子命令之前，而非之后：

```bash
jira-issue.py --json get PROJ-123     # 正确
jira-issue.py get PROJ-123 --json     # 错误（旧版风格）
```

## 7.4 无编辑化（No editorializing）

工单内容与评论中只陈述事实，不写"做得多好"之类自我评价。尤其是 AI 生成内容时，避免写入自夸式措辞。

## 7.5 语法校验作为独立门禁

提交 Jira 内容前，把 `validate-jira-syntax.sh` 作为**独立一步**执行，不与发帖命令串联：

```bash
# 先校验（独立步骤）
${CLAUDE_SKILL_DIR}/scripts/validate-jira-syntax.sh content.txt

# 再提交（后续步骤）
jira-comment.py add PROJ-123 "$(cat content.txt)"
```

## 7.6 流转名是精确字符串

`jira-transition.py do KEY "<name>"` 对流转名做字面匹配，包括部分实例配置的 emoji 前缀（如 `✅ Resolve`、`❌ QA failed`）。不匹配时，错误信息会列出可用名称，需按打印的原文精确复制。用 `jira-issue.py act KEY` 可提前查看。

## 7.7 终态流转补 resolution 字段

流转到终态（如 Resolved）时，Jira 存储**状态**（徽章）与**resolution**（绿色对勾）两个独立字段。若不显式传 `--resolution`，工单即使状态显示已解决，在过滤器中仍显示"未解决"。推荐：

```bash
jira-transition.py do PROJ-123 "Resolved" --resolution Done
jira-transition.py do PROJ-123 "Resolved" --resolution "Won't do"
```

若流转屏拒绝 `--resolution`（提示 `Field 'resolution' cannot be set`），按顺序处理：先查是否有其他终态流转携带该字段；无则去掉 `--resolution` 重试；最后用 JQL 验证，而非假设成功：

```bash
jira-search.py query "project = PROJ AND statusCategory = Done AND resolution is EMPTY" -f key,status
```

## 7.8 多阶段工作流用 path 一次走到底

工单深处于多阶段工作流（如 `QA → UAT Stage → Ready for deployment → Resolved → Closed`）时，手动逐段 `list` + `do` 需多次往返。用 `path` 子命令一次性走到目标：

```bash
jira-transition.py path PROJ-123 Closed --resolution Done
jira-transition.py path PROJ-123 Closed --dry-run   # 预览第一步
```

`path` 是贪心走法而非图搜索：每步优先走目标，否则走唯一的非回退流转；若某步有多个前进选项则停下列出，需人工选择。

## 7.9 依赖版本钉扎原则

插件将 `atlassian-python-api` 钉扎在 `>=3.41,<4`，**不要**随意升级到 v4——v4 在 Jira Server/DC 上到 4.0.5 前存在回归。仅在具备 Jira Cloud 测试租户后才考虑升级。

## 7.10 反模式清单

| 反模式 | 正确做法 |
|--------|---------|
| 认定"MCP 连接器无权限"即"无 Jira 访问" | 该技能直连 Jira，连接器作用域与 Jira 可达性无关；不确定时运行 `jira-setup.py` 检查 |
| 在工单中写自我褒扬 | 只陈述发生了什么 |
| 把语法校验与发帖命令串联 | 校验作为独立门禁步骤 |
| 用 Markdown 语法写 Jira 内容 | 使用 Jira wiki 标记（见第 5 章） |
| 终态流转不传 `--resolution` | 显式传入与结果匹配的 resolution |

## 相关概念

- [jira-communication 技能](/concepts/04-jira-communication.md)：意图动词详解
- [JQL 查询语言](/concepts/06-jql.md)：高效查询技巧
- [故障排查](/concepts/08-troubleshooting.md)：问题解决指南
- [工作流自动化示例](/examples/workflow-automation.md)：实操示例