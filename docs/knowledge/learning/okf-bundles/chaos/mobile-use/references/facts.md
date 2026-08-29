# mobile-use 事实清单

> R阶段事实采集。源码路径：d:\AI\.chaos\libs\mobile-use\
> 采集日期：2026-08-23

## 项目元信息

- F-001: 项目名称为 `minitap-mobile-use`，版本 `3.6.3`，描述为 "AI-powered multi-agent system that automates real Android and iOS devices through low-level control using LangGraph."（`pyproject.toml:2-4`）
- F-002: 作者为 Pierre-Louis Favreau、Jean-Pierre Lo、Nicolas Dehandschoewercker（`pyproject.toml:8-12`）
- F-003: 要求 Python 版本 `>=3.12`（`pyproject.toml:14`）
- F-004: 核心依赖包括 `langgraph>=1.0.2,<2.0.0`、`adbutils==2.9.3`、`langchain>=1.0.0`、`langchain-core>=1.0.0`、`pydantic-settings==2.10.1`、`typer==0.16.0`、`uiautomator2>=3.5.0`、`fb-idb>=1.1.7`、`facebook-wda>=1.5.4`、`Appium-Python-Client>=5.0.0`、`posthog>=7.4.2`、`limrun-api>=0.1.0`、`websockets>=12.0`（`pyproject.toml:16-47`）
- F-005: LLM 提供商依赖包括 `langchain-google-genai>=4.0.0`、`langchain-anthropic>=1.0.0`、`langchain-openai>=1.0.0`、`langchain-cerebras>=0.8.0`、`langchain-google-vertexai>=3.0.0`、`langchain-azure-ai>=1.1.1`、`langchain-mcp-adapters>=0.2.0`（`pyproject.toml:19-46`）
- F-006: CLI 入口点为 `mobile-use = "minitap.mobile_use.main:cli"`（`pyproject.toml:58`）
- F-007: 构建系统使用 `uv_build>=0.7.20,<0.8.0`，模块名为 `minitap.mobile_use`（`pyproject.toml:64-70`）
- F-008: 代码风格工具为 ruff，行宽 100，缩进 4 空格，目标 Python 3.12，启用规则 `E`、`F`、`TID`、`UP`，禁止相对导入（`pyproject.toml:72-123`）
- F-009: 测试框架为 pytest，测试路径为 `minitap` 和 `tests`，支持 `ios_simulator`、`android`、`integration` 标记（`pyproject.toml:138-171`）
- F-010: 项目主页 `https://minitap.ai/`，源码仓库 `https://github.com/minitap-ai/mobile-use`（`pyproject.toml:61-62`）
- F-011: README 声明项目为开源 AI agent，通过自然语言控制 Android 或 iOS 设备，支持自然语言控制、UI 感知自动化、数据抓取、可扩展 LLM 配置（`README.md:1,31,35-40`）
- F-012: 项目声称在 AndroidWorld benchmark 上达到 100% 完成率（`README.md:50`）
- F-013: 默认 LLM 配置文件 `llm-config.defaults.jsonc` 包含三组预设：`default`（OpenAI）、`minimax`（MiniMax）、`recommended`（Minitap 平台）（`llm-config.defaults.jsonc:3,76,139`）
- F-014: 默认配置中 planner/orchestrator/executor/contextor 使用 `openai/gpt-5-nano`（fallback `gpt-5-mini`），cortex 使用 `openai/gpt-5`（fallback `o4-mini`）（`llm-config.defaults.jsonc:4-43`）
- F-015: 推荐配置使用 minitap 提供商，cortex 使用 `google/gemini-3-pro-preview`（fallback `google/gemini-2.5-pro`），video_analyzer 使用 `google/gemini-3-flash-preview`（`llm-config.defaults.jsonc:139-211`）
- F-016: utils 节点包含 hopper、outputter、video_analyzer（可选），每个均有独立的 provider/model/fallback 配置（`llm-config.defaults.jsonc:44-72`）

## CLI 入口与配置

