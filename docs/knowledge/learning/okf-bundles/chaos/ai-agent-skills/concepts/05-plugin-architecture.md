---
type: Concept
title: 插件架构（plugin.json/hooks/commands）
description: Agent Plugin 规范的 plugin.json 元数据、commands 斜杠命令、hooks 生命周期钩子、checkpoints 质量门控与双技能打包模式
tags: [agent-skills, plugin, plugin.json, hooks, commands, checkpoints, jira, retro]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: jira-skill-source
    resource: "/references/jira-skill-source.md"
    title: jira-skill 源码
  - id: retro-skill-source
    resource: "/references/retro-skill-source.md"
    title: retro-skill 源码
---

# 插件架构（plugin.json/hooks/commands）

Agent Plugin 规范（agent-plugins.org/schemas/1.0.0）在单个 Skill 之上定义了插件层：一个插件可以包含多个技能、斜杠命令、生命周期钩子和质量门控。jira-skill 和 retro-skill 是两个典型的插件实现，分别展示了"双技能打包"和"自省工作流"两种插件架构模式。

## plugin.json 元数据

plugin.json 是插件的清单文件，遵循 `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`。

### jira-skill 的 plugin.json

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "jira",
  "version": "3.28.0",
  "description": "Comprehensive Jira integration with auto-detection of issue keys",
  "author": {
    "name": "Netresearch DTT GmbH",
    "url": "https://www.netresearch.de/"
  },
  "repository": "https://github.com/netresearch/jira-skill",
  "license": "(MIT AND CC-BY-SA-4.0)",
  "keywords": ["jira", "atlassian", "issue-tracking", "project-management",
               "wiki-markup", "syntax-validation", "templates"]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `$schema` | string | Plugin Schema 的 JSON Schema URI |
| `name` | string | 插件标识符（kebab-case） |
| `version` | string | 语义化版本号 |
| `description` | string | 插件描述 |
| `author` | object | 含 name 和 url |
| `repository` | string | 源码仓库 URL |
| `license` | string | SPDX 许可证表达式（支持双许可证） |
| `keywords` | array | 关键词数组，用于插件发现 |

### 版本一致性

