---
type: Reference
title: agency-agents 源码
description: The Agency 代理人格集合源码登记，含 divisions.json/tools.json 规范、脚本库与 17 部门 200+ 人格清单
tags: [agent-skills, agency-agents, source, reference, persona]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: pending, at: pending }
status: draft
stale_after: 2027-08-23
sources:
  - id: facts-agency-agents
    resource: "/references/facts-agency-agents.md"
    title: agency-agents 事实清单
---

# agency-agents 源码

## 仓库信息

| 属性 | 值 |
|------|-----|
| 项目名 | The Agency |
| 许可证 | MIT |
| 定位 | AI 代理人格集合，每个代理是具有专业技能、个性和可交付成果的专家 |
| 源码路径 | `d:\AI\.chaos\libs\agency-agents\` |
| 支持平台 | macOS / Linux / Windows（原生桌面应用） |
| 目标工具 | Claude Code、Cursor、Codex、Gemini、Copilot、Aider、Windsurf 等 16 种 |

## 核心配置文件

### divisions.json（部门集合唯一真相来源）

定义 17 个部门，每个部门映射到显示标签、Lucide 图标名（PascalCase）和品牌色（hex）：

| 部门 ID | 标签 | 图标 | 颜色 |
|---------|------|------|------|
| academic | Academic | GraduationCap | #8B5CF6 |
| design | Design | PenTool | #EC4899 |
| engineering | Engineering | Code | #3B82F6 |
| finance | Finance | DollarSign | #22C55E |
| game-development | Game Development | Gamepad2 | #A855F7 |
| gis | GIS | Map | #14B8A6 |
| healthcare | Healthcare | Stethoscope | #0D9488 |
| marketing | Marketing | Megaphone | #F97316 |
| paid-media | Paid Media | Target | #EAB308 |
| product | Product | Box | #D946EF |
| project-management | Project Management | ClipboardList | #0EA5E9 |
| sales | Sales | TrendingUp | #10B981 |
| security | Security | ShieldCheck | #EF4444 |
| spatial-computing | Spatial Computing | Boxes | #06B6D4 |
| specialized | Specialized | Sparkles | #6366F1 |
| support | Support | LifeBuoy | #84CC16 |
| testing | Testing | FlaskConical | #F59E0B |

非部门目录通过 `NON_DIVISION_DIRS` 排除：`integrations/`、`strategy/`、`examples/`、`scripts/`。

### tools.json（工具安装契约）

定义 16 个支持工具，每个条目包含：id、label、kebab、accent、icon、order、scope（user/project）、detect、version、format、installKind、dest。

三种 installKind：
- **per-agent**：每代理一个渲染文件（如 claude-code 安装到 `.claude/agents/{slug}.md`）
- **roster**：所有代理合并为一个文件（如 aider 安装为 `CONVENTIONS.md`）
- **plugin**：构建产物，不可按代理渲染（如 hermes 安装为 `.hermes/plugins/agency-agents-router`）

format 字段保证字节相同的输出——两个工具只有在渲染文件完全相同时才能共享 format。

## 关键源文件清单

### 脚本库（`scripts/`）

| 文件 | 职责 |
|------|------|
| `scripts/lib.sh` | 纯 Bash 共享辅助库，兼容 Bash 3.2+，无外部依赖。含 `get_field()`、`get_body()`、`slugify()`、`agent_slug()`、`is_agent_file()`、`incr()` 及终端能力函数 |
| `scripts/install.sh` | 从 integrations/ 读取转换文件并复制到各工具配置目录，支持 --tool/--division/--agent/--link/--dry-run/--parallel 等参数 |
| `scripts/convert.sh` | 将 Agent Markdown 转换为各工具格式，含 AGENT_DIRS 数组（需与 divisions.json 同步） |
| `scripts/check-divisions.sh` | 验证 5 位置一致性（磁盘目录、divisions.json、convert.sh、lint-agents.sh、lint-agents.yml），使用 git ls-files，无 jq 依赖 |
| `scripts/lint-agents.sh` | 验证 Agent Markdown frontmatter 必须含 name/description/color（ERROR），推荐章节（WARN），含 classify_header_target() |
| `scripts/build-hermes-plugin.py` | 构建 hermes 插件产物 |
| `scripts/check-hermes-plugin.py` | 验证 hermes 插件 |
| `scripts/check-agent-originality.sh` | 检查代理原创性 |
| `scripts/check-runbooks.sh` | 验证 runbook 文件 |
| `scripts/check-tools.sh` | 验证工具配置 |
| `scripts/i18n/localize-agents-zh.ps1` | PowerShell 脚本，将已安装代理的 name/description 本地化为中文 |

### 策略文档（`strategy/`）

| 文件 | 职责 |
|------|------|
| `strategy/QUICKSTART.md` | NEXUS 策略快速入门，三种模式（Full/Sprint/Micro），7 阶段流水线 |
| `strategy/nexus-strategy.md` | NEXUS（Network of EXperts, Unified in Strategy）完整策略 |
| `strategy/playbooks/` | 7 个阶段 playbook（phase-0-discovery 至 phase-6-operate） |
| `strategy/runbooks/` | 场景化 runbook（企业功能、事件响应、营销活动、创业 MVP） |
| `strategy/coordination/` | 协调模板（agent-activation-prompts、handoff-templates） |

### 集成输出（`integrations/`）

支持 15 种工具格式：Claude Code（.md）、Antigravity（SKILL.md）、Cursor（.mdc）、Aider（CONVENTIONS.md）、Windsurf（.windsurfrules）、Gemini CLI、GitHub Copilot、OpenCode、Qwen、Kimi、OpenClaw、Vibe、ZCode、Hermes、MCP Memory 等。

### Agent 人格文件（17 部门目录）

每个 `.md` 文件使用 YAML frontmatter（必需 name/description/color），正文包含 9 个标准章节：
1. Identity & Memory
2. Core Mission
3. Critical Rules
4. Technical Deliverables
5. Workflow Process
6. Communication Style
7. Learning & Memory
8. Success Metrics
9. Advanced Capabilities

文件分为两组语义部分：**Persona**（身份、沟通风格、规则）和 **Operations**（使命、交付物、工作流、指标、高级能力）。