- F-020: CLI 入口 `main.py` 使用 Typer 框架，创建 `app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)`（`main.py:34`）
- F-021: `DeviceType` 枚举继承 `StrEnum`，值为 `LOCAL = "local"` 和 `LIMRUN = "limrun"`（`main.py:38-42`）
- F-022: `run_automation` 异步函数签名接收 goal、locked_app_package、test_name、traces_output_path_str、output_description、graph_config_callbacks、video_recording_tools_enabled、wda_*、idb_*、device_type、limrun_platform 等参数（`main.py:45-63`）
- F-023: `run_automation` 内部调用 `initialize_llm_config()` 创建 LLM 配置，通过 `Builders.AgentConfig` 构建配置，创建 `Agent` 实例，调用 `agent.init()`、`agent.new_task(goal)`、`agent.run_task(request=task.build())`（`main.py:64-136`）
- F-024: CLI 命令 `main` 使用 `@app.command()` 装饰器，接收 goal 位置参数和多个 typer.Option 选项（`main.py:152-264`）
- F-025: CLI 支持 `--with-video-recording-tools` 标志启用视频录制工具，`--device-type/-d` 选择 local/limrun，`--limrun-platform` 指定 android/ios（`main.py:240-263`）
- F-026: `cli()` 函数首先调用 `_prompt_telemetry_consent(console)` 提示遥测同意，然后 `telemetry.initialize()`，执行 `app()`，最后 `telemetry.shutdown()`（`main.py:378-385`）
- F-027: `Settings` 类继承 `pydantic_settings.BaseSettings`，定义环境变量：OPENAI_API_KEY、GOOGLE_API_KEY、XAI_API_KEY、OPEN_ROUTER_API_KEY、ANTHROPIC_API_KEY、AZURE_API_KEY、MINIMAX_API_KEY、MINITAP_API_KEY（均为 `SecretStr | None`）（`config.py:21-29`）
- F-028: `Settings` 还定义 OPENAI_BASE_URL、AZURE_BASE_URL、MINITAP_BASE_URL（默认 `https://platform.minitap.ai`）、ADB_HOST、ADB_PORT、MOBILE_USE_TELEMETRY_ENABLED、PROJECT_NAME（`config.py:31-41`）
- F-029: 全局单例 `settings = Settings()`，模块加载时通过 `load_dotenv(verbose=True)` 加载 .env 文件（`config.py:17,45`）
- F-030: `LLMProvider` 类型字面量包含 `"openai", "google", "openrouter", "xai", "vertexai", "minitap", "anthropic", "azure", "minimax"`（`config.py:101-103`）
- F-031: `LLMUtilsNode` 类型字面量为 `"outputter", "hopper", "video_analyzer"`（`config.py:104`）
- F-032: `AgentNode` 类型字面量为 `"planner", "orchestrator", "contextor", "cortex", "executor"`（`config.py:106-112`）
- F-033: `LLM` 类继承 `BaseModel`，字段为 `provider: LLMProvider` 和 `model: str`，包含 `validate_provider(self, name: str)` 方法根据 provider 检查对应环境变量（`config.py:131-165`）
- F-034: `LLMWithFallback` 类继承 `LLM`，新增字段 `fallback: LLM`（`config.py:168-172`）
- F-035: `LLMConfigUtils` 类字段为 `outputter: LLMWithFallback`、`hopper: LLMWithFallback`、`video_analyzer: LLMWithFallback | None = None`（`config.py:175-178`）
- F-036: `LLMConfig` 类字段为 planner、orchestrator、contextor、cortex、executor（均为 `LLMWithFallback`）和 `utils: LLMConfigUtils`（`config.py:181-187`）
- F-037: `LLMConfig.validate_providers()` 方法逐一验证所有 agent 和 utils 节点的 provider 凭据（`config.py:189-198`）
- F-038: `LLMConfig.get_agent(self, item: AgentNode) -> LLMWithFallback` 和 `get_utils(self, item: LLMUtilsNode) -> LLMWithFallback` 方法通过 `getattr` 获取配置（`config.py:213-223`）
- F-039: `get_default_llm_config()` 从 `llm-config.defaults.jsonc` 加载 `default` 配置，失败时回退到硬编码 OpenAI 配置（`config.py:226-273`）
- F-040: `get_default_minitap_llm_config(validate: bool = True)` 返回使用 minitap provider 的配置，仅当 MINITAP_API_KEY 可用时返回（`config.py:276-325`）
- F-041: `deep_merge_llm_config(default, override)` 执行深度合并，override 中的未知键会被忽略并警告（`config.py:328-347`）
- F-042: `parse_llm_config()` 加载默认配置并与 `llm-config.override.jsonc` 深度合并，验证失败时回退默认配置（`config.py:350-368`）
- F-043: `initialize_llm_config()` 调用 `parse_llm_config()` 并执行 `validate_providers()`（`config.py:371-375`）
- F-044: `OutputConfig` 类字段为 `structured_output: type[BaseModel] | dict | None` 和 `output_description: str | None`，当两者同时提供时发出警告，structured_output 优先（`config.py:381-430`）
- F-045: 常量 `RECURSION_LIMIT = 400`、`MAX_MESSAGES_IN_HISTORY = 25`、`EXECUTOR_MESSAGES_KEY = "executor_messages"`（`constants.py:1-3`）
- F-046: `DevicePlatform` 枚举继承 `StrEnum`，值为 `ANDROID = "android"` 和 `IOS = "ios"`（`context.py:31-35`）
- F-047: `DeviceContext` 类继承 `BaseModel`，字段为 `host_platform: Literal["WINDOWS", "LINUX"]`、`mobile_platform: DevicePlatform`、`device_id: str`、`device_width: int`、`device_height: int`，包含 `to_str()` 方法（`context.py:38-52`）
- F-048: `ExecutionSetup` 类字段为 `traces_path`、`trace_name`、`enable_remote_tracing`、`app_lock_status: AppLaunchResult | None`，包含 `get_locked_app_package()` 方法（`context.py:55-72`）
- F-049: `MobileUseContext` 类继承 `BaseModel`，配置 `arbitrary_types_allowed=True`，字段包括 trace_id、device、llm_config、adb_client、ui_adb_client、ios_client、limrun_android_controller、execution_setup、on_agent_thought、on_plan_changes、minitap_api_key、video_recording_enabled（`context.py:78-92`）

## Agent 架构

