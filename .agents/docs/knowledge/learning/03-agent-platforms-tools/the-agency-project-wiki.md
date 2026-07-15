---
title: "The Agency 项目完整学习教程"
source: "微信公众号文章《一人组建一支 Agent 军团，狂揽 11.9 万 Star!》+ GitHub 源码分析"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/the-agency-project-wiki.toml"
date: "2026-07-04"
tags: ["the-agency", "ai-agent", "agent-framework", "multi-agent", "claude-code", "cursor"]
---
# The Agency 项目完整学习教程

> **原文参考**: [一人组建一支 Agent 军团，狂揽 11.9 万 Star!](https://mp.weixin.qq.com/s/A1dFio_9NqKKsVQ0SSUIWg?from=industrynews&color_scheme=light#rd)
> **GitHub 项目**: [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)

---

## 📋 目录导航

- [一、核心概念](#一核心概念)
  - [1.1 什么是 The Agency](#11-什么是-the-agency)
  - [1.2 项目起源](#12-项目起源)
  - [1.3 架构设计](#13-架构设计)
- [二、组织架构](#二组织架构)
  - [2.1 16 个部门概览](#21-16-个部门概览)
  - [2.2 核心部门详解](#22-核心部门详解)
- [三、分步骤操作指南](#三分步骤操作指南)
  - [3.1 方式一：使用桌面客户端（推荐）](#31-方式一使用桌面客户端推荐)
  - [3.2 方式二：使用 Claude Code](#32-方式二使用-claude-code)
  - [3.3 方式三：使用其他工具](#33-方式三使用其他工具)
  - [3.4 方式四：手动参考使用](#34-方式四手动参考使用)
- [四、关键技术点解析](#四关键技术点解析)
  - [4.1 Agent 角色定义结构](#41-agent-角色定义结构)
  - [4.2 Frontmatter 元数据](#42-frontmatter-元数据)
  - [4.3 工作流设计](#43-工作流设计)
  - [4.4 交付物模板](#44-交付物模板)
- [五、常见问题解答](#五常见问题解答)
- [六、相关资源链接](#六相关资源链接)

---

## 一、核心概念

### 1.1 什么是 The Agency

**The Agency** 是一个开源的 AI Agent 角色库项目，旨在为用户提供一个完整的 AI 军团。正如原文所述：

> "目前作者还在持续更新维护，项目已经冲到了 11.9 万 Star，可以说是得到了大部分人的认可。"

项目的核心特点：

| 特性 | 描述 |
|------|------|
| **专业化** | 每个 Agent 都是特定领域的专家，而非通用的提示词模板 |
| **人格化** | 每个 Agent 都有独特的语气、沟通风格和工作方式 |
| **成果导向** | 专注于交付实际代码、流程和可衡量的成果 |
| **生产就绪** | 经过实战检验的工作流和成功指标 |

### 1.2 项目起源

项目的起源非常有趣，正如原文描述：

> "项目起源作者在 Reddit 上随手发的一个帖子，讨论的是 AI Agent 该怎么做专业化分工。没想到评论里，大家都在求资源，于是作者便基于大家需求构建出 232+ 个 Agent，并分成 16 个部门。"

根据源码最新统计，目前项目包含 **233 个 Agent 角色**，分为 16 个专业部门。

这种源于社区需求的开发模式，使得项目能够快速响应实际使用场景，不断迭代优化。

### 1.3 架构设计

The Agency 采用**部门化**的组织架构，将 233 个 Agent 角色划分为 16 个部门：

- **工程部门**（Engineering）：前端开发、后端架构、移动开发等
- **设计部门**（Design）：UI 设计、UX 研究、品牌设计等
- **营销部门**（Marketing）：增长黑客、内容创作、社交媒体等
- **产品部门**（Product）：产品经理、需求排期、趋势分析等
- **测试部门**（Testing）：功能测试、性能测试、API 测试等
- **安全部门**（Security）：安全架构、渗透测试、合规审计等
- **销售部门**（Sales）：销售策略、客户开发、渠道管理等
- **项目管理部门**（Project Management）：项目协调、进度跟踪、会议管理等
- **付费媒体部门**（Paid Media）：PPC、广告投放、效果追踪等
- **财务部门**（Finance）：财务分析、税务策略、投资研究等
- **游戏开发部门**（Game Development）：Unity、Unreal、Godot 等引擎开发
- **GIS 部门**：地理空间分析、地图开发等
- **学术部门**（Academic）：人类学、地理学、历史学等
- **空间计算部门**（Spatial Computing）：XR、Vision Pro 等
- **支持部门**（Support）：客户支持、数据分析、基础设施维护等
- **专业部门**（Specialized）：法务、医疗、人力资源等特殊领域

---

## 二、组织架构

### 2.1 16 个部门概览

根据源码中的 [divisions.json](https://github.com/msitarzewski/agency-agents/blob/main/divisions.json)，16 个部门及其配置如下：

| 部门 | 图标 | 颜色 | Agent 数量 |
|------|------|------|-----------|
| Engineering | Code | #3B82F6 | 34 |
| Marketing | Megaphone | #F97316 | 36 |
| Design | PenTool | #EC4899 | 9 |
| Specialized | Sparkles | #636F1 | 53 |
| Testing | FlaskConical | #F59E0B | 8 |
| Security | ShieldCheck | #EF4444 | 10 |
| Product | Box | #D946EF | 5 |
| Project Management | ClipboardList | #0EA5E9 | 7 |
| Sales | TrendingUp | #10B981 | 9 |
| Paid Media | Target | #EAB308 | 7 |
| Finance | DollarSign | #22C55E | 5 |
| Game Development | Gamepad2 | #A855F7 | 20 |
| GIS | Map | #14B8A6 | 13 |
| Spatial Computing | Boxes | #06B6D4 | 6 |
| Academic | GraduationCap | #8B5CF6 | 5 |
| Support | LifeBuoy | #84CC16 | 6 |

**总计**：233 个 Agent 角色

### 2.2 核心部门详解

#### 工程部门（Engineering）

工程部门是角色最全的部门，涵盖：

- **前端开发者**：React/Vue/Angular，UI 实现，性能优化
- **后端架构师**：API 设计，数据库架构，可扩展性
- **移动端开发**：iOS/Android，React Native，Flutter
- **AI 工程师**：ML 模型，部署，AI 集成
- **DevOps 自动化工程师**：CI/CD，基础设施自动化
- **代码审查员**：建设性代码审查，安全性，可维护性
- **微信小程序开发者**：微信生态，小程序开发，支付集成

#### 营销部门（Marketing）

营销部门涵盖各类平台的专业运营：

- **增长黑客**：快速用户获取，病毒循环，实验
- **内容创作者**：多平台内容，编辑日历
- **小红书专家**：生活方式内容，趋势驱动策略
- **抖音策略师**：抖音平台，短视频营销
- **知乎策略师**：思想领导力，知识驱动互动
- **B站内容策略师**：B站算法，弹幕文化
- **微信公众号运营**：订阅者互动，内容营销

#### 设计部门（Design）

设计部门负责产品的视觉呈现：

- **UI 设计师**：视觉设计，组件库，设计系统
- **UX 研究员**：用户测试，行为分析，研究
- **UX 架构师**：技术架构，CSS 系统，实现指导
- **品牌守护者**：品牌标识，一致性，定位
- **视觉故事讲述者**：视觉叙事，多媒体内容

#### 产品部门（Product）

产品部门负责产品规划：

- **产品经理**：全生命周期产品管理
- **Sprint 优先级排序师**：敏捷规划，功能优先级
- **趋势研究员**：市场情报，竞争分析
- **反馈综合师**：用户反馈分析，洞察提取

#### 测试部门（Testing）

测试部门负责质量保障：

- **API 测试员**：API 验证，集成测试
- **性能基准测试员**：性能测试，优化
- **可访问性审计员**：WCAG 审计，辅助技术测试
- **现实检验员**：基于证据的认证，质量门

---

## 三、分步骤操作指南

### 3.1 方式一：使用桌面客户端（推荐）

原文推荐使用桌面客户端，因为：

> "为了解决这个问题，作者配套了一个桌面客户端 Agency Agents，让我们可以按需选择 Agent。支持 Windows、macOS、Linux 系统，安装包可以在项目的发布页面上找到，开箱即用。"

**操作步骤**：

1. **下载客户端**
   - 访问 [Agency Agents 发布页面](https://github.com/msitarzewski/agency-agents-app/releases/latest)
   - 选择对应操作系统的安装包（Windows/macOS/Linux）
   - macOS 用户也可以使用 Homebrew 安装：
     ```bash
     brew install --cask msitarzewski/agency-agents/agency-agents
     ```

2. **安装客户端**
   - 运行安装程序，按照提示完成安装
   - 启动 Agency Agents 应用

3. **选择 Agent**
   - 在应用中浏览所有 16 个部门的 Agent 角色
   - 根据需求选择需要的 Agent（如前端开发者、产品经理等）

4. **部署到项目**
   - 选择目标 AI 编程工具（Claude Code、Cursor、Codex 等）
   - 点击安装按钮，自动部署到对应工具

### 3.2 方式二：使用 Claude Code

**操作步骤**：

1. **克隆项目**
   ```bash
   git clone https://github.com/msitarzewski/agency-agents.git
   cd agency-agents
   ```

2. **安装所有 Agent**
   ```bash
   ./scripts/install.sh --tool claude-code
   ```

3. **或只安装特定部门**
   ```bash
   cp engineering/*.md ~/.claude/agents/
   ```

4. **在 Claude Code 中激活**
   ```
   Hey Claude, activate Frontend Developer mode and help me build a React component
   ```

### 3.3 方式三：使用其他工具

The Agency 支持 15+ 种 AI 编程工具，每种工具都有专门的集成方案：

| 工具 | 集成格式 | 安装位置 | 特殊要求 |
|------|----------|----------|----------|
| **Claude Code** | `.md` 原生 | `~/.claude/agents/` | 无 |
| **GitHub Copilot** | `.md` 原生 | `~/.github/agents/` | 无 |
| **Cursor** | `.mdc` 规则文件 | 项目级 `.cursor/rules/` | 需从项目根目录运行 |
| **Codex** | `.toml` 自定义 Agent | `~/.codex/agents/` | 需先运行 `convert.sh` |
| **Gemini CLI** | `.md` 子 Agent | `~/.gemini/agents/` | 需先运行 `convert.sh` |
| **Antigravity** | `SKILL.md` | `~/.gemini/antigravity/skills/` | 无 |
| **OpenCode** | `.md` Agent 文件 | 项目级 `.opencode/agents/` | 需从项目根目录运行 |
| **OpenClaw** | `SOUL.md` + `AGENTS.md` + `IDENTITY.md` | OpenClaw 工作空间 | 需先运行 `convert.sh`，安装后重启 gateway |
| **Aider** | 单个 `CONVENTIONS.md` | 项目根目录 | 需从项目根目录运行 |
| **Windsurf** | 单个 `.windsurfrules` | 项目根目录 | 需从项目根目录运行 |
| **Kimi Code** | YAML Agent 规范 | `~/.config/kimi/agents/` | 需先运行 `convert.sh` |
| **Qwen Code** | `.md` SubAgent | 项目级 `.qwen/agents/` | 需先运行 `convert.sh` |
| **Osaurus** | `SKILL.md` | Osaurus skills 目录 | 无 |
| **Hermes** | lazy-router 插件 | Hermes 插件目录 | 无 |

**操作步骤**：

1. **生成集成文件**（部分工具需要）
   ```bash
   ./scripts/convert.sh
   # 或针对特定工具
   ./scripts/convert.sh --tool gemini-cli
   ./scripts/convert.sh --tool kimi
   ./scripts/convert.sh --tool qwen
   ./scripts/convert.sh --tool codex
   ```

2. **交互式安装**
   ```bash
   ./scripts/install.sh
   ```

3. **指定特定工具**
   ```bash
   ./scripts/install.sh --tool cursor
   ./scripts/install.sh --tool codex
   ./scripts/install.sh --tool opencode
   ./scripts/install.sh --tool kimi
   ./scripts/install.sh --tool qwen
   ```

4. **项目级工具安装**（从项目根目录运行）
   ```bash
   cd /your/project && /path/to/agency-agents/scripts/install.sh --tool cursor
   cd /your/project && /path/to/agency-agents/scripts/install.sh --tool opencode
   cd /your/project && /path/to/agency-agents/scripts/install.sh --tool aider
   ```

5. **安装指定部门**
   ```bash
   ./scripts/install.sh --tool claude-code --division engineering,security
   ```

6. **安装指定 Agent**
   ```bash
   ./scripts/install.sh --tool cursor --agent frontend-developer,ui-designer
   ```

### 3.4 方式四：手动参考使用

每个 Agent 文件包含完整的角色定义，可以直接参考使用：

1. **浏览 Agent 文件**
   - 进入对应部门目录，查看 Agent 文件
   - 例如：`engineering/engineering-frontend-developer.md`

2. **复制内容**
   - 将 Agent 定义内容复制到你的 AI 编程工具中
   - 作为自定义角色或提示词使用

3. **按需修改**
   - 根据实际需求调整角色定义
   - 修改语气、工作流、交付物等

---

## 四、关键技术点解析

### 4.1 Agent 角色定义结构

每个 Agent 文件都遵循统一的结构，以下是基于 [engineering-frontend-developer.md](https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-frontend-developer.md) 的分析：

#### 4.1.1 身份与记忆（Identity & Memory）

定义 Agent 的基本属性：
- **角色**：专业领域定位
- **人格**：沟通风格和态度
- **记忆**：需要记住的知识和经验
- **经验**：过往的成功与失败案例

#### 4.1.2 核心使命（Core Mission）

定义 Agent 的主要职责和任务：
- 明确列出核心工作领域
- 包含具体的技术要求和标准
- 设定默认约束条件

#### 4.1.3 关键规则（Critical Rules）

定义 Agent 必须遵守的规则：
- 性能优先开发原则
- 可访问性和包容性设计要求
- 质量标准和合规性要求

#### 4.1.4 技术交付物（Technical Deliverables）

提供代码示例和实现模式：
- 包含真实的代码示例
- 展示最佳实践和技术栈选择
- 提供可复用的代码模板

#### 4.1.5 工作流程（Workflow Process）

定义标准化的工作流程：
- Step 1: 项目设置和架构
- Step 2: 组件开发
- Step 3: 性能优化
- Step 4: 测试和质量保证

#### 4.1.6 交付物模板（Deliverable Template）

提供标准化的输出格式：
- 统一的文档结构
- 明确的输出要求
- 可衡量的成果指标

#### 4.1.7 沟通风格（Communication Style）

定义 Agent 的语言风格：
- 精确的技术表达
- 用户体验导向的表述
- 性能意识的强调
- 可访问性的关注

#### 4.1.8 学习与记忆（Learning & Memory）

定义 Agent 需要积累的知识：
- 性能优化模式
- 组件架构
- 可访问性技术
- 测试策略

#### 4.1.9 成功指标（Success Metrics）

定义衡量 Agent 工作质量的标准：
- 量化的性能指标
- 质量评分要求
- 兼容性要求
- 代码复用率

#### 4.1.10 高级能力（Advanced Capabilities）

定义 Agent 的进阶技能：
- 前沿技术掌握
- 高级优化技术
- 领导能力

### 4.2 Frontmatter 元数据

每个 Agent 文件都包含 YAML frontmatter，用于存储元数据：

```yaml
---
name: Frontend Developer
description: Expert frontend developer specializing in modern web technologies
color: cyan
emoji: 🖥️
vibe: Builds responsive, accessible web apps with pixel-perfect precision.
---
```

| 字段 | 说明 |
|------|------|
| `name` | Agent 名称 |
| `description` | Agent 描述 |
| `color` | 主题颜色 |
| `emoji` | 表情符号 |
| `vibe` | 风格描述 |

### 4.3 工作流设计

The Agency 的工作流设计遵循**标准化流程**，以确保每个 Agent 都能按照一致的方式工作：

1. **项目初始化**：环境设置、工具配置、架构规划
2. **核心开发**：组件开发、功能实现、代码编写
3. **优化阶段**：性能优化、代码审查、质量提升
4. **测试验证**：单元测试、集成测试、端到端测试

这种标准化的工作流设计使得不同 Agent 之间可以无缝协作，形成完整的工作链条。

### 4.4 交付物模板

每个 Agent 都提供了标准化的交付物模板，确保输出的一致性和质量。以 Frontend Developer 为例：

```markdown
# [Project Name] Frontend Implementation

## 🎨 UI Implementation
**Framework**: [React/Vue/Angular with version and reasoning]
**State Management**: [Redux/Zustand/Context API implementation]
**Styling**: [Tailwind/CSS Modules/Styled Components approach]

## ⚡ Performance Optimization
**Core Web Vitals**: [LCP < 2.5s, FID < 100ms, CLS < 0.1]
**Bundle Optimization**: [Code splitting and tree shaking]

## ♿ Accessibility Implementation
**WCAG Compliance**: [AA compliance with specific guidelines]
**Screen Reader Support**: [VoiceOver, NVDA, JAWS compatibility]
```

### 4.5 NEXUS 工作流系统

**NEXUS**（Network of EXperts, Unified in Strategy）是 The Agency 的多 Agent 协调流水线系统，将 233 个 AI 专家转化为一个协调一致的工作流程。

#### 4.5.1 三种工作模式

| 模式 | 适用场景 | Agent 数量 | 时间 |
|------|----------|-----------|------|
| **NEXUS-Full** | 从零构建完整产品 | 全部 Agent | 12-24 周 |
| **NEXUS-Sprint** | 构建功能或 MVP | 15-25 个 | 2-6 周 |
| **NEXUS-Micro** | 特定任务（Bug 修复、营销活动、审计） | 5-10 个 | 1-5 天 |

#### 4.5.2 七大阶段流程

NEXUS-Full 模式包含七个标准化阶段：

1. **Phase 0: Discovery（发现）** — 趋势研究员、反馈综合师、UX 研究员、数据分析员、法务合规检查、工具评估
2. **Phase 1: Strategy（策略）** — 工作室制作人、高级项目经理、Sprint 优先级排序师、UX 架构师、品牌守护者、后端架构师、财务追踪员
3. **Phase 2: Foundation（基础）** — DevOps 自动化工程师、前端开发者、后端架构师、UX 架构师、基础设施维护员
4. **Phase 3: Build（构建）** — 开发↔测试循环（所有工程师 + 证据收集员）
5. **Phase 4: Harden（加固）** — 现实检验员、性能基准测试员、API 测试员、法务合规检查
6. **Phase 5: Launch（发布）** — 增长黑客、内容创作者、所有营销 Agent、DevOps 自动化工程师
7. **Phase 6: Operate（运营）** — 数据分析员、基础设施维护员、支持响应者（持续）

#### 4.5.3 核心概念

- **Quality Gates（质量门）** — 每个阶段必须通过基于证据的审批才能进入下一阶段
- **Dev↔QA Loop** — 每个任务先构建再测试，通过才能继续，失败重试（最多 3 次）
- **Handoffs（交接）** — Agent 之间结构化的上下文传递（从不冷启动）
- **Reality Checker（现实检验员）** — 最终质量权威，默认"需要改进"
- **Agents Orchestrator（Agent 编排器）** — 管理整个流程的流水线控制器
- **Evidence Over Claims（证据优先）** — 截图、测试结果、数据优先，而非断言

---

## 五、常见问题解答

### Q1: 全部安装所有 Agent 会有什么问题？

**A**: 正如原文所述：

> "那么这么多 Agent 角色我们该如何选择，要是全部装到项目里，上下文估计要爆。"

建议按需选择安装，避免上下文过长影响 AI 模型的响应质量。可以使用桌面客户端或命令行工具按部门或单个 Agent 进行安装。

### Q2: 如何自定义修改 Agent 角色？

**A**: 原文提到：

> "如果这些角色定义觉得不符合我们的需求，也能打开它们的文件进行自定义修改。"

你可以：
1. 直接编辑对应的 `.md` 文件
2. 修改 frontmatter 元数据
3. 调整身份定义、工作流程和交付物模板
4. 更新成功指标和沟通风格

### Q3: 支持哪些 AI 编程工具？

**A**: 支持以下工具：
- Claude Code
- Cursor
- Codex
- Gemini CLI
- OpenCode
- OpenClaw
- Aider
- Windsurf
- Kimi Code
- Osaurus
- Hermes

### Q4: OpenCode 有什么限制？

**A**: OpenCode 的运行时目前只注册约 119 个 Agent，超出部分会被静默丢弃。建议使用 `--division` 参数安装子集。

### Q5: 如何更新 Agent？

**A**: 
- 桌面客户端会自动更新
- 命令行方式可以重新克隆项目并运行安装脚本
- 或使用 `git pull` 更新后重新安装

### Q6: 是否支持中文 Agent？

**A**: 项目提供了中文翻译脚本（`scripts/i18n/localize-agents-zh.ps1`），可以将 Agent 名称等本地化，但目前主要内容仍是英文。

---

## 六、相关资源链接

### 官方资源

- **GitHub 项目**：[msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)
- **桌面客户端**：[Agency Agents App](https://github.com/msitarzewski/agency-agents-app)
- **官方网站**：[agencyagents.app](https://agencyagents.app)

### 学习资源

- **原文参考**：[一人组建一支 Agent 军团，狂揽 11.9 万 Star!](https://mp.weixin.qq.com/s/A1dFio_9NqKKsVQ0SSUIWg?from=industrynews&color_scheme=light#rd)
- **项目文档**：[GitHub README](https://github.com/msitarzewski/agency-agents/blob/main/README.md)
- **集成指南**：[integrations/](https://github.com/msitarzewski/agency-agents/tree/main/integrations)

### 工具链

- **Claude Code**：[官方网站](https://www.anthropic.com/index/claude-code)
- **Cursor**：[官方网站](https://cursor.sh)
- **Codex**：[官方网站](https://www.codex.so)
- **Gemini CLI**：[Google AI](https://ai.google.dev/gemini-api/docs/cli)

### 社区资源

- **Reddit 讨论**：[r/ClaudeCode](https://www.reddit.com/r/ClaudeCode/)
- **贡献指南**：[CONTRIBUTING.md](https://github.com/msitarzewski/agency-agents/blob/main/CONTRIBUTING.md)
- **中文贡献指南**：[CONTRIBUTING_zh-CN.md](https://github.com/msitarzewski/agency-agents/blob/main/CONTRIBUTING_zh-CN.md)

---

**文档版本**: v1.0  
**更新日期**: 2026-07-04  
**来源**: 微信公众号文章 + GitHub 源码分析