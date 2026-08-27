---
type: Concept
title: SDK 双层 API 与生命周期
description: Agent类核心入口与四种设备模式、AgentConfigBuilder流式配置、TaskRequestBuilder任务构建、本地与云手机双执行路径
tags: [mobile-use, sdk, agent, builder, task, cloud, limrun]
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

# SDK 双层 API 与生命周期

mobile-use 对外暴露两层 SDK 接口：高层 `Agent` 类封装完整生命周期（初始化→任务创建→执行→清理），低层 `Builders` 命名空间提供流式配置构建器。SDK 支持四种设备模式（本地、云手机、BrowserStack、Limrun），任务执行分本地图执行和云远程执行两条路径。

## Agent 类

`Agent` 是 SDK 的核心入口类，位于 `sdk/agent.py` [F-210]。

### 构造函数

```python
class Agent:
    def __init__(self, *, config: AgentConfig | None = None):
```

构造函数接收可选的 `AgentConfig`。若未提供，调用 `get_default_agent_config()` 创建默认配置（自动检测可用的 LLM profile）[F-210]。构造时初始化以下内部状态：

- `_config`：AgentConfig 实例
- `_tasks: list[Task]`：已创建的任务列表
- `_tmp_traces_dir`：临时 trace 目录（`tempfile/mobile-use-traces`）
- `_initialized: bool`：初始化标志
- `_task_lock: asyncio.Lock`：任务并发锁
- `_adb_client` / `_ui_adb_client` / `_ios_client`：设备客户端
- `_cloud_mobile_id` / `_limrun_instance_id` / `_limrun_controller`：云设备相关

若环境变量中存在 `MINITAP_API_KEY`，构造时自动创建 `PlatformService` 和 `CloudMobileService` 实例 [F-210]。

### init() 初始化

`async def init(api_key=None, server_restart_attempts=3, retry_count=5, retry_wait_seconds=5)` 是初始化设备连接的入口 [F-212]。它启动遥测会话，委托给 `_init_internal()` 执行实际初始化，异常时记录遥测并重新抛出。

`_init_internal` 支持四种设备模式 [F-213]：

1. **cloud_mobile（云手机）**：若 `cloud_mobile_id_or_ref` 已配置，通过 `CloudMobileService.resolve_cloud_mobile_id()` 解析云设备 ID，跳过本地初始化
2. **BrowserStack**：若 `browserstack_config` 已配置，创建 BrowserStack 会话并设置 iOS 客户端
3. **Limrun（云设备）**：若预置了 limrun_android_controller 或 limrun_ios_controller，直接使用；否则根据 limrun_config 创建实例
4. **本地设备**：通过 ADB 连接 Android 设备，或通过 xcrun/idb 连接 iOS 模拟器/物理设备

初始化成功后设置 `_initialized = True`，并记录遥测事件。

### new_task() 创建任务

```python
def new_task(self, goal: str) -> TaskRequestBuilder[None]:
```

返回 `TaskRequestBuilder` 实例，支持链式调用配置任务 [F-214]：

| 方法 | 用途 |
|------|------|
| `with_output_format(model_class)` | 设置 Pydantic 输出模型 |
| `with_output_description(description)` | 设置输出描述 |
| `with_locked_app_package(package)` | 锁定应用包名（防止导航离开） |
| `using_profile(profile_name)` | 指定使用的 AgentProfile |
| `with_max_steps(steps)` | 最大执行步数（默认 RECURSION_LIMIT=400） |
| `with_trace_recording(path)` | 启用 trace 录制 |
| `with_name(name)` | 设置任务名称 |
| `with_thoughts_output_saving(path)` | 保存 Agent 思考过程到文件 |
| `with_llm_output_saving(path)` | 保存 LLM 输出到文件 |
| `build()` | 构建 TaskRequest 对象 |

### run_task() 执行任务

`run_task` 有 7 个 `@overload` 签名，支持 goal 字符串或 request 对象，支持 TaskRequest 和 PlatformTaskRequest，返回类型可以是 str、dict、泛型 TOutput（Pydantic 模型）或 None [F-215]。

执行路径分两条：

**云手机路径**：若 config 配置了 cloud_mobile_id_or_ref，要求使用 `PlatformTaskRequest`，委托给 `_run_cloud_mobile_task()` [F-216][F-217]。该方法通过 `CloudMobileService.run_task_on_cloud_mobile()` 远程执行，本地不运行 Agent 图逻辑，支持状态回调和日志回调。

