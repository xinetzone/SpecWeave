---
type: Reference
title: mobile-use 源码
description: minitap-mobile-use 3.6.3 源码仓库登记，包含核心模块文件清单、依赖与许可证信息
tags: [mobile-use, minitap, source, reference]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: pending, at: pending }
status: draft
stale_after: 2027-08-23
sources:
  - id: facts
    resource: "/references/facts.md"
    title: mobile-use 事实清单
---

# mobile-use 源码

## 仓库信息

| 属性 | 值 |
|------|-----|
| 包名 | `minitap-mobile-use` |
| 版本 | `3.6.3` |
| 许可证 | Apache-2.0 |
| Python 要求 | `>=3.12` |
| 描述 | AI-powered multi-agent system that automates real Android and iOS devices through low-level control using LangGraph. |
| 仓库地址 | https://github.com/minitap-ai/mobile-use |
| Homepage | https://minitap.ai/ |
| 构建后端 | `uv_build>=0.7.20,<0.8.0` |
| 模块名 | `minitap.mobile_use` |
| CLI 入口 | `mobile-use = "minitap.mobile_use.main:cli"` |
| 作者 | Pierre-Louis Favreau, Jean-Pierre Lo, Nicolas Dehandschoewercker |

## 核心依赖

| 依赖 | 版本约束 | 用途 |
|------|---------|------|
| `langgraph` | `>=1.0.2,<2.0.0` | 多 Agent 状态图工作流框架 |
| `langchain` | `>=1.0.0` | LLM 应用框架 |
| `langchain-core` | `>=1.0.0` | LangChain 核心抽象 |
| `adbutils` | `==2.9.3` | Android ADB 客户端 |
| `uiautomator2` | `>=3.5.0` | Android UI 自动化 |
| `facebook-wda` | `>=1.5.4` | iOS WebDriverAgent 客户端 |
| `fb-idb` | `>=1.1.7` | iOS 模拟器 IDB 客户端 |
| `Appium-Python-Client` | `>=5.0.0` | Appium 客户端（可选后端） |
| `pydantic-settings` | `==2.10.1` | 环境变量配置管理 |
| `typer` | `==0.16.0` | CLI 框架 |
| `jinja2` | `==3.1.6` | Agent prompt 模板渲染 |
| `python-dotenv` | `==1.1.1` | .env 文件加载 |
| `posthog` | `>=7.4.2` | 遥测数据采集 |
| `limrun-api` | `>=0.1.0` | Limrun 云设备 API |
| `websockets` | `>=12.0` | WebSocket 通信（ADB 隧道） |
| `httpx` | `>=0.28.1` | 异步 HTTP 客户端 |

### LLM 提供商依赖

| 依赖 | 版本约束 | 提供商 |
|------|---------|--------|
| `langchain-openai` | `>=1.0.0` | OpenAI / Minitap 代理 / OpenRouter |
| `langchain-google-genai` | `>=4.0.0` | Google Gemini |
| `langchain-google-vertexai` | `>=3.0.0` | Google Vertex AI |
| `langchain-anthropic` | `>=1.0.0` | Anthropic Claude |
| `langchain-azure-ai` | `>=1.1.1` | Azure AI |
| `langchain-cerebras` | `>=0.8.0` | Cerebras |
| `langchain-mcp-adapters` | `>=0.2.0` | MCP 工具适配 |

## 关键源文件清单

