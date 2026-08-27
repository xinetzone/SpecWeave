---
type: Concept
title: 多工具兼容与集成模式
description: AI Agent Skill 跨 16 种 AI 工具的兼容模式，installKind 三类产物、format 字节一致性、部门化人格的批量转换、开放标准与插件规范
tags: [agent-skills, multi-tool, compatibility, integration, agency-agents, standards]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: agency-agents-source
    resource: "/references/agency-agents-source.md"
    title: agency-agents 源码
  - id: jira-skill-source
    resource: "/references/jira-skill-source.md"
    title: jira-skill 源码
  - id: retro-skill-source
    resource: "/references/retro-skill-source.md"
    title: retro-skill 源码
---

# 多工具兼容与集成模式

AI Agent 生态存在多种 AI 编程工具（Claude Code、Cursor、Codex、Gemini CLI、Copilot、Aider、Windsurf 等），每种工具有不同的配置格式、安装路径和扩展机制。本概念梳理了 Skill/插件实现跨工具兼容的三种模式：agency-agents 的格式转换引擎、Agent Skills 开放标准、Agent Plugin 规范。

## 兼容性问题的本质

不同 AI 工具的扩展机制差异体现在四个维度：

| 维度 | 差异示例 |
|------|---------|
| **配置格式** | Markdown（.claude/agents/）、TOML（.codex/agents/）、MDC（.cursor/rules/）、CONVENTIONS.md（aider） |
| **安装范围** | 用户全局（~/.tool/）、项目级（.tool/） |
| **能力模型** | 静态系统提示词、动态工具调用、斜杠命令、钩子 |
| **发现机制** | 目录约定、插件清单、MCP 配置 |

## 模式一：格式转换引擎（agency-agents）

agency-agents 面对的兼容性挑战最大：200+ 人格文件需要安装到 16 种不同工具，每种工具的格式和路径都不同。它的解决方案是**单一源 + 多目标转换**。

### 架构

```text
源文件（统一格式）
  │
  │  部门目录下的 Agent Markdown
  │  frontmatter: name/description/color
  │  正文: 9 个标准章节
  │
  ├── convert.sh ──→ integrations/claude-code/*.md
  ├── convert.sh ──→ integrations/codex/*.toml
  ├── convert.sh ──→ integrations/cursor/*.mdc
  ├── convert.sh ──→ integrations/aider/CONVENTIONS.md
  ├── convert.sh ──→ integrations/windsurf/*.windsurfrules
  └── ...
                     │
                     ▼
                  install.sh
                     │
                     ▼
              各工具的配置目录
```

### tools.json 的安装契约

tools.json 为每个目标工具定义了完整的安装契约：

| 字段 | 作用 |
|------|------|
| `format` | 渲染格式标识——两个工具只有在渲染输出**字节完全相同**时才能共享 format |
| `installKind` | per-agent / roster / plugin |
| `scope` | user（全局）或 project（项目级） |
| `dest` | 目标路径模板（含 `{slug}` 占位符） |
| `detect` | 工具是否已安装的检测命令 |
| `version` | 版本检测命令 |

### 三种安装类型

**per-agent（每代理独立文件）**：

大多数工具采用此模式。每个 Agent 渲染为独立文件，安装到工具的 agents/rules 目录。

| 工具 | 目标路径 |
|------|---------|
| claude-code | `.claude/agents/{slug}.md` |
| codex | `.codex/agents/{slug}.toml` |
| cursor | `.cursor/rules/{slug}.mdc` |

**roster（合并花名册）**：

aider 使用单个 `CONVENTIONS.md` 文件，所有选中的 Agent 合并到一个文件中。适用于不支持多文件扩展的工具。

**plugin（构建产物）**：

hermes 等工具有自己的插件系统，agency-agents 构建为插件产物安装到 `.hermes/plugins/agency-agents-router`。

### format 字节一致性

format 字段的约束比"兼容性"更严格——它要求**字节相同的输出**。这意味着：
- 如果两个工具的渲染结果有任何差异（哪怕是换行符或空行），它们必须使用不同的 format
- format 相同的工具可以共享转换后的文件，避免重复渲染
- CI 可以通过字节比较验证格式一致性

### 安装脚本能力

install.sh 支持灵活的选择和安装选项：

```bash
# 安装特定工具的所有代理
./install.sh --tool claude-code

# 安装特定部门
./install.sh --tool cursor --division engineering

# 安装特定代理
./install.sh --tool codex --agent software-architect

# 符号链接而非复制（便于开发）
./install.sh --tool claude-code --link

# 试运行
./install.sh --dry-run

# 并行安装
./install.sh --parallel --jobs 8
```

### CI 一致性保障

check-divisions.sh 验证五个位置的一致性：
1. 磁盘上的部门目录
2. divisions.json
3. convert.sh 的 AGENT_DIRS
4. lint-agents.sh 的 AGENT_DIRS
5. lint-agents.yml 的路径过滤器

这种"单一真相来源 + CI 门控"的模式确保新增部门或工具时不会遗漏同步点。

## 模式二：Agent Skills 开放标准

