---
id: "hermes-agent-integration-08-agents-md-autoload"
title: "08 AGENTS.md 与 .agents/ 的自动加载机制"
source: "hermes-agent 官方 Context Files 文档 + prompt_builder.py + subdirectory_hints.py + issue #14471/#502"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-integration/08-agents-md-autoload.toml"
type: "Wiki Tutorial"
description: "Hermes 如何自动加载 AGENTS.md 与 .agents/：原生单文件约定、渐进式发现、优先级、安全扫描，以及让 .agents/ 规范库被加载的方法"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Hermes 原生自动加载 AGENTS.md（启动 + 子目录渐进发现），但不会自动加载 .agents/ 目录；需通过路由地图、插件或 OKF 挂载让规范库被正确识别"
last_verified: "2026-08-09"
wiki_version: "1.0"
---

# 08 AGENTS.md 与 .agents/ 的自动加载机制

> **版本提示**
> - 本节基于 Hermes Agent 官方 **Context Files** 文档（`agent/prompt_builder.py::build_context_files_prompt()`）与 issue #14471/#502 整理
> - Hermes 的上下文文件机制为 2026 年新增能力，仍在演进；**命令与行为描述均标注"示例/需验证"**

## 8.1 核心结论（先读这个）

把 SpecWeave 接入 Hermes 时，必须理解一个不对称事实：

- **`AGENTS.md`：Hermes 原生自动加载** ✅
- **`.agents/` 目录：Hermes 不自动加载** ❌

Hermes 的上下文文件机制只认**单个 markdown 文件**（AGENTS.md / CLAUDE.md / .hermes.md / .cursorrules），**没有"目录自动扫描"能力**。`.agents/` 规范体系能否被 Hermes 正确识别，取决于你如何让它在 AGENTS.md 中被"路由"到、转成插件，或以 OKF 挂载。

## 8.2 Hermes 支持的上下文文件清单

| 文件 | 用途 | 发现方式 |
|------|------|---------|
| `.hermes.md` / `HERMES.md` | 项目指令（最高优先级） | 向上遍历至 Git 根目录 |
| **`AGENTS.md`** | 项目指令、规范、架构 | CWD 启动 + 子目录渐进发现 |
| `CLAUDE.md` | Claude Code 上下文文件（也检测） | CWD 启动 + 子目录渐进发现 |
| `SOUL.md` | 全局身份/人格（槽位 #1，独立加载） | 仅 `HERMES_HOME/SOUL.md` |
| `.cursorrules` / `.cursor/rules/*.mdc` | Cursor IDE 规范 | CWD only |

**优先级系统**：每会话仅加载**一种**项目上下文类型，首个匹配胜出：
`.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。`SOUL.md` 始终独立加载，作为 Agent 身份。

> SpecWeave 根目录已有完整 [AGENTS.md](../../../../../../AGENTS.md)，Hermes 会自动将其注入系统提示 ✅

## 8.3 AGENTS.md 的两种加载机制

### 8.3.1 启动时加载（system prompt）

会话开始时，Hermes 把 **CWD 的 AGENTS.md** 注入系统提示。加载管线：

1. **扫描工作目录**：按 `.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules` 找首个匹配
2. **读取内容**：以 UTF-8 读取整个文件
3. **安全扫描**：检测 prompt injection 模式，恶意内容被阻止
4. **截断**：超过字符上限的部分被截断

### 8.3.2 逐级子目录发现（惰性注入）

会话中，Agent 通过 `read_file` / `terminal` / `search_files` 触碰子目录时，Hermes **渐进发现**该目录的 AGENTS.md 并注入到对话（以 `[Subdirectory context discovered: ...]` 形式）：

```
my-project/
├── AGENTS.md        ← 启动时加载（system prompt）
├── frontend/AGENTS.md  ← 读 frontend/ 文件时发现
├── backend/AGENTS.md  ← 读 backend/ 文件时发现
└── shared/AGENTS.md   ← 读 shared/ 文件时发现
```

关键行为：
- **每目录每会话最多检查一次**
- **向上遍历父目录**：读 `backend/src/main.py` 会发现 `backend/AGENTS.md`，即使 `backend/src/` 无上下文文件
- 子目录上下文文件走**与启动相同的安全扫描**

### 8.3.3 为什么是"渐进发现"

Hermes 视 **per-conversation prompt caching 为神圣资源**——长会话每轮复用缓存前缀，任何中途变更 system prompt 都会使缓存失效、成倍增加成本。渐进发现避免启动时把所有子目录塞进 system prompt，从而：
- **无系统提示膨胀**（子目录提示仅在需要时出现）
- **提示缓存保留**（system prompt 跨轮稳定）

## 8.4 `.agents/` 为什么不会被自动加载（关键认知）

Hermes 的 context-files 机制**只识别单文件约定**，不递归扫描 `.agents/` 目录。原因：

- Hermes 借鉴 Claude Code 的 `CLAUDE.md` 模式（issue #502 明确对照 Cursor/Aider/Claude Code/Windsurf）
- 该模式本质是"**单文件入口**"：一个文件承载项目级规则；更细的规范靠文件内链接/引用由 Agent 主动读取，而非宿主自动展开
- `.agents/` 下的 roles/commands/scripts/skills/protocols/rules 等大量文件，**不会**自动进入 Hermes 系统提示

**推论**：SpecWeave 的 `.agents/` 能力能否被 Hermes 调用，取决于三条落地路径（见 8.5）。

## 8.5 让 `.agents/` 被 Hermes 正确识别、调用、执行的三种方法

### 方法一：路由地图（让 Agent 按需读取）— 零改造推荐

利用 AGENTS.md **自动加载** + **上下文路由表**，让 Hermes 启动即获得 `.agents/` 的导航，按需 read：

```markdown
<!-- AGENTS.md 内保持（SpecWeave 现有结构即符合） -->
# 启动协议
> 步骤 1：读取本文件全文
> 步骤 2：按「上下文路由表」读取对应规范文件 ...

