# Concepts

- [01 项目介绍与背景](01-introduction-background.md) — 介绍 DeepSeek Harness 项目背景、Agent=Model+Harness 核心理念、发布增长数据、竞品对比与战略定位。
- [02 环境准备与安装](02-installation-setup.md) — 讲解 dsh 环境准备（Node.js 版本要求）、API Key 获取、npx 一键启动、源码构建、配置目录与 Windows 兼容性说明。
- [03 快速上手：第一个任务](03-quickstart-first-task.md) — 引导完成 Web UI 工作区选择、模型配置、第一个 Agent 任务执行，介绍权限审批、实时统计面板与 Trajectory 轨迹按钮。
- [04 四种运行模式](04-four-modes.md) — 详解 Standard、Code(PTC)、Minimal、Creator 四种运行模式的能力差异、适用场景与启动方式。
- [05 核心架构：一切皆插件](05-architecture-everything-plugin.md) — 深入解读一切皆插件设计哲学、Cordis 元框架五概念、可逆效应、Bundle/Profile 机制与五层叠加架构。
- [06 Agent 循环与事件模型](06-agent-loop-events.md) — 解析 Agent 循环 Turn/Step 精确定义、官方时序图、三类事件分发模式与模型可见即已记录不变量。
- [07 会话日志与可观测性](07-session-log-observability.md) — 介绍 append-only SessionEvent 流、deriveMessages 投射机制、Trajectory 轨迹视图、Fork/Resume/Replay 调试功能。
- [08 模型配置与多模型支持](08-model-configuration.md) — 详解 DeepSeek V4 Pro/Flash 默认参数、三档思考强度、凭证安全存储、多 Provider 添加与自定义 Provider 配置。
- [09 工具系统与 Capability Seam](09-tools-capability-seam.md) — 阐述工具系统与 Capability Seam 抽象，Service Definition、Provider、Consumer 三角色模型与一次替换全局生效机制。
- [10 插件开发入门](10-plugin-development.md) — 插件开发入门，涵盖三种插件形态、依赖注入、五种事件分发模式、自定义工具示例、可逆效应与 Creator 模式热重载。
- [11 与 Claude Code/Codex/MCP 生态互操作](11-ecosystem-interop.md) — 介绍 dsh 与 Claude Code hooks 桥接、Codex 一键配置、MCP 客户端支持、AGENTS.md 规则读取与任务委托共存策略。
- [12 无头模式与 SDK 使用](12-headless-sdk.md) — 讲解无头模式一次性执行、Python SDK（自带 Node 运行时）、JSON-RPC 跨语言通信、ACP 服务端与嵌入应用场景。
- [14 适用场景与风险提示](14-use-cases-limitations.md) — 提供适用与不适用场景决策表、v0.1 预览版八大风险声明、Windows 平台限制与版本跟踪升级建议。

```{toctree}
:maxdepth: 2

01-introduction-background
02-installation-setup
03-quickstart-first-task
04-four-modes
05-architecture-everything-plugin
06-agent-loop-events
07-session-log-observability
08-model-configuration
09-tools-capability-seam
10-plugin-development
11-ecosystem-interop
12-headless-sdk
14-use-cases-limitations
```