- F-050: 系统包含 9 个 Agent 节点：PlannerNode、OrchestratorNode、ContextorNode、CortexNode、ExecutorNode、ExecutorToolNode、SummarizerNode，以及工具型 Agent hopper、outputter、video_analyzer（`graph/graph.py:9-24`）
- F-051: 所有图节点 Agent 类均实现 `__init__(self, ctx: MobileUseContext)` 和 `async def __call__(self, state: State)` 方法（`orchestrator.py:25-34`、`planner.py:25-34`、`cortex.py:34-43`、`executor.py:23-32`、`contextor.py:23-32`、`summarizer.py:12-16`）
- F-052: 图节点 Agent 使用 `@wrap_with_callbacks` 装饰器，在执行前后记录日志（before/on_success/on_failure）（`orchestrator.py:29-33`、`planner.py:29-33`、`cortex.py:38-42`、`executor.py:27-31`、`contextor.py:27-31`）
- F-053: 所有 Agent 使用 Jinja2 模板渲染 prompt，模板文件为同目录下的 `.md` 文件（如 `planner.md`、`human.md`、`orchestrator.md` 等）（`planner.py:46-62`、`orchestrator.py:61-71`、`cortex.py:54-76`）
- F-054: 所有 Agent 通过 `get_llm(ctx=self.ctx, name="<agent_name>")` 获取 LLM 实例，使用 `with_structured_output(<OutputType>)` 结构化输出，通过 `with_fallback(main_call, fallback_call)` 实现主备 LLM 切换（`planner.py:68-79`、`orchestrator.py:77-86`、`cortex.py:92-101`）
- F-055: `PlannerNode` 负责生成子目标计划，输出 `PlannerOutput`（含 `subgoals: list[PlannerSubgoalOutput]`），将响应转换为 `Subgoal` 列表，初始状态为 `SubgoalStatus.NOT_STARTED`（`planner.py:80-88`、`planner/types.py:8-13`）
- F-056: `PlannerNode` 在 prompt 中注入 executor 工具列表（通过 `format_tools_list`）、平台信息、locked_app_package、当前前台应用（`planner.py:42-54`）
- F-057: `OrchestratorNode` 管理子目标推进：若无子目标启动则启动下一个；若有 `complete_subgoals_by_ids` 则调用 LLM 审查；根据 LLM 输出标记完成、失败重规划或启动下一个子目标（`orchestrator.py:34-117`）
- F-058: `OrchestratorOutput` 字段为 `completed_subgoal_ids: list[str]`、`needs_replaning: bool`、`reason: str`（`orchestrator/types.py:6-10`）
- F-059: `CortexNode` 是核心决策节点，接收 UI 层级、截图、executor 反馈，输出 `CortexOutput`（decisions、decisions_reason、goals_completion_reason、complete_subgoals_by_ids）（`cortex.py:34-141`、`cortex/types.py:4-15`）
- F-060: `CortexNode` 通过 `create_device_controller(self.ctx)` 获取控制器压缩截图，通过 `get_screenshot_message_for_llm` 将截图加入 LLM 消息（`cortex.py:86-90`）
- F-061: `CortexNode` 返回时清空 `latest_ui_hierarchy`、`latest_screenshot`、`focused_app_info`、`device_date`，并通过 `RemoveMessage(id=REMOVE_ALL_MESSAGES)` 清空 executor 消息（`cortex.py:126-141`）
- F-062: `CortexNode` 调用 `telemetry.capture_cortex_decision()` 记录决策遥测（`cortex.py:119-124`）
- F-063: `ExecutorNode` 接收 `structured_decisions`，使用 `llm.bind_tools()` 绑定工具，Google 模型不支持 `parallel_tool_calls` 参数（`executor.py:59-75`）
- F-064: `ExecutorNode` 将 cortex_last_thought、structured_decisions 和 executor_messages 作为消息发送给 LLM（`executor.py:49-57`）
- F-065: `ContextorNode` 负责采集设备上下文：调用 `device_controller.get_screen_data()` 获取 UI 层级和截图，`get_current_foreground_package_async()` 获取前台应用，`get_device_date()` 获取设备日期（`contextor.py:33-36`）
- F-066: `ContextorNode` 包含应用锁定验证逻辑 `_handle_app_lock_verification`，当检测到当前应用与锁定应用不符时，调用 LLM 决定是否重新启动应用（`contextor.py:81-136`）
- F-067: `ContextorOutput` 字段为 `should_relaunch_app: bool` 和 `reasoning: str`（通过 `_invoke_contextor_llm` 返回）（`contextor.py:107-173`）
- F-068: `SummarizerNode` 不使用 LLM，当消息数超过 `MAX_MESSAGES_IN_HISTORY`（25）时，删除旧的 ToolMessage 和 HumanMessage（`summarizer.py:16-35`）
- F-069: `hopper` 是异步函数（非图节点），签名 `async def hopper(ctx: MobileUseContext, request: str, data: str) -> HopperOutput`，用于从数据中提取信息，使用 `is_utils=True` 获取 LLM（`hopper.py:23-46`）
- F-070: `HopperOutput` 字段为 `found: bool`、`output: str | None`、`reason: str`（`hopper.py:14-20`）
- F-071: `outputter` 是异步函数（非图节点），签名 `async def outputter(ctx: MobileUseContext, output_config: OutputConfig, graph_output: State) -> dict`，生成最终结构化输出（`outputter.py:18-85`）
- F-072: `outputter` 支持 `structured_output`（Pydantic 模型或 dict schema）和 `output_description` 两种输出方式，structured_output 优先（`outputter.py:55-68`）
- F-073: `analyze_video` 异步函数签名 `async def analyze_video(ctx: MobileUseContext, video_path: Path, prompt: str) -> str`，使用 Gemini 视频模型分析视频内容，超时 120 秒（`video_analyzer.py:22-104`）
- F-074: `SubgoalStatus` 枚举值为 `NOT_STARTED`、`PENDING`、`SUCCESS`、`FAILURE`（`planner/types.py:16-20`）
- F-075: `Subgoal` 类字段为 `id: str`、`description: str`、`completion_reason: str | None`、`status: SubgoalStatus`、`started_at: datetime | None`、`ended_at: datetime | None`（`planner/types.py:23-31`）
- F-076: Agent 调用关系：Planner → Orchestrator（图边），Orchestrator → Contextor（经 convergence gate），Contextor → Cortex，Cortex → Executor/Orchestrator（条件分支），Executor → ExecutorToolNode/Summarizer（条件分支），ExecutorToolNode → Summarizer，Summarizer → convergence（`graph/graph.py:129-158`）

