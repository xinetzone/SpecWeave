---
type: Concept
title: mobile-use 项目概览
description: minitap-mobile-use 3.6.3 的定位、功能特性、CLI 用法、核心依赖与模块架构总览
tags: [mobile-use, minitap, overview, cli, langgraph, android, ios]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: mobile-use-source
    resource: "/references/mobile-use-source.md"
    title: mobile-use 源码
  - id: facts
    resource: "/references/facts.md"
    title: mobile-use 事实清单
---

# mobile-use 项目概览

mobile-use（包名 `minitap-mobile-use`，版本 `3.6.3`）是一个基于 LangGraph 构建的开源 AI 多智能体系统，通过底层控制实现真实 Android 和 iOS 设备的自然语言自动化。用户只需用自然语言描述目标（如"在设置中打开蓝牙并截屏"），系统即可自主完成 UI 导航、元素定位、文本输入、手势操作等一系列动作。项目声称在 AndroidWorld benchmark 上达到 100% 完成率。

## 项目定位

mobile-use 的核心设计理念是**低层控制 + 多 Agent 分层认知**。与 Appium 等传统自动化框架不同，它不依赖独立的 Server 进程，而是在进程内直接通过 adbutils、uiautomator2、facebook-wda、fb-idb 等库与设备通信。AI 部分由 LangGraph 状态图驱动，9 个 Agent 节点按"规划→编排→感知→决策→执行"分层协作，每个节点可独立配置不同的 LLM 模型和提供商。

项目要求 Python `>=3.12`，采用 Apache-2.0 许可证，仓库托管于 GitHub（https://github.com/minitap-ai/mobile-use），主页为 https://minitap.ai/。

## 核心功能

- **自然语言控制**：用户以自然语言描述目标，Agent 自主拆解为子目标并逐步执行 [F-011]
- **跨平台支持**：Android（ADB + uiautomator2）和 iOS（WDA 物理设备 / IDB 模拟器）统一抽象 [F-100~F-112]
- **多设备模式**：本地 USB/Wi-Fi 设备、Limrun 云设备、BrowserStack、Minitap 云手机四种模式 [F-213]
- **UI 感知自动化**：实时获取 UI 层级（accessibility tree）和截图，LLM 基于视觉信息决策 [F-065]
- **数据抓取**：通过 scratchpad 工具（save_note/read_note/list_notes）在执行过程中持久化信息 [F-151]
- **可扩展 LLM 配置**：9 个提供商（OpenAI、Google、Anthropic、Vertex AI、OpenRouter、xAI、Azure、MiniMax、Minitap），每节点独立模型 + fallback [F-030][F-173]
- **结构化输出**：支持 Pydantic 模型或 JSON schema 定义输出格式 [F-044][F-072]
- **视频分析**：可选的视频录制工具，结合 Gemini 视觉模型分析动态屏幕内容 [F-073][F-143]
- **Trace 录制**：完整记录 Agent 思考过程、工具调用和截图，支持 GIF 生成 [F-219]

## CLI 用法

CLI 入口为 `mobile-use`，通过 Typer 框架定义。基本用法：

```bash
mobile-use "打开设置并连接到 Wi-Fi 网络 MyWiFi"
```

CLI 仅注册一个 `main` 命令，`goal` 为必填位置参数。常用选项包括：

| 选项 | 简写 | 用途 |
|------|------|------|
| `--test-name` | `-n` | 测试名称，提供时启用 trace 录制 |
| `--traces-path` | `-p` | Trace 保存路径（默认 `traces`） |
| `--output-description` | `-o` | 输出描述（JSON schema 形式） |
| `--with-video-recording-tools` | | 启用视频录制工具（需 ffmpeg） |
| `--device-type` | `-d` | 设备类型：`local`（默认）或 `limrun` |
| `--limrun-platform` | | Limrun 平台：`android` 或 `ios` |
| `--wda-url` | | 覆盖 WebDriverAgent URL |
| `--idb-host` / `--idb-port` | | IDB companion 连接配置 |

