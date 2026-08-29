---
type: Concept
title: Agent 人格文件格式与 frontmatter
description: agency-agents 中 Agent Markdown 文件的 YAML frontmatter 必需/可选字段、九段正文结构、Persona/Operations 语义分组与 lint 规则
tags: [agent-skills, agency-agents, persona, frontmatter, markdown, lint]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: agency-agents-source
    resource: "/references/agency-agents-source.md"
    title: agency-agents 源码
  - id: facts-agency-agents
    resource: "/references/facts-agency-agents.md"
    title: agency-agents 事实清单
---

# Agent 人格文件格式与 frontmatter

agency-agents 中的每个 AI 代理人格是一个 Markdown 文件，以 YAML frontmatter 声明元数据，以结构化正文定义人格和行为规范。`scripts/lint-agents.sh` 在 CI 中强制校验格式，确保 200+ 人格文件的一致性。

## Frontmatter 字段

### 必需字段（ERROR 级别）

lint 脚本要求 frontmatter 必须包含以下三个字段，缺失将导致 ERROR：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 代理显示名称，如 "Software Architect"、"Growth Hacker"。`agent_slug()` 从此字段派生 kebab-case slug |
| `description` | string | 代理的一句话能力描述 |
| `color` | string | 代理个人品牌色（hex 格式），如 "#3B82F6" |

### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `emoji` | string | 代理的 emoji 图标 |
| `vibe` | string | 代理的气质/格言，一句话表达工作哲学 |
| `tools` | array | 代理推荐使用的工具列表 |
| `services` | array | 关联服务，每项含 name/url/tier |

### 字段示例

Software Architect 的 vibe 字段：

```yaml
vibe: "Designs systems that survive the team that built them. Every decision has a trade-off — name it."
```

Growth Hacker 声明了 tools 字段：

```yaml
tools:
  - WebFetch
  - WebSearch
  - Read
  - Write
  - Edit
```

## 正文结构（九段）

CONTRIBUTING.md 定义了推荐的九个章节，lint 脚本对关键章节的缺失发出 WARN：

### Persona 组（身份层）

定义"代理是谁"——个性、风格、规则。

| 章节 | 内容 |
|------|------|
| **Identity & Memory** | 代理的核心身份、专业背景、记忆特征 |
| **Communication Style** | 沟通风格、语气、语言偏好、回复格式 |
| **Critical Rules** | 不可违反的关键规则（WARN 级别推荐章节） |

### Operations 组（操作层）

定义"代理做什么"——使命、交付物、工作流。

| 章节 | 内容 |
|------|------|
| **Core Mission** | 核心使命和存在目的 |
| **Technical Deliverables** | 可交付成果清单 |
| **Workflow Process** | 工作流程和步骤序列 |
| **Success Metrics** | 成功衡量标准 |
| **Learning & Memory** | 学习机制和记忆管理 |
| **Advanced Capabilities** | 高级能力和边界 |

### lint 规则

`scripts/lint-agents.sh` 的检查规则：

- **ERROR**：frontmatter 缺失或不包含 name/description/color
- **WARN**：缺少推荐章节（Identity、Core Mission、Critical Rules 等）
- `classify_header_target()` 将章节头部分类为 `soul`（身份/学习记忆/沟通/风格/关键规则）或 `agents`（操作类章节），用于语义验证

## Persona 与 Operations 的语义分离

文件正文在语义上分为两组，这种分离影响人格的渲染和使用方式：

**Persona（灵魂层）**：身份标识、沟通风格、关键规则。这些属性定义代理"是谁"，在所有任务中保持一致。Persona 属性适合注入到系统提示词的身份部分。

**Operations（操作层）**：使命、技术交付物、工作流程、成功指标、高级能力。这些属性定义代理"做什么"和"怎么做"，可能根据任务上下文选择性加载。Operations 属性适合注入到任务指令部分。

这种分离使得在多工具转换时，可以灵活决定哪些部分写入哪个配置区域。

## 文件命名与 Slug 派生

- **文件名**：`{division}/{division}-{role}.md`，如 `engineering/engineering-software-architect.md`、`marketing/marketing-growth-hacker.md`
- **Slug 派生**：`agent_slug()` 函数从 frontmatter 的 `name` 字段（而非文件名）派生 kebab-case slug。这是 convert 和 install 一致的唯一真相来源。
- **Slug 用途**：作为安装目标文件名（如 `.claude/agents/software-architect.md`）和跨工具引用标识。

使用 name 而非文件名派生 slug 的好处是：文件重组不影响已安装代理的标识，name 是代理身份的稳定锚点。

## 特殊代理示例

### Agents Orchestrator

位于 `specialized/agents-orchestrator.md`，负责协调多代理开发流水线。关键属性：

- 协调多代理开发流水线
- 最大重试次数为 3 次后升级
- 是 NEXUS 策略的核心执行节点

### Software Architect

位于 `engineering/engineering-software-architect.md`：

- vibe 字段表达系统设计的权衡哲学
- 是 engineering 部门最资深的人格之一

## 与 SKILL.md 的对比

agency-agents 的人格文件格式与 SKILL.md 标准既有联系又有区别：

| 维度 | Agent 人格文件 | SKILL.md |
|------|---------------|----------|
| 核心目的 | 定义"谁在做"（身份+个性） | 定义"怎么做"（知识+流程） |
| 必需字段 | name/description/color | name/description |
| 正文结构 | 九段（Persona+Operations） | 自由结构（工作流/工具清单/参考表） |
| 工具声明 | tools（推荐工具） | allowed-tools（权限控制） |
| 颜色 | 必需（品牌色） | 无此字段 |
| 适用场景 | 角色模拟、专业人格 | 能力封装、知识复用 |

两者都使用 YAML frontmatter + Markdown 正文的基本格式，都强调 description 作为激活判据，但 Agent 文件更侧重人格特质，SKILL.md 更侧重操作知识。

## 编写最佳实践

1. **name 使用 Title Case**：如 "Frontend Developer" 而非 "frontend-developer"，slug 会自动转换。
2. **description 一句话概括**：说明专业领域和核心价值。
3. **vibe 体现差异化**：用一句话表达该代理的工作哲学，是人格间区分的关键。
4. **Critical Rules 要可执行**：避免模糊规则，写清"做什么"和"不做什么"。
5. **Technical Deliverables 要具体**：列出可验证的产出物，而非抽象描述。
6. **Workflow Process 有序**：用编号步骤定义工作流程，便于 AI 遵循。

## 相关概念

- [agency-agents 部门化人格体系](/concepts/02-agency-agents-division.md)
- [SKILL.md 标准与渐进式披露](/concepts/01-skill-md-standard.md)
- [多工具兼容与集成模式](/concepts/11-integration-patterns.md)