## 设备控制层

- F-100: `MobileDeviceController` 是 `Protocol`（协议类型），定义 15 个抽象方法：tap、swipe、screenshot、input_text、launch_app、terminate_app、open_url、press_back、press_home、press_enter、get_ui_hierarchy、find_element、cleanup、erase_text、get_screen_data、get_compressed_b64_screenshot、start_video_recording、stop_video_recording（`device_controller.py:18-182`）
- F-101: `ScreenDataResponse` 类字段为 `base64: str`、`elements: list`、`width: int`、`height: int`、`platform: str`（`device_controller.py:10-15`）
- F-102: `TapOutput` 类字段为 `error: str | None = None`（`types.py:4-7`）
- F-103: `Bounds` 类字段为 `x1: int`、`y1: int`、`x2: int`、`y2: int`，包含 `get_center() -> CoordinatesSelectorRequest` 方法（`types.py:10-23`）
- F-104: `CoordinatesSelectorRequest` 类配置 `extra="forbid"`，字段为 `x: int`、`y: int`（`types.py:26-32`）
- F-105: `PercentagesSelectorRequest` 类配置 `extra="forbid"`，字段为 `x_percent: int`（0-100）、`y_percent: int`（0-100），包含 `to_coords(width, height)` 转换方法（`types.py:35-53`）
- F-106: `SwipeRequest` 类配置 `extra="forbid"`，字段为 `swipe_mode: SwipeStartEndCoordinatesRequest | SwipeStartEndPercentagesRequest` 和 `duration: int | None`（1-10000ms）（`types.py:81-106`）
- F-107: `AndroidDeviceController` 类实现 `MobileDeviceController` 协议，构造函数接收 `device_id`、`adb_client: AdbClient`、`ui_adb_client: UIAutomatorClient`、`device_width`、`device_height`（`android_controller.py:36-50`）
- F-108: `AndroidDeviceController.tap` 通过 ADB shell 命令 `input tap x y` 或 `input swipe x y x y duration`（长按）实现（`android_controller.py:58-75`）
- F-109: `AndroidDeviceController` 具有 `device` 属性，懒加载 `AdbDevice` 实例（`android_controller.py:52-56`）
- F-110: `iOSDeviceController` 类实现 `MobileDeviceController` 协议，构造函数接收 `ios_client: IosClientWrapper`、`device_id`、`device_width`、`device_height`，内部通过 `isinstance(ios_client, IdbClientWrapper)` 判断使用 IDB 还是 WDA（`ios_controller.py:36-50`）
- F-111: `iOSDeviceController.tap` 调用 `self.ios_client.tap(x, y, duration)`（`ios_controller.py:52-64`）
- F-112: `create_device_controller(ctx: MobileUseContext) -> MobileDeviceController` 工厂函数根据 `ctx.device.mobile_platform` 返回 Android 或 iOS 控制器；Android 优先使用 limrun_android_controller（`controller_factory.py:10-47`）
- F-113: `get_controller(ctx)` 是 `create_device_controller` 的别名（`controller_factory.py:50-51`）
- F-114: `UnifiedMobileController` 类封装 `MobileDeviceController`，提供 `tap_at(x, y)`、`tap_percentage(x_percent, y_percent)`、`tap_element(resource_id, text, index)`、`swipe_coords(...)` 等高级方法（`unified_controller.py:17-100`）
- F-115: `UnifiedMobileController.tap_element` 先获取 UI 层级，调用 `find_element` 查找元素，再点击元素中心（`unified_controller.py:50-87`）

## 工具系统