## 上下文路由表
| 规范 | 入口 |
|------|------|
| 全局核心规则 | [global-core-rules.md](.agents/global-core-rules.md) |
| 上下文路由表 | [context-routing.md](.agents/context-routing.md) |
| 能力注册中心 | [capability-registry.md](.agents/capability-registry.md) |
```

效果：Hermes 启动自动注入 AGENTS.md 的启动协议 + 路由表，随后按需 `read_file` 读取 `.agents/` 下的规范。**零代码、零插件**，但依赖模型主动遵循路由表。

### 方法二：插件暴露（进 tool schema）— 高频能力

把 `.agents/commands/`、`.agents/skills/` 中的高频指令集封装为 Hermes **通用插件**（`plugin.yaml` + `register(ctx)` 注册 tools/skills/hooks）。tool schema 会随每次 API 调用进入 system prompt，**这才是"可被直接调用"的可靠通道**。

```yaml
# plugin.yaml（示例/需验证）
name: specweave-commands
version: "1.0.0"
type: general
tools:
  - name: retrospective
    description: "运行 SpecWeave 复盘指令集"
```

对应 `register(ctx)` 注册 handler，逻辑参考 [04 数据格式转换](04-data-conversion.md)。

### 方法三：OKF 记忆层挂载 — 知识库检索

把 `.agents/docs/knowledge/` 的知识库转换为 **OKF bundle**，作为 Hermes Memory Provider 挂接，使其成为可检索、跨会话持久化的记忆层。参考 [03 配置文件](03-configuration.md) 与 [04 数据格式转换](04-data-conversion.md) 的 OKF 部分。

> **三条路径可并行**：AGENTS.md 路由保证"知道规范在哪"，插件保证"高频能力可调用"，OKF 保证"知识可检索"。

## 8.6 安全边界与已知问题

- **安全扫描**：所有上下文文件（启动 + 子目录）都经过 prompt injection 扫描，恶意文件被阻止。SpecWeave 的 AGENTS.md/.agents 内容应保持规范，避免看似恶意的指令模式。
- **已知 issue #14471（P1 bug）**：post-tool-call 路径发现可能从工具参数中提取路径、扫描路径及其祖先目录的 AGENTS.md/CLAUDE.md/.cursorrules，**即使在工作区之外**，导致上下文污染/跨项目泄漏。该 bug 正待修复（修复方向：将子目录提示发现限制在活动工作区/repo 内）。
  - 影响：长运行编排 Agent 可能被外部无关 AGENTS.md 静默影响
  - 缓解：关注 Hermes 版本更新；必要时将 Hermes 启动目录限定在 SpecWeave 工作区内

## 8.7 落地检查清单

- [ ] 根目录 AGENTS.md 存在且为启动协议 + 上下文路由表结构（Hermes 启动自动注入）
- [ ] 未在根目录放置 `.hermes.md`（否则优先级高于 AGENTS.md，SpecWeave 契约不生效）
- [ ] `.agents/` 高频指令集已封装为通用插件（tool schema）
- [ ] 知识库已转换为 OKF bundle 并挂接为 Memory Provider（如需持久化记忆）
- [ ] AGENTS.md 内容通过安全扫描（无恶意注入模式）
- [ ] 已关注 #14471 的 workspace 隔离修复状态

## 8.8 参考与交叉引用

- [Hermes Agent Context Files 官方文档](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/context-files.md)（需验证）
- [Hermes issue #14471：越权注入无关 AGENTS.md](https://github.com/NousResearch/hermes-agent/issues/14471)
- [Hermes issue #502：Project Context System](https://github.com/NousResearch/hermes-agent/issues/502)
- [01 插件接口规范](01-hermes-plugin-interface.md) — 方法二依赖
- [03 配置文件](03-configuration.md) — 方法三依赖
- [04 数据格式转换](04-data-conversion.md) — 方法二/三依赖
- [SpecWeave AGENTS.md](../../../../../../AGENTS.md) — 启动协议与路由表

---

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [07 常见问题](07-troubleshooting.md) | [README](./README.md) | （无，末章） |
