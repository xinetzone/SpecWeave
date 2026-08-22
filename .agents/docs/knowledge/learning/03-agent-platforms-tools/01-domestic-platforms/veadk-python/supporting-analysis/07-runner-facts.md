---
id: 07-runner-facts
title: Runner 类事实记录
source: veadk-python codebase analysis
---

# Runner 类事实记录

## Runner 类签名和继承关系

- 文件位置：veadk/runner.py:329
- 类定义：`class Runner(ADKRunner):`
- 继承关系：继承自 `google.adk.runners.Runner`（别名为 ADKRunner）

## 构造函数参数

构造函数位置：veadk/runner.py:355-365

```python
def __init__(
    self,
    agent: BaseAgent | Agent | None = None,
    short_term_memory: ShortTermMemory | None = None,
    app_name: str | None = None,
    user_id: str = "veadk_default_user",
    upload_inline_data_to_tos: bool = False,
    run_processor: "BaseRunProcessor | None" = None,
    *args,
    **kwargs,
) -> None:
```

## 核心属性列表

| 属性名 | 类型 | 默认值/赋值位置 | 说明 |
|--------|------|----------------|------|
| user_id | str | 构造函数参数 user_id，默认 "veadk_default_user" | 默认用户ID |
| long_term_memory | Any | 构造函数第397行初始化为 None，后续从 agent 或 memory_service 获取 | 长期记忆服务实例 |
| upload_inline_data_to_tos | bool | 构造函数参数 | 是否将内联媒体上传到TOS |
| short_term_memory | ShortTermMemory \| None | 构造函数参数，若未提供则从 agent.short_term_memory 获取 | 短期记忆实例 |
| run_processor | BaseRunProcessor | 构造函数第407-414行设置，优先级：runner参数 > agent.run_processor > NoOpRunProcessor | 运行处理器 |
| app_name | str | 传递给父类构造函数，默认 "veadk_default_app" | 应用名称 |

（继承自父类 ADKRunner 的属性：session_service、memory_service、agent、credential_service 等）

## 公开方法列表

### 1. run 方法
- 位置：veadk/runner.py:468-576
- 方法签名：
  ```python
  async def run(
      self,
      messages: RunnerMessage,
      user_id: str = "",
      session_id: str = f"tmp-session-{formatted_timestamp()}",
      run_config: RunConfig | None = None,
      save_tracing_data: bool = False,
      upload_inline_data_to_tos: bool = False,
      run_processor: "BaseRunProcessor | None" = None,
  ):
  ```
- 功能描述：执行多轮文本和多模态输入的对话。输入会被转换为 ADK 消息格式，配置短期记忆时自动创建会话，支持临时启用媒体上传，返回最后一个事件的文本输出。

### 2. get_trace_id 方法
- 位置：veadk/runner.py:578-607
- 方法签名：`def get_trace_id(self) -> str:`
- 功能描述：从当前 agent 的 tracer 获取 Trace ID，agent 不是 VeADK Agent 或无 tracer 时返回 "<unknown_trace_id>"。

### 3. _print_trace_id 方法
- 位置：veadk/runner.py:609-638
- 方法签名：`def _print_trace_id(self) -> None:`
- 功能描述：记录当前 tracer 的 Trace ID 到日志，agent 不是 VeADK Agent 或无 tracer 时记录 warning 日志。

### 4. save_tracing_file 方法
- 位置：veadk/runner.py:640-694
- 方法签名：`def save_tracing_file(self, session_id: str) -> str:`
- 功能描述：将 tracing 数据转储到磁盘并返回最后写入的路径。仅当 agent 是 Agent/SequentialAgent/ParallelAgent/LoopAgent 类型且配置了 tracer 时有效。

### 5. save_eval_set 方法
- 位置：veadk/runner.py:696-729
- 方法签名：`async def save_eval_set(self, session_id: str, eval_set_id: str = "default") -> str:`
- 功能描述：将当前会话保存为评估集的一部分并返回其路径。

### 6. save_session_to_long_term_memory 方法
- 位置：veadk/runner.py:731-789
- 方法签名：
  ```python
  async def save_session_to_long_term_memory(
      self, session_id: str, user_id: str = "", app_name: str = "", **kwargs
  ) -> None:
  ```
- 功能描述：将指定会话保存到长期记忆。未配置 long_term_memory 时记录 warning 日志并返回。

## 运行时会话管理相关字段

### 构造函数中的会话服务选择逻辑（veadk/runner.py:396-462）

1. 第399-401行：从 kwargs 中弹出 credential_service、session_service、memory_service
2. 第402-404行：若未提供 short_term_memory，使用 agent.short_term_memory
3. 第416-421行：若提供了 session_service 且同时提供了 short_term_memory，输出 warning 日志，使用 runner 参数提供的 session_service
4. 第422-434行：若未提供 session_service：
   - 若有 short_term_memory：使用 short_term_memory.session_service
   - 若无 short_term_memory：创建新的 ShortTermMemory() 实例，使用其 session_service
5. 第436-441行：若提供了 memory_service 且 agent 有 long_term_memory，输出 warning 日志，使用 runner 参数提供的 memory_service，同时设置 self.long_term_memory
6. 第443-448行：若未提供 memory_service：
   - 若 agent 有 long_term_memory：设置 self.long_term_memory 和 memory_service
   - 否则：输出 info 日志提示无长期记忆
7. 第451-452行：若 kwargs 中无 app 且未提供 app_name，设置 app_name 为 "veadk_default_app"
8. 第454-462行：调用父类构造函数
9. 第464-466行：使用 MethodType 包装 run_async 方法，注入 intercept_new_message(_upload_image_to_tos) 装饰器

### run 方法中的会话管理逻辑（veadk/runner.py:526-535）

- 第526-535行：若 self.short_term_memory 存在，调用 `self.short_term_memory.create_session(app_name=self.app_name, user_id=user_id, session_id=session_id)` 创建或获取会话，使用 assert 验证会话创建成功。

## 模块级辅助函数

### 1. pre_run_process
- 位置：veadk/runner.py:55-86
- 异步函数，在 agent 执行前调用，遍历 new_message 的 parts，当 part 包含 inline_data 且启用上传时，调用 process_func 处理数据。

### 2. post_run_process
- 位置：veadk/runner.py:89-104
- 函数，agent 运行后执行，当前为空操作占位符。

### 3. intercept_new_message
- 位置：veadk/runner.py:107-198
- 装饰器工厂函数，在 run_async 调用前后插入 pre/post 钩子，内部包含 thinking_parts 聚合逻辑和事件日志记录。

### 4. _convert_messages
- 位置：veadk/runner.py:201-277
- 函数，将 VeADK RunnerMessage 转换为 Google ADK 消息列表，支持 str、MediaMessage、list 类型输入。

### 5. _upload_image_to_tos
- 位置：veadk/runner.py:280-326
- 异步函数，将消息 part 中的内联媒体数据上传到 TOS 并重写其 URL。

## RunnerMessage 类型别名

- 位置：veadk/runner.py:46-52
- 定义：
  ```python
  RunnerMessage = Union[
      str,
      list[str],
      MediaMessage,
      list[MediaMessage],
      list[MediaMessage | str],
  ]
  ```

---

本文档记录了 Runner 类的继承关系、构造函数参数、核心属性、6个公开方法及运行时会话管理相关字段。本文档包含模块级辅助函数和 RunnerMessage 类型别名的客观描述。所有内容均从代码中提取，未包含主观评价。