- F-140: 工具通过 `ToolWrapper` 数据类注册，字段为 `tool_fn_getter: Callable[[MobileUseContext], BaseTool]`、`on_success_fn: Callable[..., str]`、`on_failure_fn: Callable[..., str]`（`tool_wrapper.py:9-12`）
- F-141: `CompositeToolWrapper` 继承 `ToolWrapper`，新增 `composite_tools_fn_getter: Callable[[MobileUseContext], list[BaseTool]]`（`tool_wrapper.py:15-16`）
- F-142: `EXECUTOR_WRAPPERS_TOOLS` 列表注册 15 个工具包装器：back、open_link、tap、long_press_on、swipe、focus_and_input_text、erase_one_char、launch_app、stop_app、focus_and_clear_text、press_key、wait_for_delay、save_note、read_note、list_notes（`tools/index.py:27-44`）
- F-143: `VIDEO_RECORDING_WRAPPERS` 列表注册 2 个视频工具：start_video_recording、stop_video_recording（`tools/index.py:46-49`）
- F-144: `get_tools_from_wrappers(ctx, wrappers) -> list[BaseTool]` 遍历包装器，对 `CompositeToolWrapper` 调用 `composite_tools_fn_getter`，对普通 `ToolWrapper` 调用 `tool_fn_getter`（`tools/index.py:52-63`）
- F-145: `format_tools_list(ctx, wrappers)` 返回逗号分隔的工具名称字符串（`tools/index.py:66-67`）
- F-146: 视频录制工具仅在 `ctx.video_recording_enabled` 为 True 时添加到 executor_wrappers（`graph/graph.py:113-115`、`planner.py:42-44`、`cortex.py:50-52`、`executor.py:62-64`）
- F-147: `Target` 类字段为 `resource_id: str | None`、`resource_id_index: int | None`、`text: str | None`、`text_index: int | None`、`bounds: ElementBounds | None`，model_validator 自动设置默认索引为 0（`tools/types.py:6-35`）
- F-148: `tap` 工具使用 `@tool` 装饰器定义，参数为 `agent_thought: str`、`target: Target`，注入 `tool_call_id` 和 `state`，返回 `Command` 更新状态（`tools/mobile/tap.py:21-147`）
- F-149: `tap` 工具实现三级回退定位策略：(1) bounds 坐标 → (2) resource_id → (3) text，每级失败后尝试下一级（`tools/mobile/tap.py:52-120`）
- F-150: `tap_wrapper` 是 `ToolWrapper` 实例，`on_success_fn` 返回 "Tap on element with {selector_info} was successful."，`on_failure_fn` 返回包含所有尝试详情的失败消息（`tools/mobile/tap.py:150-154`）
- F-151: scratchpad 工具包括 `save_note`、`read_note`、`list_notes`，均使用 `@tool` 装饰器，通过 `InjectedState` 访问 `state.scratchpad` 字典（`tools/scratchpad.py:18-124`）
- F-152: `save_note` 工具更新 `state.scratchpad[key] = content`，返回包含 agents_thoughts、executor_messages、scratchpad 的 Command 更新（`tools/scratchpad.py:20-52`）
- F-153: `ExecutorToolNode` 继承 LangGraph 的 `ToolNode`，重写 `_afunc` 和 `_func`，实现工具调用顺序执行（非并行），一个工具失败后中止后续调用（`executor/tool_node.py:19-134`）
- F-154: `ExecutorToolNode.__func` 遍历 tool_calls，失败时调用 `_get_erroneous_command` 生成错误消息，并通过 `telemetry.capture_executor_action` 记录成功/失败遥测（`executor/tool_node.py:67-134`）
- F-155: 工具函数统一注入 `agent_thought: str` 参数（Agent 执行工具前的思考），并通过 `state.asanitize_update` 将思考和结果加入 agents_thoughts（`tools/mobile/tap.py:24`、`tools/scratchpad.py:21`）

## 服务层（LLM/Accessibility/Telemetry）

- F-170: `invoke_llm_with_timeout_message[T]` 异步泛型函数，执行 LLM 调用，超过 `timeout_seconds`（默认 10 秒）后显示 "Waiting for LLM call response..." 消息（`services/llm.py:31-57`）
- F-171: `with_fallback[T]` 异步泛型函数，先执行 `main_call`，失败或返回 None 时执行 `fallback_call`，`none_should_fallback` 参数控制 None 是否触发回退（默认 True）（`services/llm.py:312-325`）
- F-172: `get_llm(ctx, name, is_utils, use_fallback, temperature)` 函数根据 name 从 ctx.llm_config 获取 LLMWithFallback，use_fallback=True 时取 fallback 模型，根据 provider 调用对应工厂函数（`services/llm.py:260-306`）
- F-173: LLM 提供商工厂函数包括：`get_openai_llm`、`get_google_llm`、`get_anthropic_llm`、`get_vertex_llm`、`get_openrouter_llm`、`get_grok_llm`（xAI）、`get_azure_llm`、`get_minimax_llm`、`get_minitap_llm`（`services/llm.py:70-226`）
- F-174: `get_minitap_llm` 返回 `ChatOpenAI` 实例，base_url 为 `{MINITAP_BASE_URL}/api/v1`，通过 `default_query` 传递 sessionId 和 traceOnlyUsage，通过 `default_headers` 传递 X-Agent-Name 和 X-Project-Name（`services/llm.py:70-108`）
- F-175: Google 模型（`ChatGoogleGenerativeAI`、`ChatVertexAI`）默认 max_retries=2，不支持 parallel_tool_calls（`services/llm.py:111-136`、`executor.py:70-72`）
- F-176: `get_accessibility_tree(device_id)` 异步函数通过 `adb shell uiautomator dump /dev/tty` 获取 Android UI 层级 XML，解析并清理输出（`services/accessibility.py:29-79`）
- F-177: `run_subprocess(command)` 异步函数通过 `asyncio.create_subprocess_shell` 执行 shell 命令，返回 (stdout, stderr) 元组（`services/accessibility.py:10-26`）
- F-178: 遥测服务使用 PostHog，POSTHOG_API_KEY 硬编码为 `phc_MTwMcqOjMpTdTdrYwQUlsWaKkB7C8MPAw9YyZhRv8B8`，HOST 为 `https://eu.i.posthog.com`，事件前缀 `mobile_use_`（`services/telemetry.py:17-19`）
- F-179: `TelemetryConfig` 类管理遥测同意状态，配置文件路径为 `~/.minitap/telemetry.json`，禁用时不持久化以确保下次会话再次询问（`services/telemetry.py:21-63`）
- F-180: 遥测启用优先级：环境变量 `MOBILE_USE_TELEMETRY_ENABLED` > 持久化配置文件（`services/telemetry.py:74-80`）

