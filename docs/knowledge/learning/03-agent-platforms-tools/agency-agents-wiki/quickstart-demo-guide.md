---
id: agency-agents-wiki-quickstart-demo-guide
title: "The Agency 完全指南 — 新开发者快速上手演示"
source: "https://github.com/msitarzewski/agency-agents"
date: "2026-08-05"
category: "learning"
tags: ["agency-agents", "the-agency", "quickstart", "demo", "new-developer", "get-started", "tutorial"]
---

# The Agency 完全指南 — 新开发者快速上手演示

> 一句话摘要：这是一份面向新开发者的**可复制粘贴**的分步演示教程。它会带你从零开始——先自动检测你本机装了哪款 AI 编程工具，再据此一步步克隆仓库、预览 Agent、安装到你常用的工具、激活第一个 Agent，最后用一个 5 人小团队跑通一个最小 MVP 场景。全程约 10 分钟。

---

## 1. 这个演示要带你完成什么

| 阶段 | 你将要做的 | 对应 wiki 章节 |
|------|-----------|--------------|
| ① 环境自检 | 检测本机已装的 AI 工具 | [00 概述](00-overview.md) |
| ② 克隆仓库 | 把 The Agency 拉到本地 | [01 文件夹架构](01-architecture.md) |
| ③ 预览 | 看看有哪些部门与 Agent | [03 部门名册](03-roster-divisions.md) |
| ④ 安装 | 把 Agent 装到你常用的工具 | [04 脚本体系](04-scripts-tooling.md) |
| ⑤ 激活 | 在会话中喊出第一个 Agent | [06 使用示例](06-usage-examples.md) |
| ⑥ 演示 | 用 5 个 Agent 跑通一个小任务 | [07 策略与运行手册](07-strategy-playbooks.md) |

> **适用对象**：从未用过 The Agency、但用过任意一款 AI 编程工具（Claude Code / Cursor / Codex / Gemini CLI / OpenCode 等）的开发者。全程只需要命令行 + 一个 AI 工具，不需要额外的服务器或运行时。

---

## 2. 前置条件与自动检测

### 2.1 你只需要两样东西

1. **Git**——用来克隆仓库。检查是否已安装：
   ```bash
   git --version
   # 期望输出：git version x.y.z
   ```

