---
type: Insights
title: "mobile-use 架构洞察"
---

# mobile-use 架构洞察

> I阶段分析。基于 R 阶段 265 条事实。
> 分析日期：2026-08-23

---

## 洞察一：九节点 LangGraph 工作流——分层认知的多 Agent 协作架构

**陈述**：mobile-use 并非单体 LLM 调用，而是由 9 个 Agent 节点构成的 LangGraph（状态图）工作流，按认知职责严格分层：Planner（规划者）将用户目标分解为子目标序列；Orchestrator（编排者）推进子目标状态机并决定是否重规划；Contextor（上下文采集者）抓取 UI 层级、截图和前台应用信息；Cortex（大脑皮层）是核心决策节点，基于视觉和 UI 信息产出结构化决策；Executor（执行者）将决策绑定工具并生成工具调用；ExecutorToolNode 顺序执行工具；Summarizer（摘要者）在消息超限时裁剪历史。此外还有三个工具型异步函数——hopper（信息提取）、outputter（结构化输出）、video_analyzer（视频分析）——它们不进入主图，而是作为按需调用的辅助 Agent。图中设有 convergence（汇聚）空节点和三个条件门（post_cortex_gate、post_executor_gate、convergence_gate），形成"感知→决策→执行→汇聚→再感知"的闭环，子目标失败时自动回到 Planner 重规划。

**证据**：
- F-050: 9 个 Agent 节点的完整清单（PlannerNode、OrchestratorNode、ContextorNode、CortexNode、ExecutorNode、ExecutorToolNode、SummarizerNode + hopper/outputter/video_analyzer）
- F-076: Agent 调用关系和图边定义，Planner→Orchestrator→convergence，Contextor→Cortex，Cortex 条件分支到 Executor 或 Orchestrator
- F-190~F-198: get_graph 函数构建 StateGraph，8 个命名节点和 3 个条件门的完整定义
- F-055~F-068: 各节点职责的详细描述——Planner 生成 Subgoal 列表，Orchestrator 管理子目标状态，Cortex 输出 decisions 并清空截图，Executor 绑定工具，Summarizer 无 LLM 纯规则裁剪
- F-195: post_cortex_gate 可同时返回两个路径（review_subgoals 和 execute_decisions），支持并行分支
- F-198: convergence_gate 三态路由——失败重规划、全部完成结束、有运行中子目标则继续

**反常识**：常见的 Agent 框架认知是"一个 ReAct 循环（思考→行动→观察）搞定一切"。mobile-use 揭示了多 Agent 分层的必要性：当任务需要跨多个界面、多个应用、数十步操作时，单 Agent 的上下文窗口会被截图和 UI 层级迅速淹没，且无法区分"战略规划"和"战术执行"。Cortex 节点在返回时主动清空 latest_ui_hierarchy、latest_screenshot 和 executor_messages（F-061），这是一种刻意的"工作记忆遗忘"机制——每轮决策只携带当前屏幕信息，历史信息沉淀到 subgoal_plan 和 agents_thoughts 中，而非全部塞给 LLM。更深层的反常识是：图中没有"记忆节点"，记忆分散在 State 的多个 reducer 字段中（subgoal_plan 持久化、scratchpad 字典持久化、messages 用 add_messages 累积、latest_* 用 take_last 覆盖），由 LangGraph 的 reducer 机制自动管理，而非由某个 Agent 显式读写。

**行动**：
- 理解系统时，先掌握 graph.py 的节点和边定义，这是整个系统的"骨架"；再逐个深入 agents/ 目录下的节点实现。
- 调试 Agent 行为时，利用 trace 录制功能（--test-name）查看各节点的输入输出，而非只看最终结果。
- 扩展新功能时，优先判断应新增工具（Executor 可调用）还是新增图节点（需要独立认知循环）；大多数设备操作应作为工具，只有需要独立 LLM 决策的才适合成为节点。
- 子目标失败重规划是自动的，排查"任务卡住"问题时检查 subgoal_plan 中各 Subgoal 的 status 和 completion_reason。