## 图结构与状态

- F-190: `get_graph(ctx: MobileUseContext) -> CompiledStateGraph` 异步函数构建 LangGraph 工作流（`graph/graph.py:100-160`）
- F-191: 图节点包括：planner、orchestrator、contextor、cortex、executor、executor_tools、summarizer、convergence（`graph/graph.py:104-126`）
- F-192: `convergence_node` 是空操作节点（返回 `{}`），标记为 `defer=True`，作为并行执行路径的汇聚点（`graph/graph.py:34-36,126`）
- F-193: 图边定义：START → planner → orchestrator → convergence（`graph/graph.py:129-131`）
- F-194: 图边定义：contextor → cortex（`graph/graph.py:132`）
- F-195: cortex 条件边 `post_cortex_gate`：若有 complete_subgoals_by_ids 或无 structured_decisions → "review_subgoals"（orchestrator）；若有 structured_decisions → "execute_decisions"（executor）；可同时返回两个路径（`graph/graph.py:60-74,133-140`）
- F-196: executor 条件边 `post_executor_gate`：若最后一条 AIMessage 有 tool_calls → "invoke_tools"（executor_tools）；否则 → "skip"（summarizer）（`graph/graph.py:77-97,141-145`）
- F-197: 图边定义：executor_tools → summarizer → convergence（`graph/graph.py:146-148`）
- F-198: convergence 条件边 `convergence_gate`：任一子目标失败 → "replan"（planner）；全部完成 → "end"（END）；有当前运行子目标 → "continue"（contextor）（`graph/graph.py:39-57,150-158`）
- F-199: `State` 类继承 `BaseModel`，使用 `Annotated` 类型定义字段和 reducer 函数（`graph/state.py:25-71`）
- F-200: `State` 字段包括：messages（add_messages reducer）、remaining_steps、initial_goal、subgoal_plan、latest_ui_hierarchy（take_last）、latest_screenshot（take_last）、focused_app_info（take_last）、device_date（take_last）、structured_decisions（take_last）、complete_subgoals_by_ids（take_last）、executor_messages（add_messages）、cortex_last_thought（take_last）、agents_thoughts（take_last）、scratchpad（merge_dicts，默认空字典）（`graph/state.py:26-71`）
- F-201: `take_last(a, b)` reducer 函数始终返回 b（新值覆盖旧值）（`graph/state.py:16-17`）
- F-202: `merge_dicts(a, b)` reducer 函数合并两个字典，b 的键覆盖 a（`graph/state.py:20-22`）
- F-203: `State.asanitize_update(ctx, update, agent)` 异步方法清理状态更新：将 agents_thoughts 统一为列表格式，过滤 None，调用 `_add_agent_thoughts` 添加 agent 名称前缀（`graph/state.py:73-100`）
- F-204: `_add_agent_thoughts` 为每条 thought 添加 `[agent_name]` 前缀，通过 `ctx.on_agent_thought` 回调通知，并在启用 trace 时调用 `record_interaction` 记录（`graph/state.py:103-120`）

## SDK 层