jira-skill、retro-skill、awesun-skill 等项目遵循 [agentskills.io](https://agentskills.io) 开放标准，这是一种"约定优于配置"的兼容模式。

### 标准核心

标准定义了：
1. **SKILL.md 文件**：YAML frontmatter + Markdown 正文，位于技能目录根
2. **目录约定**：scripts/、references/、templates/ 等子目录有固定用途
3. **技能发现**：AI 工具扫描技能目录（如 `~/.claude/skills/`），自动发现 SKILL.md
4. **渐进式披露**：frontmatter 始终可见，正文和子目录按需加载

### 跨工具兼容

遵循开放标准的 Skill 可以在多个支持标准的工具间无缝迁移：

| 工具 | 技能目录 |
|------|---------|
| Claude Code | `~/.claude/skills/` 或 `.claude/skills/` |
| OpenCode | `~/.opencode/skills/` 或 `.opencode/skills/` |
| OpenClaw | 对应的 skills/ 目录 |

同一份 SKILL.md 和 scripts/ 文件复制到不同工具的技能目录即可使用，无需格式转换。

### allowed-tools 声明

SKILL.md 的 `allowed-tools` 字段声明技能需要的工具权限：

```yaml
allowed-tools:
  - Bash(python:*)
  - Read
  - Write
```

这是一种可移植的权限声明——支持该标准的工具据此进行权限控制，不支持的工具可能忽略它或要求用户手动授权。

## 模式三：Agent Plugin 规范

jira-skill 和 retro-skill 同时遵循 [agent-plugins.org](https://agent-plugins.org) 的插件规范，这是比 Skill 更高层的打包格式。

### plugin.json 清单

插件规范通过 plugin.json 定义：

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "jira",
  "version": "3.28.0",
  "description": "...",
  "author": { "name": "...", "url": "..." },
  "repository": "...",
  "license": "...",
  "keywords": [...]
}
```

### 插件 vs 技能

| 维度 | Skill | Plugin |
|------|-------|--------|
| 范围 | 单一能力 | 多个技能 + 命令 + 钩子的打包 |
| 清单文件 | SKILL.md frontmatter | plugin.json |
| 斜杠命令 | 不支持 | commands/ 目录 |
| 生命周期钩子 | 不支持 | hooks/ 目录 |
| 质量门控 | 无标准 | checkpoints.yaml |
| 分发 | 目录复制 | 版本化包 + SHA256 + SLSA |

一个插件可以包含多个技能（如 jira-skill 包含 jira-communication 和 jira-syntax），技能是插件的子集。

### 双许可证

两个项目都采用了代码 MIT + 内容 CC-BY-SA-4.0 的双许可证模式，使用 SPDX 表达式 `(MIT AND CC-BY-SA-4.0)`。这允许代码自由集成到商业产品，同时保证文档内容的开源传播。

## 国际化模式

agency-agents 提供了中文本地化方案：

- `scripts/i18n/localize-agents-zh.ps1`：PowerShell 脚本，将已安装代理的 name 和 description 本地化为中文
- `scripts/i18n/agent-names-zh.json`：名称映射文件
- 默认目标目录：`~/.github/agents` 和 `~/.copilot/agents`

脚本流程：读取文件 → 解析 frontmatter → 替换 name/description → 写回，使用 UTF-8 编码。这是一种"安装后本地化"模式——源文件保持英文，安装时根据用户语言替换元数据。

## 集成模式对比

| 模式 | 代表项目 | 适用场景 | 优势 | 代价 |
|------|---------|---------|------|------|
| 格式转换 | agency-agents | 大量人格文件需适配多工具 | 一份源文件，全工具覆盖 | 需维护转换脚本和格式映射 |
| 开放标准 | awesun-skill、ui-locator | 新开发的 Skill | 零转换成本，生态通用 | 依赖工具支持标准 |
| 插件规范 | jira-skill、retro-skill | 复杂的多技能+命令+钩子 | 完整的打包和分发能力 | 规范较新，生态在成长 |

## 混合策略

实际项目常采用混合策略：
- jira-skill 和 retro-skill 同时遵循 Skill 标准和 Plugin 规范——Skill 保证单个技能的可移植性，Plugin 提供多技能打包和命令/钩子能力
- agency-agents 通过 integrations/ 目录也支持 SKILL.md 格式（Antigravity 集成），说明格式转换和开放标准可以共存
- awesun-skill 遵循 Skill 标准，同时其 executor.py 通过 MCP 协议连接工具服务器，形成"标准 Skill + 协议桥接"的三层兼容

## 设计启示

1. **优先遵循开放标准**：新开发的 Skill 应遵循 agentskills.io，避免格式锁定。
2. **单一真相来源**：当需要多格式输出时，像 agency-agents 一样保持统一源文件，用工具转换，而非手动维护多份。
3. **CI 强制一致性**：跨工具配置的同步点应由脚本自动验证，而非人工记忆。
4. **字节级 format 约束**：声称两种工具格式"相同"前，确保输出字节一致。
5. **版本同步门控**：plugin.json 与各 SKILL.md 的版本号必须一致，用 pre-commit/CI 强制。

## 相关概念

- [agency-agents 部门化人格体系](/concepts/02-agency-agents-division.md)
- [Agent 人格文件格式与 frontmatter](/concepts/03-agent-persona-format.md)
- [插件架构（plugin.json/hooks/commands）](/concepts/05-plugin-architecture.md)
- [SKILL.md 标准与渐进式披露](/concepts/01-skill-md-standard.md)