CLI 启动时首先提示遥测同意（首次运行），然后初始化 PostHog 遥测，执行命令后关闭遥测会话 [F-026]。遥测可通过环境变量 `MOBILE_USE_TELEMETRY_ENABLED=false` 禁用。

## 核心运行时依赖

mobile-use 的依赖可分为四组：

**Agent 框架**：`langgraph>=1.0.2`（状态图工作流）、`langchain>=1.0.0`、`langchain-core>=1.0.0`（LLM 抽象与工具绑定）、`jinja2==3.1.6`（prompt 模板渲染）。

**设备控制**：`adbutils==2.9.3`（Android ADB）、`uiautomator2>=3.5.0`（Android UI 自动化）、`facebook-wda>=1.5.4`（iOS WDA）、`fb-idb>=1.1.7`（iOS 模拟器）、`Appium-Python-Client>=5.0.0`（可选后端）。

**LLM 提供商**：langchain-openai、langchain-google-genai、langchain-google-vertexai、langchain-anthropic、langchain-azure-ai、langchain-cerebras，共覆盖 9 个提供商。

**基础设施**：`pydantic-settings==2.10.1`（配置）、`typer==0.16.0`（CLI）、`httpx>=0.28.1`（HTTP 客户端）、`posthog>=7.4.2`（遥测）、`limrun-api>=0.1.0`（云设备）、`websockets>=12.0`（ADB 隧道）。

## 模块架构

Python 包 `minitap/mobile_use/` 包含以下模块群：

- **入口层**：`main.py`（CLI）、`config.py`（LLM 配置）、`context.py`（上下文对象）、`constants.py`
- **Agent 层**（`agents/`）：7 个图节点（planner、orchestrator、cortex、executor、contextor、summarizer、executor/tool_node）+ 3 个工具函数（hopper、outputter、video_analyzer），每个 Agent 有独立的 `.py` 逻辑、`types.py` 类型和 `.md` prompt 模板
- **图结构层**（`graph/`）：`graph.py`（工作流定义）、`state.py`（状态模型与 reducer）
- **设备控制层**（`controllers/`）：Protocol 抽象、Android/iOS 实现、工厂函数、UnifiedController 门面
- **工具层**（`tools/`）：15 个 mobile 工具 + 3 个 scratchpad 工具 + 2 个视频工具，通过 ToolWrapper 注册
- **客户端层**（`clients/`）：ADB、uiautomator2、WDA、IDB、Limrun、BrowserStack、ADB WebSocket 隧道
- **SDK 层**（`sdk/`）：Agent 类、Builders 流式构建器、Task/TaskRequest 类型、CloudMobileService
- **服务层**（`services/`）：LLM 工厂与 fallback、accessibility tree 获取、PostHog 遥测

## 配置体系

mobile-use 的配置分三层：

1. **环境变量**（`.env` 文件）：8 个 API Key（OPENAI_API_KEY、GOOGLE_API_KEY、ANTHROPIC_API_KEY 等）、ADB 主机端口、遥测开关、Minitap 平台地址 [F-027~F-029]
2. **LLM 配置文件**：`llm-config.defaults.jsonc`（内置三组预设：default/minimax/recommended）和可选的 `llm-config.override.jsonc`（用户覆盖，深度合并） [F-013][F-042]
3. **SDK 构建器**：通过 `AgentConfigBuilder` 在代码中流式配置设备、profile、视频工具等 [F-229]

默认配置中，planner/orchestrator/contextor/executor 使用 `openai/gpt-5-nano`（fallback `gpt-5-mini`），cortex 使用 `openai/gpt-5`（fallback `o4-mini`） [F-014]。

## 相关概念

- [多 Agent 协作架构](/concepts/01-multi-agent-architecture.md)
- [设备控制抽象层](/concepts/02-device-control.md)
- [工具系统与执行节点](/concepts/03-tools-system.md)
- [LLM 配置与可插拔体系](/concepts/04-llm-configuration.md)
- [SDK 双层 API 与生命周期](/concepts/05-sdk-layer.md)
- [图结构与状态管理](/concepts/06-graph-state.md)
