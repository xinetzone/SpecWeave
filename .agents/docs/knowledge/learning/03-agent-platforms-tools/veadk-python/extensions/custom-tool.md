---
id: custom-tool
title: 自定义工具开发完整指南
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# 自定义工具开发完整指南

本文档详细介绍如何在 VeADK 中开发自定义工具，包括函数式工具、类式工具和工具集（Toolset）的开发方法。

---

## 一、工具开发基础

VeADK 基于 Google ADK 的工具系统，提供三种工具开发方式：

| 方式 | 适用场景 | 基类/装饰器 | 参考实现 |
|---|---|---|---|
| **函数式工具** | 简单无状态工具 | Python 函数（带类型提示） | [web_search.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/web_search.py#L31-L118) |
| **类式工具** | 需要状态管理、复杂参数、Tracing | `google.adk.tools.BaseTool` | [skills_tool.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/skills_tools/skills_tool.py#L36-L567) |
| **工具集（Toolset）** | 多个相关工具的组合 | `google.adk.tools.base_toolset.BaseToolset` | [vanna_toolset.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/vanna_tools/vanna_toolset.py#L44-L262) |

### 核心概念

- **工具描述（Description）**：LLM 通过工具的 docstring/description 来判断何时调用该工具，描述质量直接影响工具选择的准确性
- **参数类型系统**：基于 Google GenAI 的 `types.Schema` 定义参数结构，支持字符串、数字、布尔、对象、数组等类型
- **ToolContext**：工具执行上下文，可访问会话状态（state）、会话ID、用户ID等运行时信息
- **同步/异步**：函数式工具支持同步和异步（`async def`），类式工具统一实现 `run_async()` 方法

---

## 二、完整开发步骤

### 步骤1：定义工具

根据工具复杂度选择合适的实现方式：

- **简单工具**：使用函数式工具，编写带类型提示和 docstring 的 Python 函数
- **有状态工具**：使用类式工具，继承 `BaseTool` 并实现必要方法
- **工具组合**：使用 Toolset，继承 `BaseToolset` 并管理多个相关工具

### 步骤2：实现工具逻辑

- 函数式工具：直接在函数体内实现逻辑
- 类式工具：在 `run_async()` 方法中实现逻辑，在 `_get_declaration()` 中定义参数Schema
- 工具集：在 `_post_init()` 中初始化所有子工具，在 `get_tools()` 中返回工具列表

### 步骤3：注册工具

在构造 `Agent` 时通过 `tools=[...]` 参数传入：

```python
agent = Agent(
    name="my_agent",
    instruction="...",
    tools=[my_function_tool, MyClassTool(), MyToolset(...)],
)
```

### 步骤4：测试工具

- 编写单元测试验证工具输入输出
- 编写集成测试验证 LLM 能正确选择和调用工具
- 参考 `examples/02_custom_tools/main.py` 进行端到端测试

---

## 三、代码模板

### 模板1：函数式工具

```python
from google.adk.tools import ToolContext


def my_simple_tool(
    param1: str,
    param2: int = 10,
    tool_context: ToolContext | None = None,
) -> dict[str, str]:
    """工具的一句话功能描述（LLM会首先看到这句）。

    详细说明工具的使用场景、注意事项等。
    这段描述帮助LLM判断何时应该调用此工具。

    Args:
        param1: 参数1的说明，说明其用途、格式要求等。
        param2: 参数2的说明，含默认值说明。
        tool_context: 工具上下文对象，用于访问会话状态等（可选）。

    Returns:
        返回值说明，描述返回数据的结构和含义。
    """
    # 实现工具逻辑
    try:
        # 业务逻辑
        result = f"Processed {param1} with param2={param2}"
        return {"result": result}
    except Exception as e:
        # 错误处理：返回错误信息字符串，而非抛出异常
        return {"error": f"Tool execution failed: {str(e)}"}
```

**参考实现**：[get_city_weather](file:///d:/AI/.chaos/libs/veadk-python/examples/02_custom_tools/main.py#L27-L41)、[web_search](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/web_search.py#L31-L118)

### 模板2：异步函数式工具

```python
import asyncio
from google.adk.tools import ToolContext


async def my_async_tool(
    query: str,
    timeout: int = 30,
    tool_context: ToolContext | None = None,
) -> str:
    """异步工具功能描述。

    适用于需要IO操作（网络请求、文件读写等）的场景。

    Args:
        query: 查询参数。
        timeout: 超时时间（秒）。
        tool_context: 工具上下文。

    Returns:
        处理结果字符串。
    """
    # 使用 asyncio.to_thread 包装同步IO操作
    def blocking_io():
        # 同步操作
        import time
        time.sleep(1)
        return f"Result for {query}"

    result = await asyncio.to_thread(blocking_io)
    return result
```

### 模板3：类式工具（BaseTool）

```python
from __future__ import annotations
from typing import Any, Dict
from google.adk.tools import BaseTool, ToolContext
from google.genai import types


class MyStatefulTool(BaseTool):
    """带状态的类式工具，适用于需要维护配置或复杂参数Schema的场景。"""

    def __init__(self, config_param: str = "default"):
        """初始化工具，可接收配置参数。

        Args:
            config_param: 工具配置参数。
        """
        self.config_param = config_param

        super().__init__(
            name="my_stateful_tool",
            description=(
                "工具功能描述。\n\n"
                "详细说明工具用途、适用场景、参数含义。"
            ),
        )

    def _get_declaration(self) -> types.FunctionDeclaration:
        """定义工具的参数Schema，这是LLM看到的工具接口定义。"""
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "input_text": types.Schema(
                        type=types.Type.STRING,
                        description="输入文本的说明",
                    ),
                    "max_items": types.Schema(
                        type=types.Type.INTEGER,
                        description="最大条目数",
                    ),
                    "verbose": types.Schema(
                        type=types.Type.BOOLEAN,
                        description="是否输出详细信息",
                    ),
                },
                required=["input_text"],
            ),
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> str:
        """执行工具逻辑。

        Args:
            args: LLM传入的参数字典。
            tool_context: 工具执行上下文。

        Returns:
            工具执行结果字符串。
        """
        input_text = args.get("input_text", "")
        max_items = args.get("max_items", 10)
        verbose = args.get("verbose", False)

        try:
            # 实现业务逻辑
            result = self._process(input_text, max_items, verbose, tool_context)
            return result
        except Exception as e:
            return f"Error: {str(e)}"

    def _process(
        self,
        input_text: str,
        max_items: int,
        verbose: bool,
        tool_context: ToolContext,
    ) -> str:
        """内部处理逻辑。"""
        # 可通过 tool_context.state 存取会话状态
        # tool_context.state["some_key"] = "some_value"
        session_id = tool_context.session.id if tool_context else "unknown"
        return f"Processed '{input_text}' (max={max_items}, verbose={verbose}, session={session_id})"
```

**参考实现**：[SkillsTool](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/skills_tools/skills_tool.py#L36-L97)

### 模板4：工具集（BaseToolset）

```python
from __future__ import annotations
from typing import List, Optional
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import BaseTool
from google.adk.tools.base_toolset import BaseToolset


class MyRelatedTool(BaseTool):
    """工具集中的单个工具。"""

    def __init__(self, shared_config: dict):
        self.shared_config = shared_config
        super().__init__(
            name="my_related_tool",
            description="相关工具的功能描述",
        )

    def _get_declaration(self) -> types.FunctionDeclaration:
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "param": types.Schema(
                        type=types.Type.STRING,
                        description="参数说明",
                    ),
                },
                required=["param"],
            ),
        )

    async def run_async(self, *, args: dict, tool_context: ToolContext) -> str:
        param = args.get("param", "")
        return f"Result: {param} with config {self.shared_config}"


class MyToolSet(BaseToolset):
    """工具集，将多个相关工具组合在一起，共享配置。"""

    def __init__(self, connection_string: str, config_value: str = "default"):
        super().__init__()
        self.connection_string = connection_string
        self.config_value = config_value
        self._post_init()

    def _post_init(self):
        """初始化工具集中的所有工具，共享配置。"""
        shared_config = {
            "connection": self.connection_string,
            "config": self.config_value,
        }

        self._tools = {
            "my_related_tool": MyRelatedTool(shared_config),
            # 可以添加更多相关工具
        }

    async def get_tools(
        self, readonly_context: Optional[ReadonlyContext] = None
    ) -> List[BaseTool]:
        """返回工具集中的所有工具列表。"""
        return list(self._tools.values())
```

**参考实现**：[VannaToolSet](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/vanna_tools/vanna_toolset.py#L44-L262)

---

## 四、工具参数类型系统

VeADK 使用 Google GenAI 的 Schema 系统定义工具参数，支持以下类型：

| Schema 类型 | Python 类型 | 说明 |
|---|---|---|
| `types.Type.STRING` | `str` | 字符串 |
| `types.Type.INTEGER` | `int` | 整数 |
| `types.Type.NUMBER` | `float` | 浮点数 |
| `types.Type.BOOLEAN` | `bool` | 布尔值 |
| `types.Type.ARRAY` | `list` | 数组，需指定 `items` |
| `types.Type.OBJECT` | `dict` | 对象，需指定 `properties` |

### 参数定义示例

```python
parameters=types.Schema(
    type=types.Type.OBJECT,
    properties={
        "name": types.Schema(
            type=types.Type.STRING,
            description="名称（必填）",
        ),
        "count": types.Schema(
            type=types.Type.INTEGER,
            description="数量，默认10",
        ),
        "tags": types.Schema(
            type=types.Type.ARRAY,
            description="标签列表",
            items=types.Schema(type=types.Type.STRING),
        ),
        "options": types.Schema(
            type=types.Type.OBJECT,
            description="选项配置",
            properties={
                "verbose": types.Schema(type=types.Type.BOOLEAN),
                "format": types.Schema(type=types.Type.STRING),
            },
        ),
    },
    required=["name"],  # 必填参数列表
)
```

**参考实现**：[SkillsTool._get_declaration()](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/skills_tools/skills_tool.py#L78-L92)

---

## 五、工具描述最佳实践

工具描述（docstring 或 description 参数）是 LLM 选择工具的唯一依据，其质量直接影响工具调用准确率。

### 最佳实践

1. **首句即核心**：docstring 第一句话清晰说明工具功能，LLM 会优先看到这部分
2. **明确使用场景**：说明"什么时候该用这个工具"，而不仅仅是"这个工具做什么"
3. **参数说明详尽**：每个参数的含义、格式要求、取值范围、示例
4. **返回值说明**：说明返回数据的结构，方便 LLM 解析
5. **给出示例**：在描述中包含调用示例，帮助 LLM 理解用法
6. **避免歧义**：不要使用模糊词汇，如"相关信息"、"适当处理"

### 反例 vs 正例

**反例**（描述不清）：
```python
def search_data(query):
    """搜索数据。"""
    ...
```

**正例**（描述清晰）：
```python
def search_database(
    table_name: str,
    query_conditions: dict,
    limit: int = 10,
) -> list[dict]:
    """在指定数据库表中查询符合条件的记录。

    当需要从数据库中检索结构化数据时使用此工具。支持等值查询和范围查询。

    Args:
        table_name: 要查询的表名，可选值：users, orders, products。
        query_conditions: 查询条件字典，格式如 {"status": "active", "age>": 18}。
            支持操作符：=（等值）、>（大于）、<（小于）、like（模糊匹配）。
        limit: 返回结果最大数量，默认10，最大100。

    Returns:
        记录列表，每条记录为字典格式。例如：
        [{"id": 1, "name": "张三", "status": "active"}]
    """
    ...
```

**参考实现**：[web_search 描述](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/web_search.py#L32-L39)、[SkillsTool 描述生成](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/skills_tools/skills_tool.py#L54-L76)

---

## 六、错误处理

工具执行中可能出现各种错误，VeADK 的错误处理原则是：**返回错误信息字符串，而非抛出异常**。

### 错误处理模式

参考 [web_search.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/web_search.py#L110-L118) 的实现：

```python
def my_tool(param: str) -> str | dict:
    try:
        # 业务逻辑
        result = do_something(param)
        return {"result": result}
    except ValueError as e:
        # 参数错误：返回明确的错误提示，LLM可根据提示修正参数
        return f"Invalid parameter: {str(e)}. Please provide a valid value."
    except ConnectionError as e:
        # 外部服务错误：记录日志，返回友好错误信息
        logger.error(f"External service error: {e}")
        return f"Service temporarily unavailable. Please try again later."
    except Exception as e:
        # 未知错误：记录详细日志，返回通用错误信息
        logger.exception(f"Unexpected error in my_tool: {e}")
        return f"Tool execution failed: {type(e).__name__}"
```

### 注意事项

1. **不要抛出未捕获的异常**：未捕获的异常会中断整个 Agent 执行流程
2. **错误信息要有指导性**：告诉 LLM 如何修正问题（如参数格式错误）
3. **敏感信息脱敏**：错误信息中不要包含 API Key、密码等敏感信息
4. **日志分级**：预期内的错误用 warning/debug，未知异常用 error/exception
5. **凭证错误特殊处理**：认证失败可考虑通过 RunProcessor 触发OAuth流程（参考 AuthRequestProcessor）

---

## 七、异步工具开发

VeADK 原生支持异步工具，所有工具最终都会通过异步路径执行。

### 异步工具要点

1. **函数式异步工具**：直接使用 `async def` 定义即可
2. **类式工具**：统一实现 `async def run_async()` 方法
3. **阻塞IO包装**：使用 `asyncio.to_thread()` 包装同步阻塞操作，避免阻塞事件循环
4. **会话状态访问**：通过 `tool_context.state` 异步安全地访问会话状态

### 异步工具模板

```python
import asyncio
import aiohttp
from google.adk.tools import ToolContext


async def async_http_tool(
    url: str,
    method: str = "GET",
    timeout: int = 30,
    tool_context: ToolContext | None = None,
) -> dict:
    """异步HTTP请求工具，用于调用外部API。

    Args:
        url: 请求URL。
        method: HTTP方法，GET/POST/PUT/DELETE。
        timeout: 请求超时秒数。
        tool_context: 工具上下文。

    Returns:
        包含status、headers、body的响应字典。
    """
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            async with session.request(method, url) as resp:
                body = await resp.text()
                return {
                    "status": resp.status,
                    "headers": dict(resp.headers),
                    "body": body[:5000],
                }
    except asyncio.TimeoutError:
        return {"error": f"Request timed out after {timeout} seconds"}
    except aiohttp.ClientError as e:
        return {"error": f"HTTP request failed: {str(e)}"}


def sync_blocking_tool(
    file_path: str,
    tool_context: ToolContext | None = None,
) -> str:
    """包含阻塞IO的工具，同步函数即可（框架自动在线程池中执行）。

    Args:
        file_path: 文件路径。
        tool_context: 工具上下文。

    Returns:
        文件内容。
    """
    # 同步文件操作，框架会自动处理线程调度
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
```

---

## 八、内置工具参考

VeADK 在 `veadk/tools/builtin_tools/` 目录下提供了丰富的内置工具，可作为开发参考：

| 工具 | 文件 | 特点 |
|---|---|---|
| 网页搜索 | [web_search.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/web_search.py) | 火山引擎API签名、多级凭证链 |
| 代码执行 | [run_code.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/run_code.py) | AgentKit沙箱调用、ToolContext使用 |
| 图片生成 | [image_generate.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/image_generate.py) | 多模态API调用 |
| PPT生成 | [ppt_generate.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/ppt_generate.py) | 子进程调用Node.js脚本 |
| TTS语音合成 | [tts.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/tts.py) | 火山引擎语音服务集成 |

### 凭证获取模式

内置工具统一遵循"工具专属环境变量 → ToolContext状态 → 全局环境变量 → IAM角色"的四级凭证链模式，参考 [web_search.py:40-65](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/web_search.py#L40-L65)：

```python
# 1. 工具专属环境变量
ak = os.getenv("TOOL_WEB_SEARCH_ACCESS_KEY")
sk = os.getenv("TOOL_WEB_SEARCH_SECRET_KEY")

# 2. ToolContext状态
if not (ak and sk) and tool_context:
    ak = tool_context.state.get("VOLCENGINE_ACCESS_KEY")
    sk = tool_context.state.get("VOLCENGINE_SECRET_KEY")

# 3. 全局环境变量
if not (ak and sk):
    ak = os.getenv("VOLCENGINE_ACCESS_KEY")
    sk = os.getenv("VOLCENGINE_SECRET_KEY")

# 4. IAM角色（云端部署）
if not (ak and sk):
    credential = get_credential_from_vefaas_iam()
    ak = credential.access_key_id
    sk = credential.secret_access_key
    session_token = credential.session_token
```

---

## 九、工具注册与使用

### 基本注册方式

```python
from veadk import Agent, Runner

# 1. 直接传入工具列表
agent = Agent(
    name="my_agent",
    instruction="使用提供的工具帮助用户完成任务。",
    tools=[
        my_function_tool,      # 函数式工具直接传函数
        MyClassTool(),         # 类式工具传实例
        MyToolSet(conn_str),   # 工具集传实例
    ],
)
```

### 初始化后动态添加工具

Agent 初始化后会自动追加 knowledgebase、memory 等内置工具（参考架构洞察1），也可手动追加：

```python
agent = Agent(...)
# 初始化后添加工具
agent.tools.append(my_extra_tool)
```

### 检查已注册工具

初始化后检查工具列表，确认符合预期：

```python
print("Registered tools:", [t.name for t in agent.tools])
```
