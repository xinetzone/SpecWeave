---
type: Concept
title: SKILL.md 标准与渐进式披露
description: Agent Skills 开放标准的 SKILL.md 文件格式，frontmatter 字段规范，以及三层渐进式披露的知识组织模式
tags: [agent-skills, skill.md, standard, progressive-disclosure, frontmatter]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: awesun-skill-source
    resource: "/references/awesun-skill-source.md"
    title: awesun-skill 源码
  - id: awesun-ui-locator-source
    resource: "/references/awesun-ui-locator-source.md"
    title: awesun-ui-locator 源码
  - id: jira-skill-source
    resource: "/references/jira-skill-source.md"
    title: jira-skill 源码
  - id: retro-skill-source
    resource: "/references/retro-skill-source.md"
    title: retro-skill 源码
---

# SKILL.md 标准与渐进式披露

SKILL.md 是 Agent Skills 开放标准（agentskills.io）的核心文件。每个技能目录必须包含一个 SKILL.md，它既是 AI 理解技能能力的入口，也是人类开发者了解技能用途的文档。标准的核心设计理念是**渐进式披露**（progressive disclosure）：技能知识按 Token 消耗从低到高分为三层，AI 仅在需要时才加载更深层的内容。

## Frontmatter 字段

SKILL.md 以 YAML frontmatter 开头，不同技能根据复杂度声明不同字段。

### 必需字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 技能标识符，kebab-case 格式。如 `awesun-remote-control`、`screenshot-ui-locator`、`jira-communication`、`retro` |
| `description` | string | 技能描述，包含触发关键词和使用场景。**这是 AI 判断是否加载技能的唯一依据**，应包含功能、工具名、使用场景等关键信息 |

### 常见可选字段

| 字段 | 类型 | 说明 | 示例项目 |
|------|------|------|---------|
| `version` | string | 技能版本号 | awesun-skill（1.0） |
| `license` | string | 许可证 | jira-skill、retro-skill（MIT） |
| `compatibility` | string/array | 兼容的 AI 工具列表 | retro-skill |
| `metadata` | object | 元数据对象，含 author/version/repository | jira-skill、retro-skill |
| `allowed-tools` | array | 声明技能允许使用的工具 | jira-communication、retro |

### allowed-tools 示例

jira-communication 的 allowed-tools 声明：

```yaml
allowed-tools:
  - Bash(python:*)
  - Bash(uv:*)
  - Read
  - Write
```

retro 技能的 allowed-tools 更广泛：

```yaml
allowed-tools:
  - Bash(python3:*)
  - Bash(gh:*)
  - Bash(glab:*)
  - Bash(git:*)
  - Bash(find:*)
  - Bash(grep:*)
  - Bash(jq:*)
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Task
```

无执行需求的纯知识技能（如 jira-syntax）不声明 allowed-tools。

### description 编写要点

description 字段是技能的"广告文案"，直接影响 AI 是否在正确场景激活技能。观察各项目的实践：

- **awesun-remote-control**："提供 22 个工具。使用场景包括：控制命令、控制连接、控制断开。关键词：远程控制，设备管理，桌面控制，远程CMD，远程电源管理。"
- **jira-communication**：声明自动触发条件——Jira URL 或 issue key（PROJ-123），以及任何 Jira 意图（"create/find a ticket"）。
- **retro**：描述会话复盘和摩擦点检测能力。

好的 description 应包含：功能概述、工具/领域关键词、触发场景。

## 三层渐进式披露

```text
第一层（始终可见）
  └── SKILL.md frontmatter 的 name + description
      Token 消耗：极低（~50-100 Token）
      加载时机：技能列表扫描时

第二层（激活时加载）
  └── SKILL.md 正文：工作流程、工具清单、参数说明、意图映射
      Token 消耗：中等（~500-3000 Token）
      加载时机：AI 判断技能相关后

第三层（按需加载）
  ├── references/*.md：深度参考文档、配置指南、故障排除
  └── scripts/*：可执行脚本，AI 按需读取或调用
      Token 消耗：按实际读取量计算
      加载时机：需要具体细节或执行操作时
```

### 第一层：frontmatter

frontmatter 的 name 和 description 在 AI 启动时随技能列表一起加载，无论技能是否被使用。因此 description 必须精炼且信息密度高——它决定了技能的"激活率"。

### 第二层：SKILL.md 正文

正文的内容组织因技能类型而异，但常见结构包括：

- **工具清单**：按类别列出所有可用工具，每个工具含功能描述和参数（awesun-skill 的 Device/Control/Desktop 三类）。
- **工作流程**：定义 AI 应遵循的步骤序列（awesun-ui-locator 的 5 步工作流）。
- **意图映射**：将用户意图映射到具体脚本（jira-communication 的 triage→jira-issue.py work）。
- **语法参考**：快速查表（jira-syntax 的 Jira vs Markdown 对照表）。
- **模式定义**：多种运行模式的触发方式和适用场景（retro 的六种模式）。
- **References 表**：列出 references/ 子目录中的文档及其用途，引导 AI 按需深入。

### 第三层：references/ 和 scripts/

**references/** 存放不需要每次都加载的深度知识：

- jira-communication 引用了 16 篇参考文档：JQL 食谱、配置指南、故障排除、问题编辑、创建、评论、工作日志、附件、链接、敏捷、无编辑化、字段用户、观察者、版本、QA 收集、意图动词。
- retro 引用了 9 篇：摩擦目录、目标分类法、分类启发式、技能发现、补丁工作流、评估集成、提升模式、工作流、项目工具检查。
- awesun-ui-locator 引用了 ui_patterns.md，包含按钮/输入框/图标的视觉特征对照表。

**scripts/** 存放可执行脚本，SKILL.md 只描述何时调用、如何传参，不重复脚本内部实现。AI 需要理解脚本行为时才读取脚本源码，需要执行时直接调用。

## 渐进式披露的工程价值

对比 MCP 全量 Schema 注入（25 工具消耗 8,000-12,000 Token/会话），渐进式披露的优势在于：

1. **Token 效率**：安装 100 个技能的 frontmatter 消耗可能还不如一个 MCP 服务器的全量 Schema。
2. **信噪比**：AI 仅加载与当前任务相关的知识，不会被无关工具的 Schema 干扰。
3. **可维护性**：references/ 和 scripts/ 的更新不影响 frontmatter 契约，技能向后兼容性更好。
4. **可组合性**：多个技能可共存，AI 根据 description 自主选择和组合。

## 技能类型谱系

六个项目展示了 Skill 的类型光谱：

| 类型 | 特征 | 示例 |
|------|------|------|
| 纯知识型 | 无 allowed-tools，仅提供参考信息 | jira-syntax |
| 知识+计算型 | 有脚本但仅做本地计算，无外部 API | awesun-ui-locator |
| MCP 桥接型 | 通过执行器连接 MCP 服务器 | awesun-skill |
| API 脚本型 | 直接通过脚本调用外部 API | jira-communication |
| 自省分析型 | 分析会话记录，检测模式，生成提案 | retro |

## 相关概念

- [AI Agent Skills 生态概览](/concepts/00-overview.md)
- [插件架构（plugin.json/hooks/commands）](/concepts/05-plugin-architecture.md)
- [Skill 脚本工具模式](/concepts/10-skill-tooling-scripts.md)
- [SKILL.md 编写示例](/examples/skill-authoring.md)