jira-skill 的 AGENTS.md 规定：plugin.json 和两个 skills/*/SKILL.md 的 `metadata.version` 必须三者匹配，由 pre-commit 和 CI 强制执行。这确保了插件版本与技能版本的一致性——用户不会安装到版本不匹配的组合。

## 插件目录结构

### jira-skill（双技能插件）

```text
jira-skill/
├── plugin.json                          # 插件清单
├── .claude-plugin/
│   └── plugin.json                      # Claude Code 专用插件配置
├── skills/
│   ├── jira-communication/              # 技能一：API 操作
│   │   ├── SKILL.md
│   │   ├── AGENTS.md
│   │   ├── scripts/{core,workflow,utility,lib}/
│   │   ├── references/                  # 16 篇参考文档
│   │   └── evals/
│   └── jira-syntax/                     # 技能二：语法参考
│       ├── SKILL.md
│       ├── AGENTS.md
│       ├── scripts/validate-jira-syntax.sh
│       ├── templates/                   # Bug/Feature 模板
│       └── references/
├── commands/                            # （如有）斜杠命令
├── hooks/                               # 生命周期钩子
│   └── hooks.json
├── scripts/                             # 插件级脚本
│   ├── detect_jira_issues.py
│   └── verify-harness.sh
└── tests/                               # pytest 测试
```

### retro-skill（单技能+命令+钩子插件）

```text
retro-skill/
├── plugin.json
├── commands/
│   └── retro.md                         # /retro 斜杠命令
├── hooks/
│   └── session-end.json                 # SessionEnd 钩子
└── skills/retro/
    ├── SKILL.md
    ├── checkpoints.yaml                 # 质量门控
    ├── references/                      # 9 篇参考文档
    ├── scripts/                         # 8 个脚本
    └── evals/                           # 15 个评估场景
```

## Commands（斜杠命令）

commands/ 目录定义用户可通过斜杠调用的命令。retro-skill 的 `commands/retro.md` 是典型范例。

### retro 命令

frontmatter 仅包含 `description` 字段：

```yaml
---
description: Session retro — detect friction and route learnings
---
```

正文定义了 **10 个阶段**的详细执行流程：

| 阶段 | 名称 | 说明 |
|------|------|------|
| 1 | 机械预检 | 运行 detect-mechanical.py 获取确定性信号 |
| 2 | LLM 增强 | 添加推断信号，过滤误报 |
| 2b | 跨会话增强 | （可选）运行 scan-cross-session.py |
| 3 | 分类 | 按三轴启发式路由到七个目标 |
| 4 | 技能发现 | 发现已安装和可用技能（必须在分类前运行） |
| 5 | 评估咨询 | 评估验证器集成 |
| 6 | 提案生成 | 生成具体改进提案 |
| 7 | 审批 | 逐提案人工审批（"No silent writes"） |
| 8 | 物化 | 将批准的提案写入目标位置 |
| 9 | 报告 | 输出复盘报告 |

### 模式变体

命令正文还定义了不同模式的流程变体：

- **Outcome 模式**：检测 Schicht D 信号 D1-D12（失败、持久成功、取代的临时副本）
- **Promote 模式**：替换阶段 1 为 scan-memory-inventory.py，跳过阶段 2/2b/3/3b/3c，阶段 9 增加"物化后排空"步骤
- **Auto 模式**：通过 SessionEnd 钩子触发，默认仅打印提醒

### 安全设计

- 阶段 7 拒绝的技能更新编辑记录到 `~/.claude/retro/rejected-edits.md` 以避免重复提议
- 阶段 7 的技能更新提案必须包含 Skill instruction delta（当前指令、建议编辑、边界说明）
- 补丁始终指向源仓库，绝不指向 `~/.claude/plugins/cache/`

## Hooks（生命周期钩子）

hooks/ 目录定义 AI 客户端生命周期事件的自动触发逻辑。

### retro-skill 的 SessionEnd 钩子

`hooks/session-end.json` 是可选的自动触发钩子：
- 默认关闭
- 仅对超过 1000 字的会话打印提醒
- 提醒用户可以运行 `/retro` 进行复盘
- 不自动执行复盘（遵守"No silent writes"原则）

### jira-skill 的钩子

jira-skill 有 `hooks/hooks.json` 和插件级脚本 `scripts/detect_jira_issues.py`，用于在会话中自动检测 Jira issue key（如 PROJ-123）并触发相应技能。

## Checkpoints（质量门控）

retro-skill 的 `skills/retro/checkpoints.yaml` 定义了技能安装和更新时的自动化质量检查。

| 检查点 | 验证内容 |
|--------|---------|
| 前置条件 | `python3 --version` 可用 |
| RT-01~RT-05 | SKILL.md、commands/retro.md、detect-mechanical.py 存在且 Python 语法有效 |
| RT-07 | 单元测试套件通过（`python3 -m unittest discover -s tests -q`） |
| RT-10~RT-11 | 核心参考文档和工作流参考文档存在 |
| RT-40~RT-42 | 评估验证器脚本存在、语法有效、评估场景 ≥5 个且格式良好 |

checkpoints.yaml 的版本为 1，skill_id 为 retro。这些检查在技能安装或更新时自动运行，确保交付物的完整性。

## 双许可证模式

两个项目都采用了**代码 MIT + 内容 CC-BY-SA-4.0** 的双许可证模式：

- **MIT**：适用于代码文件（Python 脚本、Shell 脚本、JSON 配置）
- **CC-BY-SA-4.0**：适用于内容文件（SKILL.md 正文、参考文档、模板）

这种设计使得代码可以自由集成到商业产品中，而文档内容保持开源且要求衍生作品同样开源。plugin.json 中使用 SPDX 表达式 `(MIT AND CC-BY-SA-4.0)` 表达双许可证。

## 插件级脚本与技能级脚本

jira-skill 区分了两种脚本层级：

| 层级 | 位置 | 用途 | 示例 |
|------|------|------|------|
| 插件级 | `scripts/` | 跨技能的共享逻辑 | detect_jira_issues.py（issue key 检测） |
| 技能级 | `skills/*/scripts/` | 技能专属逻辑 | jira-issue.py、validate-jira-syntax.sh |

技能级脚本通过 PYTHONPATH 导入共享 lib/ 库，但不反向依赖插件级脚本。这种分层确保了技能的可独立分发性（jira-skill 发布时同时提供完整版和两个独立技能版）。

## 发布工程化

jira-skill 的 AGENTS.md 描述了高度自动化的发布流程：

- 标签推送时自动发布三个包族：完整版 + 两个独立技能版
- 每个发布包含 SHA256SUMS 校验和
- 包含 SLSA 证明（供应链安全）
- Pre-commit 检查：脚本帮助验证、pytest 测试、ruff check 和 format --check（两个独立门控）、markdownlint
- PR 保持小体量（~300 净 LOC）
- Conventional Commits 规范

## 相关概念

- [SKILL.md 标准与渐进式披露](/concepts/01-skill-md-standard.md)
- [Jira Skill 工程化实践](/concepts/08-jira-skill-engineering.md)
- [Retro Skill 自省与演进模式](/concepts/09-retro-skill-introspection.md)
- [AI Agent Skills 生态概览](/concepts/00-overview.md)