---

## 洞察二：Protocol + Factory + UnifiedController——跨平台设备控制的三层抽象

**陈述**：mobile-use 通过三层抽象实现 Android 与 iOS 的统一控制。第一层是 `MobileDeviceController` Protocol（结构子类型协议），定义 18 个抽象方法（tap、swipe、screenshot、input_text、launch_app、get_ui_hierarchy、find_element 等），不使用继承而是用 Python 的 Protocol 做隐式接口约束。第二层是平台实现：`AndroidDeviceController` 通过 ADB shell 命令和 uiautomator2 实现；`iOSDeviceController` 封装 IosClientWrapper，内部自动适配 IDB（模拟器）和 WDA（物理设备）两种后端。第三层是 `create_device_controller` 工厂函数，根据 MobileUseContext 中的 mobile_platform 返回对应控制器，Android 端还会优先使用 limrun_android_controller（云手机控制器）。在 Protocol 之上还有 `UnifiedMobileController` 门面类，提供 tap_at（绝对坐标）、tap_percentage（百分比坐标）、tap_element（按 resource_id/text 查找并点击）等高级方法，将"查找元素→计算中心→点击"的三步操作封装为单次调用。坐标系统支持 CoordinatesSelectorRequest（绝对像素）和 PercentagesSelectorRequest（0-100 百分比），后者通过设备宽高自动转换。

**证据**：
- F-100: MobileDeviceController 是 Protocol，定义 18 个抽象方法（tap/swipe/screenshot/input_text/launch_app/terminate_app/open_url/press_back/press_home/press_enter/get_ui_hierarchy/find_element/cleanup/erase_text/get_screen_data/get_compressed_b64_screenshot/start_video_recording/stop_video_recording）
- F-107~F-108: AndroidDeviceController 实现协议，tap 通过 ADB shell `input tap x y` 或 `input swipe x y x y duration`（长按）实现
- F-110~F-111: iOSDeviceController 通过 isinstance 判断使用 IDB 还是 WDA，tap 委托给 ios_client.tap()
- F-112: create_device_controller 工厂函数，Android 优先 limrun_android_controller，其次本地 ADB；iOS 必须有 ios_client
- F-114~F-115: UnifiedMobileController 封装控制器，tap_element 先 get_ui_hierarchy 再 find_element 再点击元素中心
- F-103~F-105: Bounds 类有 get_center() 方法，PercentagesSelectorRequest 有 to_coords(width, height) 转换方法
- F-245~F-249: UIAutomatorClient 封装 uiautomator2，连接前会卸载冲突的 Maestro 包
- F-250~F-253: WdaClientWrapper 封装 facebook-wda，自动检查/启动 iproxy 和 WDA

**反常识**：跨平台移动自动化的常见方案是 Appium——一个独立的 Server 进程，通过 HTTP 协议接收命令，再用各平台的驱动（UiAutomator2/XCUITest）执行。mobile-use 反其道而行：它不依赖 Appium Server，而是直接在进程内通过 adbutils、uiautomator2、facebook-wda、fb-idb 等库与设备通信，Appium-Python-Client 仅作为可选依赖出现在列表中。这种"无 Server"架构减少了一个进程故障点和网络开销，但代价是需要为每个平台维护独立的客户端封装。更深层的设计选择是使用 Protocol 而非抽象基类（ABC）：Protocol 是结构子类型，任何实现了对应方法签名的对象都可以作为控制器传入，无需显式继承，这使得云手机控制器（LimrunAndroidController）可以不继承 AndroidDeviceController 就能直接替换，符合"组合优于继承"原则。UnifiedMobileController 不是 Protocol 的实现，而是它的装饰者——它持有一个 MobileDeviceController 实例并添加高级方法，这种分层使得底层协议保持精简（18 个原子操作），复杂逻辑在上层组合。

