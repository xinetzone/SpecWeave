---
type: Concept
title: agency-agents 部门化人格体系
description: The Agency 的 17 部门 200+ 人格组织架构，divisions.json/tools.json 单一真相来源，CI 一致性校验与多工具格式转换
tags: [agent-skills, agency-agents, division, persona, organization, tools]
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

# agency-agents 部门化人格体系

agency-agents（The Agency）是一个模拟专业服务公司组织架构的 AI 代理人格集合。它不是零散的提示词堆积，而是以**部门化分类**和**单一真相来源**为核心设计原则的工程化体系，包含 17 个部门、200+ 个专业人格，并支持一键安装到 16 种 AI 工具。

## 部门体系（divisions.json）

`divisions.json` 是部门集合的**唯一真相来源**。每个部门映射到三个属性：

| 属性 | 说明 | 示例 |
|------|------|------|
| `label` | 显示名称 | "Engineering" |
| `icon` | Lucide 图标名（PascalCase） | "Code" |
| `color` | 品牌色（hex） | "#3B82F6" |

17 个部门覆盖了专业服务的主要领域：

| 部门 | 图标 | 颜色 | 领域 |
|------|------|------|------|
| academic | GraduationCap | #8B5CF6 | 学术研究 |
| design | PenTool | #EC4899 | 设计 |
| engineering | Code | #3B82F6 | 工程开发（最大部门，60+ 人格） |
| finance | DollarSign | #22C55E | 财务金融 |
| game-development | Gamepad2 | #A855F7 | 游戏开发（含 Unity/Unreal/Godot/Roblox/Blender 子目录） |
| gis | Map | #14B8A6 | 地理信息系统 |
| healthcare | Stethoscope | #0D9488 | 医疗健康 |
| marketing | Megaphone | #F97316 | 市场营销（40+ 人格，含中国市场专员） |
| paid-media | Target | #EAB308 | 付费媒体 |
| product | Box | #D946EF | 产品管理 |
| project-management | ClipboardList | #0EA5E9 | 项目管理 |
| sales | TrendingUp | #10B981 | 销售 |
| security | ShieldCheck | #EF4444 | 安全 |
| spatial-computing | Boxes | #06B6D4 | 空间计算（visionOS/macOS Spatial/XR） |
| specialized | Sparkles | #6366F1 | 综合专家（50+ 人格，含跨领域角色） |
| support | LifeBuoy | #84CC16 | 支持服务 |
| testing | FlaskConical | #F59E0B | 测试 |

### 非部门目录

并非所有顶级目录都是部门。`integrations/`（转换输出）、`strategy/`（策略文档）、`examples/`（示例）、`scripts/`（脚本）通过 `NON_DIVISION_DIRS` 排除。一个部门目录必须包含至少一个以 `---` frontmatter 开头的 `.md` 文件。

### 添加新部门的流程

1. 创建部门目录
2. 在 `divisions.json` 添加条目（label/icon/color）
3. 更新 `scripts/convert.sh` 和 `scripts/lint-agents.sh` 中的 `AGENT_DIRS` 数组
4. 更新 `.github/workflows/lint-agents.yml` 的路径过滤器
5. 运行 `scripts/check-divisions.sh` 验证一致性

## 工具适配（tools.json）

`tools.json` 是支持工具集的唯一真相来源，定义了 16 个 AI 工具的安装契约：

claude-code、codex、gemini-cli、copilot、qwen、cursor、opencode、osaurus、aider、antigravity、kimi、openclaw、windsurf、hermes、vibe、zcode。

每个工具条目包含：

| 字段 | 说明 |
|------|------|
| `id` | 工具唯一标识 |
| `label` | 显示名称 |
| `kebab` | kebab-case 名称 |
| `accent` | 品牌强调色 |
| `icon` | 图标 |
| `order` | 排序权重 |
| `scope` | 安装范围：`user`（全局）或 `project`（项目级） |
| `detect` | 工具检测方式 |
| `version` | 版本检测命令 |
| `format` | 渲染格式标识（保证字节相同输出） |
| `installKind` | 安装类型 |
| `dest` | 安装目标路径模板 |

### 三种安装类型（installKind）

| 类型 | 行为 | 典型目标 | 示例工具 |
|------|------|---------|---------|
| `per-agent` | 每个代理渲染为独立文件 | `.claude/agents/{slug}.md` | claude-code、codex、cursor |
| `roster` | 所有代理合并为一个文件 | `CONVENTIONS.md` | aider |
| `plugin` | 构建为插件产物 | `.hermes/plugins/agency-agents-router` | hermes |

