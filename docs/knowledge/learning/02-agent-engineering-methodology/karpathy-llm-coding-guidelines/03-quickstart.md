---
id: "karpathy-llm-coding-guidelines-quickstart"
title: "快速上手指南"
category: learning
tags: [karpathy, llm, coding, agent, guidelines, claude-code, cursor, installation, quickstart, skills, plugin]
date: "2026-07-02"
status: stable
author: "multica-ai"
summary: "快速上手安装和使用指南：三种分发格式对比（CLAUDE.md/SKILL.md/Cursor Rules）、Claude Code插件安装、Cursor编辑器集成详解、SKILL.md格式、项目定制方法、贡献者指南。"
source: "https://github.com/multica-ai/andrej-karpathy-skills"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/03-quickstart.toml"
---
# 快速上手指南

## 三种分发格式概览

本仓库提供了**四种集成方式**，适用于不同工具和使用场景：

| 格式 | 文件位置 | 适用工具 | 作用范围 | 说明 |
|------|---------|---------|---------|------|
| **CLAUDE.md** | 项目根目录 `CLAUDE.md` | Claude Code、Codex CLI 等 | 单项目 | 最简单，丢进项目根目录就生效 |
| **Cursor Rules** | `.cursor/rules/karpathy-guidelines.mdc` | Cursor 编辑器 | 单项目 | `alwaysApply: true` 自动生效 |
| **Agent Skill** | `skills/karpathy-guidelines/SKILL.md` | Claude Code（插件）、支持 Skills 的工具 | 跨项目 | 可复用的技能包，通过插件市场安装 |
| **Claude Plugin** | `.claude-plugin/` 目录 | Claude Code | 跨项目 | 插件市场分发，一键安装所有项目可用 |

---

## 安装方式

### 选项 A：Claude Code 插件（推荐，跨项目）

安装插件后，所有项目自动生效，无需每个项目配置。

在 Claude Code 中，首先添加插件市场：

```
/plugin marketplace add multica-ai/andrej-karpathy-skills
```

然后安装插件：

```
/plugin install andrej-karpathy-skills@karpathy-skills
```

#### 插件配置文件说明

插件由两个 JSON 文件配置：

**`.claude-plugin/plugin.json`** - 插件元数据：
```json
{
  "name": "andrej-karpathy-skills",
  "description": "Behavioral guidelines to reduce common LLM coding mistakes, derived from Andrej Karpathy's observations on LLM coding pitfalls",
  "version": "1.0.0",
  "author": { "name": "forrestchang" },
  "license": "MIT",
  "keywords": ["guidelines", "best-practices", "coding", "karpathy"],
  "skills": ["./skills/karpathy-guidelines"]
}
```

**`.claude-plugin/marketplace.json`** - 市场注册信息：
```json
{
  "name": "karpathy-skills",
  "id": "karpathy-skills",
  "owner": { "name": "forrestchang" },
  "metadata": {
    "description": "Behavioral guidelines to reduce common LLM coding mistakes...",
    "version": "1.0.0"
  },
  "plugins": [{
    "name": "andrej-karpathy-skills",
    "source": "./",
    "description": "Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution",
    "category": "workflow"
  }]
}
```

---

### 选项 B：CLAUDE.md（按项目）

最简单的方式，适合不想用插件的场景。

**新项目（直接下载）：**

```bash
curl -o CLAUDE.md https://raw.githubusercontent.com/multica-ai/andrej-karpathy-skills/main/CLAUDE.md
```

**已有项目（追加到现有 CLAUDE.md）：**

```bash
echo "" >> CLAUDE.md
curl https://raw.githubusercontent.com/multica-ai/andrej-karpathy-skills/main/CLAUDE.md >> CLAUDE.md
```

CLAUDE.md 会被 Claude Code 等工具自动读取，无需额外配置。

---

### 选项 C：Cursor 编辑器集成（.cursor/rules）

Cursor 使用 `.mdc`（Markdown Cursor Rules）格式，支持 `alwaysApply` 自动应用。

#### 本仓库中已配置

本仓库已包含 `.cursor/rules/karpathy-guidelines.mdc`，设置了 `alwaysApply: true`：

```markdown
---
description: Behavioral guidelines to reduce common LLM coding mistakes...
alwaysApply: true
---

# Karpathy behavioral guidelines
[四条原则内容...]
```