**行动**：
- 新增设备平台支持时，实现 MobileDeviceController Protocol 的 18 个方法即可，无需修改现有代码；在工厂函数中添加平台分支。
- 编写自定义工具时，通过 create_device_controller(ctx) 获取控制器，使用 UnifiedMobileController 的高级方法（如 tap_element）而非直接操作坐标。
- 百分比坐标适配不同分辨率设备，优先于绝对像素坐标；只有在需要精确定位时才使用 CoordinatesSelectorRequest。
- iOS 物理设备需要 WDA + Xcode 环境，iOS 模拟器需要 idb-companion；Android 仅需 ADB 和 uiautomator2，环境门槛更低。

---

## 洞察三：每节点独立模型 + 双层 fallback——9 提供商的 LLM 可插拔配置体系

**陈述**：mobile-use 的 LLM 配置不是"一个 API Key 用到底"，而是为每个 Agent 节点（planner/orchestrator/contextor/cortex/executor）和每个工具节点（hopper/outputter/video_analyzer）单独配置 provider、model 和 fallback 模型。配置体系由四个 Pydantic 模型构成：`LLM`（provider + model）、`LLMWithFallback`（继承 LLM，新增 fallback: LLM）、`LLMConfigUtils`（三个工具节点的配置）、`LLMConfig`（五个图节点 + utils）。系统支持 9 个 LLM 提供商：openai、google、anthropic、vertexai、openrouter、xai、azure、minimax、minitap，每个提供商有独立的工厂函数（如 get_openai_llm、get_google_llm 等）。配置加载采用三层合并：内置的 llm-config.defaults.jsonc（包含 default/minimax/recommended 三组预设）→ 用户可选的 llm-config.override.jsonc（深度合并，未知键被忽略并警告）→ 环境变量中的 API Key。运行时，每个 Agent 通过 get_llm(ctx, name) 获取 LLM 实例，with_fallback() 异步泛型函数实现主模型失败时自动切换到 fallback 模型。Google 模型有特殊处理：max_retries=2 且不支持 parallel_tool_calls 参数。

**证据**：
- F-030: LLMProvider 类型字面量包含 9 个提供商
- F-033~F-036: LLM、LLMWithFallback、LLMConfigUtils、LLMConfig 四个模型的字段定义
- F-037: LLMConfig.validate_providers() 逐一验证所有 8 个节点（5 个 agent + 3 个 utils）的 provider 凭据
- F-039~F-043: 配置加载链路——get_default_llm_config() 读 JSONC，deep_merge_llm_config() 深度合并，parse_llm_config() 组合默认与覆盖，initialize_llm_config() 执行验证
- F-013~F-016: 默认配置中，planner/orchestrator/executor/contextor 使用 gpt-5-nano（fallback gpt-5-mini），cortex 使用 gpt-5（fallback o4-mini），video_analyzer 可选
- F-171~F-172: with_fallback 泛型函数和 get_llm 函数，use_fallback 参数控制取主模型还是 fallback
- F-173: 9 个提供商工厂函数的完整清单
- F-175: Google 模型不支持 parallel_tool_calls，max_retries=2
- F-027~F-029: Settings 类定义 8 个 API Key 环境变量，MINITAP_BASE_URL 默认为 https://platform.minitap.ai

**反常识**：大多数 Agent 框架的 LLM 配置是全局的——一个 model 字符串传给所有 Agent。mobile-use 的"每节点独立模型"设计看似冗余，实则是成本与能力的精细平衡：Cortex 作为核心决策节点需要最强模型（gpt-5 或 gemini-3-pro），而 Planner/Orchestrator/Contextor 等结构化输出节点用 nano 级模型即可，Executor 绑定工具也不需要顶级推理能力。这种分层可以将单次任务的 LLM 成本降低数倍。另一个反常识是 fallback 不是"重试同一个 API"，而是"切换到不同提供商的不同模型"——例如主模型用 OpenAI gpt-5，fallback 可以是 Google gemini-2.5-pro，这要求所有 LLM 输出都通过 with_structured_output 统一为 Pydantic 模型，从而抹平提供商间的接口差异。Minitap 提供商（F-174）本质是 OpenAI 兼容代理，通过自定义 base_url 和请求头传递 sessionId/projectName，这是一种"平台即代理"的商业模式设计。