`format` 字段的设计约束是：两个工具只有在渲染文件完全相同时才能共享 format。这比"兼容性"更严格——它要求字节级一致性。

### 安装范围

- **用户范围（user）**：安装到用户主目录的全局配置，所有项目可用（如 claude-code 的 `~/.claude/agents/`）
- **项目范围（project）**：安装到项目目录，仅该项目可用（如 cursor 的 `.cursor/rules/`、aider 的 `CONVENTIONS.md`）

项目范围工具（OpenCode、Cursor、Aider、Windsurf、Qwen）需从目标项目根目录运行安装程序。

## CI 一致性校验

`scripts/check-divisions.sh` 强制执行部门集合的单一真相来源，验证**五个位置**的一致性：

1. 磁盘上的顶级代理目录（使用 `git ls-files` 而非文件系统 glob，确保与 CI 干净检出一致）
2. `divisions.json` 中的部门定义
3. `scripts/convert.sh` 的 `AGENT_DIRS` 数组
4. `scripts/lint-agents.sh` 的 `AGENT_DIRS` 数组
5. `.github/workflows/lint-agents.yml` 的路径过滤器

脚本无 jq 依赖，仅使用 Bash 3.2 + coreutils（awk/grep/sed），确保 macOS 和 CI 上行为一致。`canonical()` 函数从 divisions.json 提取部门名称，`actual_dirs()` 使用 `git ls-files` 获取磁盘上的实际部门目录。

## 脚本工具链

| 脚本 | 职责 |
|------|------|
| `scripts/lib.sh` | 纯 Bash 共享库，提供 `get_field()`、`get_body()`、`slugify()`、`agent_slug()`、`is_agent_file()` 等函数 |
| `scripts/convert.sh` | 将 Agent Markdown 转换为各工具格式，AGENT_DIRS 数组需与 divisions.json 同步 |
| `scripts/install.sh` | 从 integrations/ 读取转换文件并安装到各工具配置目录，支持 --tool/--division/--agent/--link/--dry-run/--parallel |
| `scripts/lint-agents.sh` | 验证 Agent 文件 frontmatter 和章节结构 |
| `scripts/check-divisions.sh` | 五位置一致性校验 |
| `scripts/check-tools.sh` | 工具配置校验 |
| `scripts/check-runbooks.sh` | Runbook 文件校验 |
| `scripts/i18n/localize-agents-zh.ps1` | 中文本地化 PowerShell 脚本 |

### lib.sh 核心函数

- `get_field(field, file)`：使用 awk 提取 YAML frontmatter 字段值
- `get_body(file)`：去除前导 frontmatter 块返回文件正文
- `slugify(string)`：将字符串转为 kebab-case（"Frontend Developer" → "frontend-developer"）
- `agent_slug(file)`：从文件的 name frontmatter 派生 slug，是 convert + install 一致的唯一真相来源
- `is_agent_file(file)`：检查文件是否以 `---` frontmatter 分隔符开头

## NEXUS 编排策略

NEXUS（Network of EXperts, Unified in Strategy）将静态人格集合转变为协调流水线，提供三种模式：

| 模式 | 周期 | 代理数量 | 适用场景 |
|------|------|---------|---------|
| Full | 12-24 周 | 全代理 | 企业级完整产品开发 |
| Sprint | 2-6 周 | 15-25 代理 | 集中功能交付 |
| Micro | 1-5 天 | 5-10 代理 | 快速原型/MVP |

Full 模式包含 7 个阶段（Phase 0-6）：发现 → 策略 → 基础 → 构建 → 加固 → 发布 → 运营。每阶段之间有质量门控，所有评估需要证据，每任务最大重试 3 次。

## 设计启示

agency-agents 的部门化体系为多 Agent 组织提供了可复用的模式：

1. **分类法先行**：在编写任何人格之前先定义 divisions.json 分类体系，避免无序增长。
2. **单一真相来源**：部门定义、工具定义、版本号等都有唯一的 JSON 文件作为真相来源，CI 强制一致性。
3. **格式抽象**：通过 format 和 installKind 将"内容"与"目标格式"解耦，新增工具只需添加 tools.json 条目。
4. **人格即文件**：每个 Agent 是一个 Markdown 文件，可版本控制、可 diff、可本地化。

## 相关概念

- [Agent 人格文件格式与 frontmatter](/concepts/03-agent-persona-format.md)
- [多工具兼容与集成模式](/concepts/11-integration-patterns.md)
- [AI Agent Skills 生态概览](/concepts/00-overview.md)