**本地路径**：`_run_task()` 方法 [F-218]：
1. 创建 Task 对象
2. 构建 MobileUseContext（包含设备上下文、LLM 配置、客户端、回调等）
3. 准备 tracing（若启用）
4. 处理应用安装和锁定
5. 准备输出文件
6. 通过 `get_graph(context).astream()` 流式执行图，stream_mode 为 `["messages", "custom", "updates", "values"]` [F-219]
7. 图执行完成后提取输出，调用 outputter 生成最终结果
8. 调用 `task.finalize()` 完成任务

图执行的 `recursion_limit` 来自 `task.request.max_steps`，防止无限循环。

### 其他方法

| 方法 | 用途 |
|------|------|
| `install_apk(apk_path)` | 安装 Android APK（支持本地和云手机）[F-220] |
| `install_app(app_path)` | 安装应用（Android APK 或 iOS .app）[F-221] |
| `get_screenshot()` | 获取截图（支持所有设备模式）[F-222] |
| `stop_current_task()` | 取消当前运行的 asyncio.Task [F-224] |
| `clean(force=False)` | 清理资源（云手机、Limrun、iOS 客户端、遥测）[F-223] |

`install_app` 对 iOS Limrun 设备使用基于 diff 的 patch syncing 同步 .app 文件夹，返回 bundle_id。

## AgentConfig 与 Builder

### AgentConfig

`AgentConfig` 是 SDK 配置的核心数据类 [F-225]：

| 字段 | 类型 | 用途 |
|------|------|------|
| `agent_profiles` | `list[AgentProfile]` | LLM 配置 profile 列表 |
| `task_request_defaults` | `TaskRequestCommon` | 任务默认配置 |
| `default_profile` | `str \| None` | 默认 profile 名称 |
| `device_id` | `str \| None` | 设备 ID |
| `device_platform` | `DevicePlatform \| None` | 平台（android/ios） |
| `servers` | `ServerConfig \| None` | ADB 服务器配置 |
| `graph_config_callbacks` | `Callbacks` | LangGraph 回调 |
| `cloud_mobile_id_or_ref` | `str \| None` | 云手机 ID/引用 |
| `ios_client_config` | `IosClientConfig \| None` | iOS 客户端配置 |
| `browserstack_config` | `BrowserStackConfig \| None` | BrowserStack 配置 |
| `video_recording_enabled` | `bool` | 视频工具开关 |
| `limrun_config` | `LimrunConfig \| None` | Limrun 配置 |
| `limrun_android_controller` | 控制器实例 | 预置 Android 控制器 |
| `limrun_ios_controller` | 控制器实例 | 预置 iOS 控制器 |

### AgentProfile

`AgentProfile` 包含 `name: str` 和 `llm_config: LLMConfig` [F-232]。构造函数支持 `from_file: str | None` 参数，从 JSONC 文件加载 LLM 配置，支持用户自定义配置文件而不影响全局 override。

### AgentConfigBuilder

`AgentConfigBuilder` 提供流式接口构建 AgentConfig [F-229]。核心方法：

**Profile 管理**：
- `add_profile(profile)` / `add_profiles(profiles)`：添加 LLM profile
- `with_default_profile(profile)`：设置默认 profile（接收 AgentProfile 对象）

**设备配置（互斥）**：
- `for_device(platform, device_id)`：配置本地设备
- `for_cloud_mobile(cloud_mobile_id_or_ref)`：配置云手机
- `for_browserstack(config)`：配置 BrowserStack
- `for_limrun(config)`：配置 Limrun 云设备

**其他配置**：
- `with_default_task_config(...)`：任务默认值
- `with_adb_server(host, port)`：ADB 服务器
- `with_servers(server_config)`：服务器配置
- `with_graph_config_callbacks(callbacks)`：图回调
- `with_ios_client_config(config)`：iOS 客户端
- `with_limrun_android_controller(controller)` / `with_limrun_ios_controller(controller)`：注入预置控制器
- `with_video_recording_tools()`：启用视频工具
- `build(validate_profiles=True)`：构建 AgentConfig

**互斥校验**：for_device/for_cloud_mobile/for_browserstack/for_limrun/with_limrun_*_controller 不能同时设置，否则 build() 时抛出异常 [F-230]。这是一种类型状态模式，在构建期即阻止非法组合。

**自动 profile 选择**：build() 时若 profile 列表为空，自动创建默认 profile（优先 minitap，其次 OpenAI）；只有一个 profile 时自动选择；多个 profile 时必须调用 with_default_profile [F-231]。