**行动**：
- 自定义配置时，复制 llm-config.override.template.jsonc 为 llm-config.override.jsonc，只覆盖需要修改的节点；不要直接改 defaults 文件。
- 成本优化：保持 cortex 使用强模型，其余节点用便宜模型；视频分析需要 Gemini 视觉能力，不能用纯文本模型替代。
- 排查 LLM 错误时，注意区分是主模型还是 fallback 模型报错——with_fallback 会记录两次尝试的异常。
- 离线/内网环境可通过 OPENAI_BASE_URL 指向本地兼容端点（如 vLLM/Ollama），provider 仍设为 "openai"。
- API Key 通过 .env 文件或环境变量配置，不要硬编码在配置文件中。

---

## 洞察四：双层 SDK API——高层 Agent 生命周期与低层 Builders 流式配置

**陈述**：mobile-use 对外暴露两层 SDK 接口。高层是 `Agent` 类，封装完整生命周期：构造（接收 AgentConfig）→ init()（初始化设备连接，支持本地/云手机/BrowserStack/Limrun 四种模式）→ new_task(goal)（返回 TaskRequestBuilder 链式构建任务）→ run_task(request)（执行图工作流，支持 7 个 overload 签名，返回 str/dict/Pydantic 模型/None）→ clean()（清理资源）。低层是 `Builders` 命名空间（BuildersWrapper 单例），提供 `Builders.AgentConfig`（AgentConfigBuilder）和 `Builders.TaskDefaults`（TaskRequestCommonBuilder）两个流式构建器。AgentConfigBuilder 采用互斥设备配置设计——for_device()、for_cloud_mobile()、for_browserstack()、for_limrun() 不能同时调用，build() 时自动处理 profile 选择（无 profile 自动创建、单 profile 自动选择、多 profile 必须指定默认）。任务执行分两条路径：本地路径创建 MobileUseContext 后通过 get_graph().astream() 流式执行，stream_mode 包含 messages/custom/updates/values 四种；云手机路径委托给 CloudMobileService.run_task_on_cloud_mobile()，本地不运行 Agent 逻辑，通过 httpx 异步调用 Platform API。Task 类维护状态机（pending/running/completed/failed），TaskResult 支持 get_as_model() 将 JSON 结果解析为 Pydantic 模型。

**证据**：
- F-210: Agent 类构造函数接收可选 config，无配置时用 get_default_agent_config()
- F-212~F-213: init() 方法和 _init_internal 支持四种设备模式（cloud_mobile/BrowserStack/Limrun/本地）
- F-214: new_task() 返回 TaskRequestBuilder，支持 with_output_format/with_output_description/with_locked_app_package/with_max_steps/with_trace_recording/with_name 等链式方法
- F-215~F-218: run_task 的 7 个 overload，cloud_mobile 用 PlatformTaskRequest 委托远程，本地路径构建 Context 后 astream 执行
- F-219: 图执行配置 recursion_limit 来自 max_steps（默认 400），stream_mode 为 ["messages", "custom", "updates", "values"]
- F-225: AgentConfig 字段包含 agent_profiles、device_id、device_platform、servers、cloud_mobile_id_or_ref、browserstack_config、limrun_config、video_recording_enabled 等
- F-229~F-231: AgentConfigBuilder 的流式方法清单和互斥校验逻辑
- F-232: AgentProfile 支持 from_file 参数从 JSONC 文件加载 LLM 配置
- F-235~F-237: TaskRequest 泛型类、PlatformTaskRequest、TaskResult.get_as_model()
- F-239: CloudMobileService 通过 httpx.AsyncClient 调用 Platform API