- F-210: `Agent` 类是 SDK 核心入口，构造函数 `__init__(self, *, config: AgentConfig | None = None)`，无配置时使用 `get_default_agent_config()`（`sdk/agent.py:88-118`）
- F-211: `Agent` 类内部状态字段：`_config`、`_tasks: list[Task]`、`_tmp_traces_dir`、`_initialized: bool`、`_device_context`、`_adb_client`、`_ui_adb_client`、`_ios_client`、`_ios_device_type`、`_current_task`、`_task_lock: asyncio.Lock`、`_cloud_mobile_id`、`_limrun_instance_id`、`_limrun_controller`（`sdk/agent.py:89-102`）
- F-212: `Agent.init(api_key, server_restart_attempts=3, retry_count=5, retry_wait_seconds=5)` 异步方法初始化设备连接，内部调用 `_init_internal`，异常时记录遥测并重新抛出（`sdk/agent.py:120-144`）
- F-213: `_init_internal` 支持四种设备模式：cloud_mobile（跳过本地初始化）、BrowserStack、Limrun（预置控制器或 limrun_config）、本地设备（ADB/xcrun）（`sdk/agent.py:146-286`）
- F-214: `Agent.new_task(goal: str)` 返回 `TaskRequestBuilder[None]`，支持链式调用 with_output_format、with_output_description、with_locked_app_package、using_profile、with_max_steps、with_trace_recording、with_name（`sdk/agent.py:536-556`）
- F-215: `Agent.run_task(...)` 有 7 个 @overload 签名，支持 goal 参数或 request 参数，支持 TaskRequest 和 PlatformTaskRequest，返回 str/dict/TOutput/None（`sdk/agent.py:558-640`）
- F-216: `run_task` 对 cloud_mobile 配置要求使用 `PlatformTaskRequest`，委托给 `_run_cloud_mobile_task`（`sdk/agent.py:642-651`）
- F-217: `_run_cloud_mobile_task` 通过 `CloudMobileService.run_task_on_cloud_mobile` 远程执行任务，本地不运行 agent 逻辑，支持状态和日志回调（`sdk/agent.py:704-809`）
- F-218: `_run_task` 本地执行路径：创建 Task 对象 → 构建 MobileUseContext → 准备 tracing/app 安装/app 锁定/输出文件 → 通过 `get_graph(context).astream()` 流式执行图 → 提取输出 → 调用 `task.finalize()`（`sdk/agent.py:811-1041`）
- F-219: 图执行配置 `recursion_limit` 来自 `task.request.max_steps`，stream_mode 为 `["messages", "custom", "updates", "values"]`（`sdk/agent.py:927-934`）
- F-220: `Agent.install_apk(apk_path)` 支持本地 Android（ADB install）和云手机（CloudMobileService.install_apk，含签名 URL 上传三步流程）（`sdk/agent.py:288-367`）
- F-221: `Agent.install_app(app_path)` 支持 Android（APK）和 iOS Limrun（.app 文件夹，使用 diff-based patch syncing），iOS 返回 bundle_id（`sdk/agent.py:369-534`）
- F-222: `Agent.get_screenshot()` 支持云手机、本地 Android（ADB）、Limrun iOS、本地 iOS 模拟器（xcrun simctl）（`sdk/agent.py:1058-1144`）
- F-223: `Agent.clean(force=False)` 清理资源：云手机直接标记未初始化；Limrun 清理设备；本地清理 iOS 客户端；结束遥测会话（`sdk/agent.py:1146-1176`）
- F-224: `Agent.stop_current_task()` 取消当前运行的 asyncio.Task（`sdk/agent.py:1043-1056`）
- F-225: `AgentConfig` 类字段为 agent_profiles、task_request_defaults、default_profile、device_id、device_platform、servers、graph_config_callbacks、cloud_mobile_id_or_ref、ios_client_config、browserstack_config、video_recording_enabled、limrun_config、limrun_android_controller、limrun_ios_controller（`sdk/types/agent.py:95-130`）
- F-226: `LimrunConfig` 类字段为 platform（LimrunPlatform）、api_key、base_url、inactivity_timeout（默认 "10m"）、hard_timeout、display_name、labels（`sdk/types/agent.py:24-48`）
- F-227: `ServerConfig` 类字段为 `adb_host: str`、`adb_port: int`（`sdk/types/agent.py:86-92`）
- F-228: `ApiBaseUrl` 类字段为 scheme（http/https）、host、port，包含 `to_url()`、`from_url(url)` 类方法和 `__eq__` 比较（`sdk/types/agent.py:51-83`）
- F-229: `AgentConfigBuilder` 类提供流式接口构建 AgentConfig，方法包括 add_profile、add_profiles、with_default_profile、for_device、for_cloud_mobile、for_browserstack、for_limrun、with_default_task_config、with_adb_server、with_servers、with_graph_config_callbacks、with_ios_client_config、with_limrun_android_controller、with_limrun_ios_controller、with_video_recording_tools、build（`sdk/builders/agent_config_builder.py:27-445`）
- F-230: `AgentConfigBuilder` 强制设备配置互斥：for_device/for_cloud_mobile/for_browserstack/for_limrun/with_limrun_*_controller 不能同时设置（`sdk/builders/agent_config_builder.py:100-243`）
- F-231: `build(validate_profiles=True)` 方法在无 profile 时自动创建默认 profile（优先 minitap，其次 OpenAI），单 profile 时自动选择，多 profile 时必须调用 with_default_profile（`sdk/builders/agent_config_builder.py:387-445`）
- F-232: `AgentProfile` 类字段为 `name: str`、`llm_config: LLMConfig`，构造函数支持 `from_file` 参数从 JSONC 文件加载 LLM 配置（`sdk/types/task.py:21-57`）
- F-233: `TaskRequestBase` 字段为 max_steps（默认 RECURSION_LIMIT=400）、record_trace（默认 False）、trace_path（默认 "mobile-use-traces"）、llm_output_path、thoughts_output_path（`sdk/types/task.py:64-73`）
- F-234: `TaskRequestCommon` 继承 TaskRequestBase，新增 locked_app_package、app_path（`sdk/types/task.py:76-91`）
- F-235: `TaskRequest[TOutput]` 继承 TaskRequestCommon，字段为 goal、profile、task_name、output_description、output_format（Pydantic 模型类）、enable_remote_tracing（`sdk/types/task.py:94-117`）
- F-236: `PlatformTaskRequest[TOutput]` 继承 TaskRequestBase，字段为 task（str 或 ManualTaskConfig）、profile、execution_origin（默认 "sdk"）、record_trace（默认 True）、trace_path（临时目录）、task_run_id_available_event、task_run_id（`sdk/types/task.py:135-156`）
- F-237: `TaskResult` 字段为 content、error、execution_time_seconds、steps_taken，包含 `get_as_model(model_class)` 方法解析为 Pydantic 模型（`sdk/types/task.py:163-196`）
- F-238: `Task` 类字段为 id、device（DeviceContext）、status（TaskRunStatus）、status_message、on_status_changed 回调、request（TaskRequest）、created_at、ended_at、result（TaskResult），包含 `finalize()`、`get_name()`、`set_status()` 方法（`sdk/types/task.py:199-272`）
- F-239: `CloudMobileService` 类管理云手机任务执行，方法包括 start_and_wait_for_ready、resolve_cloud_mobile_id、run_task_on_cloud_mobile、cancel_task_runs、get_screenshot、install_apk，使用 httpx.AsyncClient 调用 Platform API（`sdk/services/cloud_mobile.py:90-656`）