### Builders 命名空间

`Builders` 是 `BuildersWrapper` 的单例实例 [F-229]：

```python
class BuildersWrapper:
    @property
    def AgentConfig(self) -> AgentConfigBuilder:
        return AgentConfigBuilder()

    @property
    def TaskDefaults(self) -> TaskRequestCommonBuilder:
        return TaskRequestCommonBuilder()

Builders = BuildersWrapper()
```

使用方式：

```python
config = Builders.AgentConfig.with_default_profile(profile).for_device(...).build()
```

每次访问属性返回新的 Builder 实例，保证线程安全。

## Task 类型体系

### TaskRequest

`TaskRequest[TOutput]` 继承 `TaskRequestCommon` [F-235]：

| 字段 | 类型 | 默认值 | 用途 |
|------|------|--------|------|
| `goal` | `str` | 必填 | 任务目标 |
| `profile` | `str \| None` | None | 使用的 profile 名 |
| `task_name` | `str \| None` | None | 任务名 |
| `output_description` | `str \| None` | None | 输出描述 |
| `output_format` | `type[BaseModel] \| None` | None | Pydantic 输出模型 |
| `enable_remote_tracing` | `bool` | False | 远程 tracing |

`TaskRequestBase` 定义了通用字段 [F-233]：`max_steps`（默认 400）、`record_trace`（默认 False）、`trace_path`（默认 "mobile-use-traces"）、`llm_output_path`、`thoughts_output_path`。

`TaskRequestCommon` 新增 `locked_app_package` 和 `app_path` [F-234]。

### PlatformTaskRequest

`PlatformTaskRequest[TOutput]` 用于云手机执行 [F-236]：

- `task: str | ManualTaskConfig`：任务标识或手动任务配置
- `execution_origin: str = "sdk"`：执行来源
- `record_trace: bool = True`：云执行默认启用 trace
- `task_run_id_available_event` / `task_run_id`：异步任务 ID 同步

### TaskResult

任务执行结果 [F-237]：

- `content`：结果内容（str/dict/None）
- `error`：错误信息
- `execution_time_seconds`：执行耗时
- `steps_taken`：执行步数
- `get_as_model(model_class)`：将 content 解析为 Pydantic 模型

### Task 运行时对象

`Task` 类维护任务运行时状态 [F-238]：id、device（DeviceContext）、status（TaskRunStatus 枚举）、status_message、on_status_changed 回调、request、created_at、ended_at、result。核心方法：

- `finalize()`：标记任务完成，计算耗时
- `get_name()`：获取任务名
- `set_status(status, message)`：更新状态并触发回调

## CloudMobileService

`CloudMobileService` 管理云手机任务的远程执行 [F-239]，使用 `httpx.AsyncClient` 调用 Minitap Platform API。核心方法：

| 方法 | 用途 |
|------|------|
| `start_and_wait_for_ready()` | 启动云手机并等待就绪 |
| `resolve_cloud_mobile_id(id_or_ref)` | 解析云手机 ID（支持名称引用） |
| `run_task_on_cloud_mobile(...)` | 在云手机上远程执行任务 |
| `cancel_task_runs(task_run_id)` | 取消远程任务 |
| `get_screenshot(cloud_mobile_id)` | 获取云手机截图 |
| `install_apk(cloud_mobile_id, apk_path)` | 安装 APK（含签名 URL 上传三步流程） |

云手机路径下，本地 Agent 类不包含任何设备控制逻辑，所有操作通过 HTTP API 委托给云端。

## CLI 中的 SDK 使用

CLI 入口 `run_automation` 展示了 SDK 的最小使用方式 [F-023]：

```python
llm_config = initialize_llm_config()
agent_profile = AgentProfile(name="default", llm_config=llm_config)
config = Builders.AgentConfig.with_default_profile(profile=agent_profile)
if video_recording_tools_enabled:
    config.with_video_recording_tools()

agent = Agent(config=config.build())
await agent.init()
task = agent.new_task(goal)
await agent.run_task(request=task.build())
await agent.clean()
```

约 10 行核心代码即完成从配置到执行的全流程，体现了高层 API 的简洁性。

## 相关概念

- [多 Agent 协作架构](/concepts/01-multi-agent-architecture.md)
- [LLM 配置与可插拔体系](/concepts/04-llm-configuration.md)
- [设备控制抽象层](/concepts/02-device-control.md)
- [图结构与状态管理](/concepts/06-graph-state.md)
- [CLI 命令使用示例](/examples/cli-usage.md)