在 Cursor 中打开本项目时自动生效，可以在 **Settings → Rules** 中确认 `karpathy-guidelines` 已出现。

#### 在其他项目中使用

1. 在项目中创建 `.cursor/rules/` 目录
2. 下载规则文件：
   ```bash
   curl -o .cursor/rules/karpathy-guidelines.mdc https://raw.githubusercontent.com/multica-ai/andrej-karpathy-skills/main/.cursor/rules/karpathy-guidelines.mdc
   ```
3. 重启 Cursor 或重新加载窗口（Ctrl+Shift+P → "Reload Window"）

Cursor 会自动识别并应用项目根目录 `.cursor/rules/` 下所有 `.mdc` 文件。

---

### 选项 D：Agent Skill 格式（个人可复用技能）

如果你想把这些准则作为个人可复用 Skill（放在 `~/.cursor/skills/` 或 Claude Code 个人技能目录），使用 `skills/karpathy-guidelines/SKILL.md`：

#### SKILL.md 格式

```markdown
---
name: karpathy-guidelines
description: Behavioral guidelines to reduce common LLM coding mistakes. Use when writing, reviewing, or refactoring code to avoid overcomplication, make surgical changes, surface assumptions, and define verifiable success criteria.
license: MIT
---

# Karpathy Guidelines

Behavioral guidelines to reduce common LLM coding mistakes...

[四条原则内容...]
```

**安装为个人 Skill：**

1. 复制 `skills/karpathy-guidelines/SKILL.md` 到你的个人技能目录
   - Cursor: `~/.cursor/skills/karpathy-guidelines/SKILL.md`
   - 或创建符号链接
2. 重启编辑器即可在所有项目中使用

**description 字段的重要性**：description 是 Skill 触发的关键，需要清晰描述在什么场景下应该激活这个 Skill。

---

## Claude Code vs Cursor 对比

| 特性 | Claude Code | Cursor |
|------|------------|--------|
| 读取文件 | 自动读取项目根 `CLAUDE.md` | 读取 `.cursor/rules/*.mdc` |
| 插件系统 | 支持，可跨项目安装 | 不支持插件，但支持 Rules |
| Skill 格式 | 通过 `.claude-plugin/` 加载 SKILL.md | 通过 `~/.cursor/skills/` 加载 |
| 默认行为 | CLAUDE.md 自动生效 | Rules 需要 `alwaysApply: true` |
| 是否读取 CLAUDE.md | ✅ 是 | ❌ 默认不读取 |
| 是否读取 .cursor/rules | ❌ 否 | ✅ 是 |

**重要**：Cursor 默认**不**读取 `CLAUDE.md` 或 `.claude-plugin/` 目录，需要通过 `.cursor/rules/` 配置。

---

## 项目定制

这些指南设计用于与项目特定指令合并。将它们添加到你现有的 `CLAUDE.md` 或 Rules 文件中。

### 添加项目特定规则

在文件末尾添加如下章节：

```markdown
## 项目特定指南

- 使用 TypeScript 严格模式
- 所有 API 端点必须有测试
- 遵循 `src/utils/errors.ts` 中现有的错误处理模式
- 提交信息遵循 Conventional Commits 规范
```

### 示例：前端项目配置

```markdown
## 项目特定指南

- 使用 React 18 + TypeScript
- 样式使用 Tailwind CSS，不要写内联样式
- 组件放在 `src/components/`，按功能模块组织
- 所有 API 调用通过 `src/api/` 层
- 状态管理使用 Zustand，不要用 Redux
- 测试使用 Vitest + React Testing Library
```

### 示例：Python 后端项目配置

```markdown
## 项目特定指南

- Python 3.11+，使用 type hints
- 遵循 PEP 8 代码风格，使用 ruff 格式化
- FastAPI 框架，Pydantic v2 做数据验证
- 数据库使用 SQLAlchemy 2.0 + Alembic 迁移
- 测试使用 pytest，放在 tests/ 目录
- 不要在代码中硬编码配置，使用环境变量
```

---

## 使用技巧

### 1. 给任务时用验收标准

| 不好的说法 | 好的说法 |
|-----------|---------|
| "写一个登录函数" | "实现用户登录，要求：1. 邮箱密码验证 2. JWT token 返回 3. 先写测试用例覆盖成功/失败/锁定场景，然后让所有测试通过" |
| "修一下这个bug" | "用户反馈列表分页第3页数据重复。先写一个能复现这个bug的测试，然后修复它让测试通过，最后跑一遍所有测试确保没有回归" |
| "重构一下这个模块" | "把用户认证相关逻辑从 `app.py` 抽出来到 `auth/` 模块，要求：1. 重构前后所有现有测试必须通过 2. 先列计划带验证点" |