源码根路径：`d:\AI\.chaos\libs\mobile-use\minitap\mobile_use\`

### 入口与配置

| 文件路径 | 职责 |
|---------|------|
| `main.py` | Typer CLI 入口，定义 `app`、`DeviceType`、`run_automation()`、`cli()` |
| `config.py` | `Settings`、`LLM`、`LLMWithFallback`、`LLMConfig`、配置加载与验证函数 |
| `context.py` | `MobileUseContext`、`DeviceContext`、`DevicePlatform`、`ExecutionSetup` |
| `constants.py` | `RECURSION_LIMIT=400`、`MAX_MESSAGES_IN_HISTORY=25` 等常量 |

### Agent 节点（`agents/`）

| 文件路径 | 职责 |
|---------|------|
| `agents/planner/planner.py` | `PlannerNode`：将目标分解为 Subgoal 列表 |
| `agents/planner/types.py` | `Subgoal`、`SubgoalStatus`、`PlannerOutput` 等类型 |
| `agents/orchestrator/orchestrator.py` | `OrchestratorNode`：子目标状态推进与重规划决策 |
| `agents/cortex/cortex.py` | `CortexNode`：核心决策，基于截图和 UI 层级产出结构化决策 |
| `agents/executor/executor.py` | `ExecutorNode`：绑定工具，生成 tool_calls |
| `agents/executor/tool_node.py` | `ExecutorToolNode`：顺序执行工具调用，失败中止 |
| `agents/contextor/contextor.py` | `ContextorNode`：采集屏幕数据、前台应用、设备日期 |
| `agents/summarizer/summarizer.py` | `SummarizerNode`：消息历史裁剪（无 LLM） |
| `agents/hopper/hopper.py` | `hopper()` 异步函数：从数据中提取信息 |
| `agents/outputter/outputter.py` | `outputter()` 异步函数：生成最终结构化输出 |
| `agents/video_analyzer/video_analyzer.py` | `analyze_video()` 异步函数：Gemini 视频内容分析 |

### 图结构（`graph/`）

| 文件路径 | 职责 |
|---------|------|
| `graph/graph.py` | `get_graph()` 构建 LangGraph，节点注册、边定义、条件门 |
| `graph/state.py` | `State` Pydantic 模型、`take_last`/`merge_dicts` reducer、`asanitize_update()` |

### 设备控制（`controllers/`）

| 文件路径 | 职责 |
|---------|------|
| `controllers/device_controller.py` | `MobileDeviceController` Protocol、`ScreenDataResponse` |
| `controllers/android_controller.py` | `AndroidDeviceController`：ADB + uiautomator2 实现 |
| `controllers/ios_controller.py` | `iOSDeviceController`：IDB/WDA 适配实现 |
| `controllers/controller_factory.py` | `create_device_controller()` / `get_controller()` 工厂函数 |
| `controllers/unified_controller.py` | `UnifiedMobileController`：高级操作门面 |
| `controllers/types.py` | `Bounds`、`CoordinatesSelectorRequest`、`PercentagesSelectorRequest`、`SwipeRequest` 等 |
| `controllers/limrun_controller.py` | `LimrunAndroidController`、`LimrunIosController`：云设备控制器 |

### 工具系统（`tools/`）

| 文件路径 | 职责 |
|---------|------|
| `tools/tool_wrapper.py` | `ToolWrapper`、`CompositeToolWrapper` 数据类 |
| `tools/index.py` | `EXECUTOR_WRAPPERS_TOOLS`（15 个工具）、`VIDEO_RECORDING_WRAPPERS`、工具获取函数 |
| `tools/types.py` | `Target` 等工具参数类型 |
| `tools/mobile/tap.py` | `tap` 工具：三级回退定位（bounds/resource_id/text） |
| `tools/mobile/swipe.py` | `swipe` 工具 |
| `tools/mobile/back.py` | `back` 工具（返回键） |
| `tools/mobile/open_link.py` | `open_link` 工具 |
| `tools/mobile/launch_app.py` | `launch_app` 工具 |
| `tools/mobile/stop_app.py` | `stop_app` 工具 |
| `tools/mobile/focus_and_input_text.py` | `focus_and_input_text` 工具 |
| `tools/mobile/focus_and_clear_text.py` | `focus_and_clear_text` 工具 |
| `tools/mobile/erase_one_char.py` | `erase_one_char` 工具 |
| `tools/mobile/press_key.py` | `press_key` 工具 |
| `tools/mobile/wait_for_delay.py` | `wait_for_delay` 工具 |
| `tools/mobile/long_press_on.py` | `long_press_on` 工具 |
| `tools/mobile/video_recording.py` | `start_video_recording`/`stop_video_recording` 工具 |
| `tools/scratchpad.py` | `save_note`、`read_note`、`list_notes` 草稿工具 |

### 客户端层（`clients/`）

| 文件路径 | 职责 |
|---------|------|
| `clients/ui_automator_client.py` | `UIAutomatorClient`：uiautomator2 封装 |
| `clients/wda_client.py` | `WdaClientWrapper`：facebook-wda 封装（物理 iOS） |
| `clients/idb_client.py` | `IdbClientWrapper`：fb-idb 封装（iOS 模拟器） |
| `clients/ios_client.py` | `IosClientWrapper` 抽象、`get_ios_client()` 工厂 |
| `clients/adb_tunnel.py` | `AdbTunnel`：WebSocket 桥接远程 ADB |
| `clients/limrun_client.py` | Limrun 云设备 API 客户端 |
| `clients/limrun_factory.py` | Limrun 实例创建/销毁工厂 |
| `clients/browserstack_client.py` | BrowserStack 云设备客户端 |
| `clients/ios_client_config.py` | `WdaClientConfig`、`IdbClientConfig`、`IosClientConfig` |

### SDK 层（`sdk/`）

| 文件路径 | 职责 |
|---------|------|
| `sdk/agent.py` | `Agent` 类：核心入口，生命周期管理，本地/云双路径 |
| `sdk/builders/index.py` | `Builders` 命名空间单例（`BuildersWrapper`） |
| `sdk/builders/agent_config_builder.py` | `AgentConfigBuilder`：流式配置构建器 |
| `sdk/builders/task_request_builder.py` | `TaskRequestBuilder`：任务请求构建器 |
| `sdk/types/agent.py` | `AgentConfig`、`LimrunConfig`、`ServerConfig`、`ApiBaseUrl` |
| `sdk/types/task.py` | `TaskRequest`、`PlatformTaskRequest`、`Task`、`TaskResult`、`AgentProfile` |
| `sdk/services/cloud_mobile.py` | `CloudMobileService`：云手机远程执行 |
| `sdk/services/platform.py` | `PlatformService`：Minitap 平台 API |

### 服务层（`services/`）

| 文件路径 | 职责 |
|---------|------|
| `services/llm.py` | `get_llm()`、`with_fallback()`、9 个提供商工厂函数 |
| `services/accessibility.py` | `get_accessibility_tree()`：ADB uiautomator dump |
| `services/telemetry.py` | PostHog 遥测，同意管理 |

### 项目配置文件

| 文件路径 | 职责 |
|---------|------|
| `pyproject.toml` | 项目元数据、依赖、ruff/pytest 配置 |
| `llm-config.defaults.jsonc` | 默认 LLM 配置（default/minimax/recommended 三组预设） |
| `llm-config.override.template.jsonc` | 用户覆盖配置模板 |
| `README.md` | 项目说明 |
| `LICENSE` | Apache-2.0 许可证全文 |
| `Dockerfile` / `slim.Dockerfile` | 容器构建定义 |