**反常识**：传统 SDK 设计常提供"一个配置对象 + 一个 run 方法"。mobile-use 的双层 API 体现了"80% 用户用高层，20% 用户用低层"的设计哲学：CLI 入口 main.py 只需要约 10 行代码就完成了从配置构建到任务执行的全流程（F-023），这是高层 API 的价值；但高级用户可能需要自定义 graph_config_callbacks、多 profile 切换、iOS 客户端精细配置等，这些通过 Builders 暴露。更深层的反常识是 AgentConfigBuilder 的设备配置互斥——它不是用一个 device_type 枚举字段加 switch，而是用独立的 for_xxx() 方法在构建期就阻止非法组合，这种"类型状态模式"（typestate pattern）让错误配置在 build() 时即失败，而非延迟到 init() 运行时。云手机路径的"瘦客户端"设计也值得注意：本地 Agent 类不包含任何云手机执行逻辑，所有远程调用封装在 CloudMobileService 中，Agent.run_task 只是根据 config 判断走哪条路径，这符合单一职责原则。

**行动**：
- 快速上手：直接 `Agent()` + `agent.init()` + `agent.run_task(goal="...")` 三行代码即可，使用默认 OpenAI 配置。
- 生产环境：使用 AgentConfigBuilder 显式配置设备和 profile，不要依赖默认值；多 profile 时务必调用 with_default_profile()。
- 需要结构化输出时，定义 Pydantic 模型传给 with_output_format(MyModel)，结果通过 TaskResult.get_as_model(MyModel) 获取。
- 云手机用户使用 PlatformTaskRequest 而非 TaskRequest，record_trace 默认为 True（云执行需要远程 trace）。
- 长时间运行任务时，通过 on_agent_thought 回调实时获取 Agent 思考过程，而非等任务结束后读取 trace 文件。

---

## 知识地图

### 概念文档规划

| 编号 | 文件名 | 标题 | 覆盖事实编号 | 前置依赖 |
|------|--------|------|-------------|---------|
| 00 | 00-overview.md | mobile-use 项目概览 | F-001~F-049 | 无 |
| 01 | 01-multi-agent-architecture.md | 多 Agent 协作架构 | F-050~F-087 | 00 |
| 02 | 02-device-control.md | 设备控制抽象层 | F-100~F-115, F-240~F-255 | 00 |
| 03 | 03-tools-system.md | 工具系统与执行节点 | F-140~F-155 | 01 |
| 04 | 04-llm-configuration.md | LLM 配置与可插拔体系 | F-027~F-044, F-170~F-175 | 00 |
| 05 | 05-sdk-layer.md | SDK 双层 API 与生命周期 | F-210~F-239 | 00, 01 |
| 06 | 06-graph-state.md | 图结构与状态管理 | F-190~F-204, F-045 | 01 |

### 学习路径

1. **入门（理解是什么）**：00 → 01
   - 先建立项目全局视图（定位、CLI、依赖、9 个 Agent 概览），再深入多 Agent 分层架构和 LangGraph 工作流。
2. **核心（理解怎么工作）**：02 → 03 → 06
   - 掌握设备控制三层抽象（Protocol/Factory/Unified），再理解工具系统如何封装设备操作，最后看 State 和 reducer 如何串联整个图。
3. **进阶（理解怎么用）**：04 → 05
   - 理解 LLM 配置体系和 fallback 机制，最后学习 SDK 双层 API 和 Agent 生命周期管理。

### 示例文档规划

| 文件名 | 标题 | 内容要点 |
|--------|------|---------|
| cli-usage.md | CLI 命令使用示例 | mobile-use 主命令的位置参数 goal、--test-name/-n、--traces-path/-p、--output-description/-o、WDA/IDB 相关选项、--with-video-recording-tools、--device-type/-d、--limrun-platform 等参数的实际用法 |