### 2. 看到AI"想太多"时及时打断

如果 AI 开始：
- 写一大堆你没要求的功能
- 引入复杂的抽象层和设计模式
- 改不相关的代码

直接说："停，简化一下，只做我要求的部分" 或 "回到原则二（简约至上）"。

### 3. 用计划+验证处理复杂任务

对于超过3步的任务，要求AI先列计划：

```
请先列出分步计划，每一步带上验证方式，确认后再开始执行。
格式：
1. [步骤描述] → 验证：[怎么检查这步对不对]
2. ...
```

---

## 贡献者指南（修改原则时）

如果你修改了四条原则内容，**必须保持以下文件同步**：

| 文件 | 用途 | 必须同步 |
|------|------|---------|
| `CLAUDE.md` | Claude Code 根目录配置 | ✅ 是 |
| `.cursor/rules/karpathy-guidelines.mdc` | Cursor 规则 | ✅ 是 |
| `skills/karpathy-guidelines/SKILL.md` | 可复用 Skill | ✅ 是（发布时） |

**同步检查清单**：
- [ ] CLAUDE.md 已更新
- [ ] .cursor/rules/karpathy-guidelines.mdc 已更新（注意末尾的"These guidelines are working if"段落）
- [ ] 如发布新版本，SKILL.md 也已更新
- [ ] plugin.json 版本号已更新
- [ ] EXAMPLES.md 中的示例如有变化也已更新

---

## 如何判断它在起作用

如果你看到以下情况，说明这些指南正在发挥作用：

| 现象 | 说明 |
|------|------|
| ✅ diff 中不必要的改动更少 | 只有你请求的改动出现 |
| ✅ 澄清问题在实现之前提出 | 而不是在犯错之后 |
| ✅ 代码第一次就写得简洁 | 没有因为过度复杂而重写 |
| ✅ 干净、精简的 PR | 没有顺带的重构或"改进" |
| ✅ AI 能独立工作更长时间 | 不需要你频繁介入澄清 |

如果你看到以下情况，说明指南没有被遵守：

| 现象 | 违反的原则 |
|------|-----------|
| ❌ AI 默默做了假设没问你 | 原则一：编码前思考 |
| ❌ 代码看起来"企业级"但没必要 | 原则二：简约至上 |
| ❌ PR/diff 里有很多不相关改动 | 原则三：精确编辑 |
| ❌ 做了一半停下来等你指示 | 原则四：目标驱动 |

---

## 与其他 AI 工具的兼容性

这些原则是通用的 AI 编程行为准则，不仅适用于 Claude Code 和 Cursor，也适用于：

- **GitHub Copilot** - 可以在 `.github/copilot-instructions.md` 中添加类似规则
- **Codex CLI** - 支持项目根目录指令文件（CLAUDE.md 或类似命名）
- **Windsurf / Continue.dev 等其他 AI IDE** - 大多支持自定义指令文件
- **Trae CN 等国内 AI IDE** - 本项目（SpecWeave）已整合到 `.agents/` 规范体系

原则本身与工具无关，核心是四条行为准则。

---

## 常见问题

**Q: 这些规则会让 AI 变慢吗？**
A: 对于简单任务（如修个错别字），不会。规则明确说"对于琐碎任务请自行判断"。它主要防止复杂任务上的昂贵错误——那些浪费30分钟最后要回滚的错误。

**Q: 可以只选部分原则吗？**
A: 可以。四条原则是独立的，你可以根据团队需要选用。但建议四条一起用效果最好。

**Q: CLAUDE.md 和 .cursor/rules 可以同时用吗？**
A: 可以。它们作用于不同工具，互不冲突。如果你同时用 Claude Code 和 Cursor，建议两个都配置。

**Q: 规则太严格了怎么办？**
A: 在项目特定指南部分添加例外说明。比如"对于原型/实验性代码，可以放宽简约原则，快速验证想法"。

**Q: 个人Skill和项目CLAUDE.md冲突时怎么办？**
A: 通常项目级配置优先级高于个人全局配置。具体行为取决于你使用的工具，建议在项目特定指南中明确说明覆盖关系。