## 客户端层

- F-240: `AdbTunnel` 类通过 WebSocket 桥接本地 TCP 连接到远程 ADB 服务器，在独立线程中运行 asyncio 事件循环（`clients/adb_tunnel.py:34-46`）
- F-241: `AdbTunnel` 构造函数接收 `remote_url: str` 和 `token: str`（Bearer 认证），`start()` 返回本地地址 `127.0.0.1:PORT`（`clients/adb_tunnel.py:48-114`）
- F-242: `AdbTunnel._bridge` 实现双向数据转发：tcp_to_ws 从 TCP 接收数据发送到 WebSocket，ws_to_tcp 从 WebSocket 接收数据发送到 TCP，任一方向结束即取消另一方向（`clients/adb_tunnel.py:220-293`）
- F-243: `adb_tunnel(remote_url, token)` 是异步上下文管理器，封装 AdbTunnel 的 start/stop 生命周期（`clients/adb_tunnel.py:296-319`）
- F-244: BUFFER_SIZE 为 32KB（与 Go SDK 一致），PING_INTERVAL 为 30 秒（`clients/adb_tunnel.py:30-31`）
- F-245: `UIAutomatorClient` 类封装 uiautomator2 库用于 Android 屏幕数据采集，构造函数接收 `device_id: str`（`clients/ui_automator_client.py:181-200`）
- F-246: `UIAutomatorClient._ensure_connected` 在连接前检查并卸载 Maestro 包（`dev.mobile.maestro`），因为 Maestro 与 uiautomator2 冲突（`clients/ui_automator_client.py:166-225`）
- F-247: `UIAutomatorClient` 方法包括 press_key、send_text（使用 FastInputIME 支持特殊字符）、get_hierarchy、get_screenshot、get_screenshot_base64、get_screen_data、disconnect（`clients/ui_automator_client.py:227-317`）
- F-248: `UIAutomatorScreenData` 字段为 base64、hierarchy_xml、elements（list[dict]）、width、height（`clients/ui_automator_client.py:29-36`）
- F-249: `get_client(device_id)` 工厂函数返回 UIAutomatorClient 实例（`clients/ui_automator_client.py:320-330`）
- F-250: `WdaClientWrapper` 类封装 facebook-wda 用于物理 iOS 设备自动化，构造函数接收 `udid` 和 `config: WdaClientConfig`（`clients/wda_client.py:71-126`）
- F-251: `WdaClientWrapper.init_client` 自动检查/启动 iproxy 和 WDA（通过 xcodebuild），创建 WDA session（`clients/wda_client.py:128-226`）
- F-252: `with_wda_client` 装饰器包装 WDA 操作，捕获 WDARequestError/WDAError/Exception，根据返回类型注解返回 False 或 None（`clients/wda_client.py:27-68`）
- F-253: `WdaClientWrapper` 方法包括 tap、swipe、screenshot、launch、terminate、text、open_url、key（key_code=42 为退格）、button（HOME/volume_up/volume_down）、describe_all、app_current、cleanup（`clients/wda_client.py:295-526`）
- F-254: `WdaClientWrapper` 支持异步上下文管理器 `__aenter__`/`__aexit__`（`clients/wda_client.py:269-278`）
- F-255: `WdaClientWrapper._parse_xml_to_elements` 将 WDA XML 源码解析为扁平元素列表，元素字段包括 type、value、label、frame（x/y/width/height）、enabled、visible（`clients/wda_client.py:485-512`）

## 技能定义

- F-260: 技能文件 `skills/mobile-use-setup/SKILL.md` 定义了交互式安装向导，frontmatter 包含 name 和 description（`skills/mobile-use-setup/SKILL.md:1-4`）
- F-261: 技能适用于：设置移动自动化、配置 mobile-use SDK、连接 iOS/Android 设备、设置云虚拟设备、创建新移动测试项目（`skills/mobile-use-setup/SKILL.md:10-17`）
- F-262: 安装流程分 8 个阶段：收集需求、检查前置条件、安装缺失依赖、创建项目、配置凭据、设备特定设置、创建启动脚本、验证设置（`skills/mobile-use-setup/SKILL.md:19-226`）
- F-263: 支持的设备类型：iOS 物理设备（Appium + XCUITest + libimobiledevice）、iOS 模拟器（idb-companion）、Android 物理设备（ADB）、Android 云设备（Platform only）（`skills/mobile-use-setup/SKILL.md:35-46,228-235`）
- F-264: LLM 配置模式：Platform（推荐，Minitap 处理 LLM 配置，仅需 API key）和 Local（完全控制，使用 llm-config.override.jsonc）（`skills/mobile-use-setup/SKILL.md:29-33`）
- F-265: 平台模式启动脚本使用 `Agent()` + `PlatformTaskRequest(task="...")`，本地模式使用 `AgentProfile(from_file=...)` + `Builders.AgentConfig.with_default_profile(...)`（`skills/mobile-use-setup/SKILL.md:159-208`）