2. **任意一款 AI 编程工具**——The Agency 支持 16 种。检查本机已装了哪些：
   ```bash
   for t in claude cursor codex gemini opencode kimi qwen windsurf aider; do
     command -v "$t" >/dev/null 2>&1 && echo "✓ 已检测到: $t"
   done
   ```

   > 如果上面**一行都没输出**，说明你还没装任何受支持的 AI 工具。最简单的办法是装 [Claude Code](https://claude.com/claude-code)（原生支持 `.md` Agent、免转换），或直接用 The Agency 的[桌面应用](https://agencyagents.app)（零命令行）。

### 2.2 工具 → 安装方式映射（记住这张表）

The Agency 的 16 种工具按"是否需要转换"分两类，这决定了下面的安装步骤：

| 是否需要转换 | 工具 | 含义 |
|-------------|------|------|
| **免转换（identity）** | Claude Code、GitHub Copilot | 源 `.md` 文件即目标格式，`install.sh` 直接复制 |
| **需转换** | Cursor、Codex、Gemini CLI、OpenCode、Aider、Windsurf、Qwen、Kimi、Osaurus、Antigravity、OpenClaw、Hermes、Vibe、ZCode | 先 `convert.sh` 生成格式，再 `install.sh` 安装 |

> 记住口诀：**Claude Code / Copilot 免转换，其余先转再装**。

---

## 3. 步骤 1：克隆并进入仓库

```bash
git clone https://github.com/msitarzewski/agency-agents.git
cd agency-agents
```

> 验证：`ls` 应该能看到 `divisions.json`、`tools.json`、`scripts/`、各部门目录（`engineering/`、`design/`、`marketing/` 等）。

---

## 4. 步骤 2：预览——先别急着装

安装前花 30 秒看看"名册"里有什么，避免盲目全量安装（230+ Agent 会占用大量上下文）。

```bash
# 查看有哪些部门（team）以及每个部门的 Agent 数量
./scripts/install.sh --list teams

# 查看所有 Agent（数量较多，可配合 grep 过滤）
./scripts/install.sh --list agents | head -20

# 查看支持哪些工具
./scripts/install.sh --list tools
```

> **关键建议**：**按需安装**，不要一次全装。优先用一个部门（如 `engineering`）开练。这是 wiki 里反复强调的最佳实践——装太多会让 AI 助手"选择困难"，精度反而下降。

---

## 5. 步骤 3：按检测到的工具安装

根据第 2.1 步检测到的工具，走对应的分支。

### 分支 A：你装了 Claude Code（免转换，最推荐给新手）

```bash
# 只把 engineering 部门装到 Claude Code（按需，不贪多）
./scripts/install.sh --tool claude-code --division engineering
```

> 装完即可用，无需运行 `convert.sh`。可立刻跳到**步骤 4 激活**。

### 分支 B：你装的是 Cursor / Codex / Gemini CLI 等需转换的工具

其他工具要走"先转再装"双步流程：

```bash
# 第一步：为你的工具生成集成文件（以 cursor 为例）
./scripts/install.sh --tool cursor --division engineering

# 若提示"找不到转换产物 / 不生效"，先手动补一次转换，再安装
./scripts/convert.sh --tool cursor
./scripts/install.sh --tool cursor --division engineering
```

> 上面的 `install.sh` 在发现转换产物缺失时会**自动调用 `convert.sh` 补齐**，所以多数情况下一条命令即可。若你装了多个工具，也可以先全量转换再指定安装：
> ```bash
> ./scripts/convert.sh --parallel --jobs 8          # 全量转换所有工具
> ./scripts/install.sh --tool cursor,codex          # 只装指定的两个
> ```

### 分支 C：你用的是 OpenCode（注意 119 上限）

OpenCode 上游有个已知 bug，运行时只注册约 **119 个** Agent，超出会静默丢弃：

```bash
# 务必用 --division 安装子集，保持在 119 上限内
./scripts/install.sh --tool opencode --division engineering --dry-run   # 先预览
./scripts/install.sh --tool opencode --division engineering              # 确认后安装
```

### 进阶：预览与安全安装

```bash
# 任何工具都可以先 --dry-run 预览，确认无误再真装
./scripts/install.sh --tool claude-code --division engineering --dry-run

# 非交互 + 并行（适合脚本 / CI）
./scripts/install.sh --no-interactive --parallel --jobs 4

# 软链接安装（源文件更新自动同步）
./scripts/install.sh --tool claude-code --link
```

---

## 6. 步骤 4：激活第一个 Agent

安装完成后，在你常用的 AI 工具会话中用**自然语言点名**即可激活。给 Agent 的指令越具体，输出越可靠——建议包含"**Agent + 目标 + 上下文 + 交付物**"四要素。

| 工具 | 激活示例 |
|------|---------|
| **Claude Code** | `Use the Frontend Developer agent to review my React component and suggest improvements.` |
| **Cursor** | `Use the @engineering-frontend-developer rules to review this code.` |
| **OpenCode** | `@engineering-backend-architect design the API for this todo app.` |
| **Gemini / Antigravity** | `@agency-frontend-developer review this React component` |

**第一个 Agent 最小演示**（以 Claude Code 为例）：

```text
Use the Frontend Developer agent to:
- Target: build a responsive landing page for my SaaS product
- Context: use the brand colors in design/brand.md
- Deliverable: a working React component with a summary of what was built
```

> **验证安装是否成功**：当你能在会话中像上面这样点名并得到符合 Agent 档案风格的回应，就说明安装生效了。

---

## 7. 步骤 5：验证安装

```bash
# 检查 Claude Code 目录里装了多少个 Agent 文件
ls ~/.claude/agents/ | wc -l

# 检查 Cursor 规则目录
ls .cursor/rules/ | head

# 更直接的验证：在会话里实际点名一个 Agent，看能否被识别
```

> 若文件已就位但会话里"喊不出来"，多半是**文件名与引用名不一致**——确认引用的是 Agent 的 `name`/slug（如 `frontend-developer`），而非文件路径。

---

## 8. 步骤 6：5 人小团队跑通一个 MVP 演示

这是"组合 > 单打独斗"的最小演示。用一个"build a startup MVP"场景，把不同部门的 Agent 串成流水线（在支持多 Agent 的会话中依次激活）：

| 顺序 | Agent | 分工 |
|------|-------|------|
| 1 | `Rapid Prototyper` | 快速验证核心假设，产出原型 |
| 2 | `Backend Architect` | 设计 API 与数据库 schema |
| 3 | `Frontend Developer` | 按架构实现 React UI |
| 4 | `Growth Hacker`（并行） | 规划用户获取策略 |
| 5 | `Reality Checker` | 上线前质量审查（默认给出 NEEDS WORK，需证据才放行） |

```text
1) Activate Rapid Prototyper and build a working prototype of my MVP idea in 3 days.
2) Activate Backend Architect to design the API and database schema for the validated prototype.
3) Activate Frontend Developer to build the React UI following the architecture spec.
4) In parallel, activate Growth Hacker to plan a user acquisition strategy.
5) Before launch, activate Reality Checker to verify production readiness.
```

> 更多开箱即用的团队组合见 wiki [06 使用示例](06-usage-examples.md) 第 8 节，以及 `examples/` 目录下的 `workflow-*.md`。

---

## 9. 常见问题速查（新手最容易踩的坑）

| 现象 | 原因 | 解决 |
|------|------|------|
| 提示"找不到 convert / install 脚本" | 未在仓库根目录执行 | 先 `cd agency-agents` 再运行 `./scripts/...` |
| 装了 Cursor/Codex/Gemini 但不生效 | 未先 `convert.sh` | 先 `./scripts/convert.sh --tool <name>`，再 `install.sh` |
| OpenCode 只有约 119 个 Agent | 上游 bug（issue #27988） | 用 `--division` 装子集，保持在限内 |
| 会话里喊不出 Agent | 文件名与引用名不一致 | 引用 `name`/slug，而非路径 |
| 上下文不够用 | 装太多 Agent | 只装 `--division`/`--agent` 子集 |
| 改了 Agent 后没变化 | 修改后未重新 convert | 重跑 `./scripts/convert.sh` |

> 完整排查流程见 wiki [08 常见问题解答](08-faq-troubleshooting.md)。

---

## 10. 下一步与资源

**一两分钟内你还想做的**：
- 完整阅读本教程，从 [00 概述](00-overview.md) 开始按学习路径走。
- 想团队落地？看 [09 最佳实践](09-best-practices.md) 的"团队落地"章节与 [07 策略与运行手册](07-strategy-playbooks.md) 的 NEXUS 策略。
- 想自定义 Agent？学 [02 Agent 文件格式](02-agent-format.md)，或浏览各部门目录参考现成档案。

**核心资源**：
- 官方仓库：[github.com/msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)
- 桌面应用（零命令行）：[agencyagents.app](https://agencyagents.app)
- 社区讨论：[GitHub Discussions](https://github.com/msitarzewski/agency-agents/discussions)

> 🎭 你已经能从"装好几个专家"到"让专家组队干活"了。剩下的，就是挑一个真实小任务，把这 5 步再走一遍。