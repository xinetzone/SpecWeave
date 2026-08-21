---
id: tools
title: Tools 工具系统详解
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# Tools 工具系统详解

## 概述

### 什么是 Tool

在 VeADK 中，**Tool（工具）**是 Agent 与外部世界交互的桥梁。Tool 本质上是带有类型提示和文档字符串（docstring）的可调用对象（Python 函数或类），LLM 模型可以根据用户输入自主决定在合适的时机调用合适的工具来完成特定任务。

工具为 Agent 提供了超越纯文本生成的能力，包括：
- **信息获取**：网页搜索、知识库检索、文件读取等
- **内容生成**：图像生成、视频生成、PPT 生成、语音合成等
- **执行操作**：代码运行、命令执行、沙箱操作等
- **UI 交互**：A2UI（Agent 驱动 UI）、隧道连接等

### 为什么 Agent 需要工具

LLM 本身的局限性：
1. **知识截止**：训练数据有时间截止点，无法获取实时信息
2. **无法执行**：只能生成文本，无法执行实际操作或访问外部系统
3. **无持久记忆**：上下文窗口有限，无法跨会话持久化信息
4. **无环境感知**：无法直接访问文件系统、网络或其他资源

工具通过将外部能力封装为模型可调用的函数接口，弥补了这些局限，使 Agent 能够：
- 实时检索最新信息
- 与外部系统和 API 交互
- 执行计算和代码
- 操作文件和数据库
- 生成多模态内容

## 工具注册机制

VeADK 提供两种工具注册方式：**构造函数直接传入**和**自动条件挂载**。

### 方式一：Agent 构造函数直接传 tools 列表

这是最直接的方式，在创建 Agent 实例时通过 `tools` 参数显式传入工具列表。

```python
from veadk import Agent, Runner

def get_city_weather(city: str) -> dict[str, str]:
    """Get the current weather for a city.

    Args:
        city: The English name of the city, e.g. "Beijing".

    Returns:
        A dict with a human-readable weather "result".
    """
    return {"result": "Sunny, 25°C"}

agent = Agent(
    name="weather_agent",
    instruction="You help users with weather queries.",
    tools=[get_city_weather],  # 直接传入工具列表
)
```

代码参考：[veadk/agent.py:126](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L126-L126)

### 方式二：自动条件挂载

Agent 在初始化时（`model_post_init` 方法）会根据配置条件自动挂载相应的工具，无需用户手动添加。自动挂载逻辑位于 [veadk/agent.py:304-438](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L304-L438)。

| 触发条件 | 挂载工具 | 代码位置 |
|---------|---------|---------|
| `self.knowledgebase` 不为 None | `LoadKnowledgebaseTool`；若 `enable_profile=True` 则附加 `load_kb_queries` | [agent.py:306-324](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L306-L324) |
| `self.long_term_memory` 不为 None | `load_memory`（来自 google.adk.tools） | [agent.py:326-333](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L326-L333) |
| `self.skills` 非空 | `SkillsToolset`（技能工具集） | [agent.py:377-600](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L377-L600) |
| `self.example_store` 不为 None | `ExampleTool` | [agent.py:399-402](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L399-L402) |
| `self.enable_ghostchar=True` | `GhostcharTool` | [agent.py:404-410](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L404-L410) |
| `self.enable_a2ui=True` | A2UI Toolset（`build_a2ui_toolset`） | [agent.py:412-416](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L412-L416) |
| `self.enable_tunnel=True` | `TunnelToolset` | [agent.py:418-422](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L418-L422) |

## 内置工具清单

VeADK 的内置工具位于 `veadk/tools/` 目录下，按功能分为多个子目录。

### 目录结构

```
veadk/tools/
├── __init__.py                    # 内置工具注册表
├── demo_tools.py                  # 演示工具
├── ghost_char.py                  # 幽灵字符工具
├── load_history_events.py         # 历史事件加载
├── load_knowledgebase_tool.py     # 知识库工具（旧版）
├── builtin_tools/                 # 标准内置工具
├── mcp_tool/                      # MCP 协议工具
├── sandbox/                       # 沙箱工具
├── skills_tools/                  # 技能相关工具
└── vanna_tools/                   # Vanna 数据分析工具
```

### 工具注册表

`veadk/tools/__init__.py` 维护了一个内置工具注册表 `_BUILTIN_TOOLS`，通过 `get_builtin_tool(name)` 可以按名称懒加载工具：

代码参考：[veadk/tools/__init__.py:26-46](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/__init__.py#L26-L46)

| 工具名 | 模块路径 | 功能分类 |
|-------|---------|---------|
| `web_search` | `veadk.tools.builtin_tools.web_search:web_search` | 网页搜索 |
| `web_fetch` | `veadk.tools.builtin_tools.web_fetch:web_fetch` | 网页抓取 |
| `parallel_web_search` | `veadk.tools.builtin_tools.parallel_web_search:parallel_web_search` | 并行搜索 |
| `vesearch` | `veadk.tools.builtin_tools.vesearch:vesearch` | 火山引擎搜索 |
| `link_reader` | `veadk.tools.builtin_tools.link_reader:link_reader` | 链接读取 |
| `run_code` | `veadk.tools.builtin_tools.run_code:run_code` | 代码执行 |
| `coding` | `veadk.tools.builtin_tools.coding:coding` | 编码工具 |
| `image_generate` | `veadk.tools.builtin_tools.image_generate:image_generate` | 图像生成 |
| `image_edit` | `veadk.tools.builtin_tools.image_edit:image_edit` | 图像编辑 |
| `video_generate` | `veadk.tools.builtin_tools.video_generate:video_generate` | 视频生成 |
| `video_task_query` | `veadk.tools.builtin_tools.video_generate:video_task_query` | 视频任务查询 |
| `ppt_generate` | `veadk.tools.builtin_tools.ppt_generate:ppt_generate` | PPT 生成 |
| `text_to_speech` | `veadk.tools.builtin_tools.tts:text_to_speech` | 语音合成 |
| `get_city_weather` | `veadk.tools.demo_tools:get_city_weather` | 演示：城市天气 |
| `get_location_weather` | `veadk.tools.demo_tools:get_location_weather` | 演示：位置天气 |

### 完整内置工具列表

#### 根目录工具

| 工具名 | 文件路径 | 功能 | 自动挂载条件 | 依赖 |
|-------|---------|------|-------------|------|
| `get_city_weather` | [demo_tools.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/demo_tools.py) | 获取指定城市固定天气数据（演示用） | 否（需手动添加） | 无 |
| `get_location_weather` | [demo_tools.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/demo_tools.py) | 获取随机天气数据（演示用） | 否（需手动添加） | 无 |
| `GhostcharTool` | [ghost_char.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/ghost_char.py) | 幽灵字符工具，确保模型响应以 `<` 开头 | `enable_ghostchar=True` | 无 |
| `LoadKnowledgebaseTool` | [load_knowledgebase_tool.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/load_knowledgebase_tool.py) | 知识库检索工具（旧版） | `knowledgebase` 已设置 | veadk.knowledgebase |

#### builtin_tools/ 标准内置工具

| 工具名 | 文件路径 | 功能 | 自动挂载条件 | 依赖 |
|-------|---------|------|-------------|------|
| `LoadKnowledgebaseTool` | [load_knowledgebase.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/load_knowledgebase.py) | 知识库检索工具 | `knowledgebase` 已设置 | veadk.knowledgebase |
| `load_kb_queries` | [load_kb_queries.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/load_kb_queries.py) | 知识库 Profile 查询工具 | `knowledgebase.enable_profile=True` | 知识库模块 |
| `web_search` | [web_search.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/web_search.py) | 火山引擎网页搜索 | 否（需手动添加） | requests, volcengine sign |
| `web_fetch` | [web_fetch.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/web_fetch.py) | 网页内容抓取 | 否（需手动添加） | httpx |
| `web_scraper` | [web_scraper.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/web_scraper.py) | 网页爬虫工具 | 否（需手动添加） | - |
| `parallel_web_search` | [parallel_web_search.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/parallel_web_search.py) | 并行多搜索引擎搜索 | 否（需手动添加） | asyncio |
| `vesearch` | [vesearch.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/vesearch.py) | 火山引擎向量搜索 | 否（需手动添加） | - |
| `link_reader` | [link_reader.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/link_reader.py) | 链接内容读取解析 | 否（需手动添加） | - |
| `run_code` | [run_code.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/run_code.py) | 代码执行工具 | 否（需手动添加） | - |
| `coding` | [coding.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/coding.py) | 编码辅助工具 | 否（需手动添加） | - |
| `image_generate` | [image_generate.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/image_generate.py) | 图像生成 | 否（需手动添加） | httpx |
| `generate_image` | [generate_image.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/generate_image.py) | 图像生成（另一种实现） | 否（需手动添加） | - |
| `image_edit` | [image_edit.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/image_edit.py) | 图像编辑 | 否（需手动添加） | - |
| `video_generate` | [video_generate.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/video_generate.py) | 视频生成 | 否（需手动添加） | httpx |
| `video_task_query` | [video_generate.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/video_generate.py) | 视频生成任务状态查询 | 与 `video_generate` 自动配对 | httpx |
| `ppt_generate` | [ppt_generate.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/ppt_generate.py) | PPT 文档生成 | 否（需手动添加） | Node.js (ppt_generate.mjs) |
| `tts` | [tts.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/tts.py) | 文本转语音 | 否（需手动添加） | - |
| `vod` | [vod.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/vod.py) | 视频点播工具 | 否（需手动添加） | - |
| `playwright` | [playwright.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/playwright.py) | Playwright 浏览器自动化 | 否（需手动添加） | playwright |
| `mcp_router` | [mcp_router.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/mcp_router.py) | MCP 工具路由 | 否（需手动添加） | mcp |
| `a2a_registry` | [a2a_registry.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/a2a_registry.py) | A2A 代理注册中心 | 否（需手动添加） | - |
| `agent_authorization` | [agent_authorization.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/agent_authorization.py) | Agent 授权检查回调 | `enable_authz=True` | - |
| `execute_skills` | [execute_skills.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/execute_skills.py) | 技能执行工具（沙箱模式） | 通过 SkillsToolset 间接使用 | - |
| `lark` | [lark.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/lark.py) | 飞书集成工具 | 否（需手动添加） | lark-oapi |
| `las` | [las.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/las.py) | LAS 日志服务工具 | 否（需手动添加） | - |
| `llm_shield` | [llm_shield.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/llm_shield.py) | LLM 安全防护 | 否（需手动添加） | - |
| `mobile_run` | [mobile_run.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/mobile_run.py) | 移动端运行工具 | 否（需手动添加） | - |
| `run_sandbox_agent` | [run_sandbox_agent.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/run_sandbox_agent.py) | 沙箱 Agent 运行 | 否（需手动添加） | - |
| `supabase_toolset` | [supabase_toolset.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/supabase_toolset.py) | Supabase 工具集 | 否（需手动添加） | supabase |
| `_agentkit` | [_agentkit.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/_agentkit.py) | AgentKit 内部工具 | 内部使用 | - |

#### mcp_tool/ MCP 协议工具

| 工具名/类 | 文件路径 | 功能 | 自动挂载条件 | 依赖 |
|----------|---------|------|-------------|------|
| `TrustedMcpToolset` | [trusted_mcp_toolset.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/mcp_tool/trusted_mcp_toolset.py) | 可信 MCP 服务器连接工具集 | 否（需手动添加） | mcp, google.adk mcp |
| `TrustedMcpSessionManager` | [trusted_mcp_session_manager.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/mcp_tool/trusted_mcp_session_manager.py) | MCP 会话管理器 | TrustedMcpToolset 内部使用 | mcp |

#### sandbox/ 沙箱工具

| 工具名 | 文件路径 | 功能 | 自动挂载条件 | 依赖 |
|-------|---------|------|-------------|------|
| `browser_sandbox` | [browser_sandbox.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/sandbox/browser_sandbox.py) | 浏览器沙箱 | 否（需手动添加） | - |
| `code_sandbox` | [code_sandbox.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/sandbox/code_sandbox.py) | 代码沙箱 | 否（需手动添加） | - |
| `computer_sandbox` | [computer_sandbox.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/sandbox/computer_sandbox.py) | 计算机操作沙箱 | 否（需手动添加） | - |

#### skills_tools/ 技能相关工具

| 工具名 | 文件路径 | 功能 | 自动挂载条件 | 依赖 |
|-------|---------|------|-------------|------|
| `SkillsToolset` | [skills_toolset.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/skills_tools/skills_toolset.py) | 技能工具集（含文件操作、命令执行等） | `skills` 非空时自动挂载 | veadk.skills |
| `SkillsTool` | [skills_tool.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/skills_tools/skills_tool.py) | 技能发现和加载工具 | SkillsToolset 内部 | - |
| `bash_tool` | [bash_tool.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/skills_tools/bash_tool.py) | Shell 命令执行工具 | SkillsToolset 内部（local模式） | - |
| `file_tool` | [file_tool.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/skills_tools/file_tool.py) | 文件读写编辑工具 | SkillsToolset 内部（local模式） | - |
| `download_skills_tool` | [download_skills_tool.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/skills_tools/download_skills_tool.py) | 技能下载工具 | SkillsToolset 内部 | - |
| `register_skills_tool` | [register_skills_tool.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/skills_tools/register_skills_tool.py) | 技能注册工具 | SkillsToolset 内部 | - |
| `session_path` | [session_path.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/skills_tools/session_path.py) | 会话路径工具 | SkillsToolset 内部 | - |

#### vanna_tools/ Vanna 数据分析工具

| 工具名 | 文件路径 | 功能 | 自动挂载条件 | 依赖 |
|-------|---------|------|-------------|------|
| `VannaToolset` | [vanna_toolset.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/vanna_tools/vanna_toolset.py) | Vanna AI 数据分析工具集 | 否（需手动添加） | vanna |
| `run_sql` | [run_sql.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/vanna_tools/run_sql.py) | SQL 执行工具 | VannaToolset 内部 | - |
| `python` | [python.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/vanna_tools/python.py) | Python 执行工具 | VannaToolset 内部 | - |
| `file_system` | [file_system.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/vanna_tools/file_system.py) | 文件系统工具 | VannaToolset 内部 | - |
| `summarize_data` | [summarize_data.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/vanna_tools/summarize_data.py) | 数据摘要工具 | VannaToolset 内部 | - |
| `visualize_data` | [visualize_data.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/vanna_tools/visualize_data.py) | 数据可视化工具 | VannaToolset 内部 | - |
| `agent_memory` | [agent_memory.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/vanna_tools/agent_memory.py) | Agent 记忆工具 | VannaToolset 内部 | - |
| `vikingdb_agent_memory` | [vikingdb_agent_memory.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/vanna_tools/vikingdb_agent_memory.py) | VikingDB 记忆工具 | VannaToolset 内部 | - |
| `vanna_trainer` | [vanna_trainer.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/vanna_tools/vanna_trainer.py) | Vanna 训练工具 | VannaToolset 内部 | - |

## 工具依赖自动补全机制

Agent 在初始化时会调用 `_validate_tool_dependencies()` 方法检查工具依赖关系，目前仅实现了视频生成工具对的自动补全。

代码参考：[veadk/agent.py:614-643](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L614-L643)

### 执行流程

```
1. 收集所有已挂载工具的名称到 tool_names 集合
2. 检查是否存在 video_generate
3. 检查是否存在 video_task_query
4. 如果只有 video_generate 没有 video_task_query：
   - 输出 warning 日志
   - 自动添加 video_task_query
5. 如果只有 video_task_query 没有 video_generate：
   - 输出 warning 日志
   - 自动添加 video_generate
```

这种互补机制确保视频生成任务能够正常查询状态，避免用户遗漏配对工具。

## 自定义工具开发指南

VeADK 基于 Google ADK 构建，工具开发遵循 ADK 的工具规范。有两种自定义工具方式：**函数工具**和**类工具**。

### 方式一：函数工具（最简单）

最简单的工具就是一个带有类型提示和文档字符串的普通 Python 函数。

**要求：**
1. 函数必须有类型注解（参数类型和返回值类型）
2. 函数必须有清晰的 docstring，描述工具功能、参数和返回值
3. docstring 是给模型看的，需要清晰说明何时以及如何使用该工具

**示例：**

```python
def recommend_clothing(temperature_celsius: int) -> dict[str, str]:
    """Recommend what to wear for a given temperature.

    Args:
        temperature_celsius: The temperature in degrees Celsius.

    Returns:
        A dict with a clothing "result" suggestion.
    """
    if temperature_celsius < 10:
        advice = "Wear a thick coat."
    elif temperature_celsius < 23:
        advice = "A light jacket is enough."
    else:
        advice = "T-shirt weather."
    return {"result": advice}
```

代码参考：[examples/02_custom_tools/main.py:44-59](file:///d:/AI/.chaos/libs/veadk-python/examples/02_custom_tools/main.py#L44-L59)

### 方式二：继承 BaseTool（类工具）

对于需要维护状态或更复杂逻辑的工具，可以继承 `google.adk.tools.BaseTool` 或 `google.adk.tools.FunctionTool`。

**必要方法：**
- `__init__()`: 初始化，调用 `super().__init__(name=..., description=...)`
- 对于 `FunctionTool`：传入一个可调用对象
- 对于需要干预 LLM 请求的工具：重写 `process_llm_request()` 方法

**完整代码模板：**

```python
from __future__ import annotations
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.models.llm_request import LlmRequest
from typing_extensions import override
from veadk.utils.logger import get_logger

logger = get_logger(__name__)

class MyCustomTool(BaseTool):
    """我的自定义工具，用于 XXXXX 功能。

    在这里详细描述工具的用途，让模型知道何时应该调用此工具。
    """

    def __init__(self, custom_param: str = "default"):
        super().__init__(
            name="my_custom_tool",
            description=(
                "Description of what this tool does. "
                "Explain when the model should call this tool. "
                "Detail each parameter clearly."
            ),
        )
        self.custom_param = custom_param

    @override
    async def process_llm_request(
        self, *, tool_context: ToolContext, llm_request: LlmRequest
    ) -> None:
        """如果需要在 LLM 请求处理阶段进行干预（如修改请求），重写此方法。

        可选，不是所有工具都需要。
        """
        await super().process_llm_request(
            tool_context=tool_context, llm_request=llm_request
        )
        # 自定义逻辑...

    async def run_async(
        self, *, tool_context: ToolContext, **kwargs
    ) -> dict | str:
        """工具的核心执行逻辑。

        Args:
            tool_context: 工具上下文，可访问 state、session 等
            **kwargs: 模型传入的参数，需与 _get_declaration 中定义一致

        Returns:
            工具执行结果，会返回给模型
        """
        # 实现工具逻辑
        result = f"Processed with param: {self.custom_param}, args: {kwargs}"
        return {"result": result}
```

**FunctionTool 继承示例（参考 LoadKnowledgebaseTool）：**

```python
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.adk.models.llm_request import LlmRequest
from google.genai import types
from pydantic import BaseModel, Field
from typing_extensions import override

class MyResponse(BaseModel):
    result: str = Field(description="The result of the operation")

class MyCustomFunctionTool(FunctionTool):
    def __init__(self, config: dict):
        super().__init__(self.my_function)
        self.config = config

    @override
    def _get_declaration(self) -> types.FunctionDeclaration | None:
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(
                        type=types.Type.STRING,
                        description="The query parameter",
                    ),
                },
                required=["query"],
            ),
        )

    async def my_function(self, query: str, tool_context: ToolContext) -> MyResponse:
        """工具功能描述。

        Args:
            query: 查询参数说明

        Returns:
            MyResponse 对象
        """
        return MyResponse(result=f"Processed: {query}")

    @override
    async def process_llm_request(
        self, *, tool_context: ToolContext, llm_request: LlmRequest
    ) -> None:
        await super().process_llm_request(
            tool_context=tool_context, llm_request=llm_request
        )
        # 自定义请求处理...
```

代码参考：[veadk/tools/builtin_tools/load_knowledgebase.py:39-100](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/load_knowledgebase.py#L39-L100)

### 方式三：使用 Toolset（工具集）

当需要将多个相关工具组织在一起时，可以继承 `google.adk.tools.base_toolset.BaseToolset`。

**模板：**

```python
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools import BaseTool, FunctionTool
from google.adk.agents.readonly_context import ReadonlyContext
from typing import List, Optional
from typing_extensions import override

class MyToolset(BaseToolset):
    """我的工具集，包含多个相关工具。"""

    def __init__(self, config: dict):
        super().__init__()
        self.config = config

        self._tools = {
            "tool_a": FunctionTool(self._tool_a),
            "tool_b": FunctionTool(self._tool_b),
        }

    @override
    async def get_tools(
        self, readonly_context: Optional[ReadonlyContext] = None
    ) -> List[BaseTool]:
        """根据上下文返回可用工具列表。"""
        return list(self._tools.values())

    async def _tool_a(self, param: str) -> dict:
        """Tool A 功能描述。"""
        return {"result": f"Tool A: {param}"}

    async def _tool_b(self, param: int) -> dict:
        """Tool B 功能描述。"""
        return {"result": f"Tool B: {param}"}
```

代码参考：[veadk/tools/skills_tools/skills_toolset.py:43-100](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/skills_tools/skills_toolset.py#L43-L100)

### 注册到 Agent 的方式

将自定义工具添加到 Agent 的 `tools` 参数中：

```python
from veadk import Agent, Runner

# 函数工具
def my_simple_tool(input_text: str) -> dict:
    """我的简单工具，处理输入文本。"""
    return {"result": f"Processed: {input_text}"}

# 类工具实例
from veadk.tools.builtin_tools.web_search import web_search

agent = Agent(
    name="custom_tool_agent",
    instruction="You are a helpful assistant with custom tools.",
    tools=[
        my_simple_tool,  # 函数直接传入
        web_search,      # 内置函数工具
        # MyCustomTool(),  # 类工具实例
        # MyToolset(config={}),  # 工具集实例
    ],
)
```

## MCP 协议工具接入

VeADK 支持 MCP（Model Context Protocol）协议，通过 `TrustedMcpToolset` 可以连接到 MCP 服务器，将服务器提供的工具自动集成到 Agent 中。

### TrustedMcpToolset 使用方式

代码参考：[veadk/tools/mcp_tool/trusted_mcp_toolset.py:33-125](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/mcp_tool/trusted_mcp_toolset.py#L33-L125)

**支持的连接方式：**

1. **Stdio 连接**（本地进程）：
```python
from mcp import StdioServerParameters
from veadk.tools.mcp_tool import TrustedMcpToolset

toolset = TrustedMcpToolset(
    connection_params=StdioServerParameters(
        command='npx',
        args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"],
    ),
)
```

2. **SSE 连接**（远程服务器）：
```python
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from veadk.tools.mcp_tool import TrustedMcpToolset

toolset = TrustedMcpToolset(
    connection_params=SseConnectionParams(
        url="https://mcp-server.example.com/sse",
    ),
)
```

3. **Streamable HTTP 连接**：
```python
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from veadk.tools.mcp_tool import TrustedMcpToolset

toolset = TrustedMcpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mcp-server.example.com/mcp",
    ),
)
```

**注册到 Agent：**
```python
agent = Agent(
    name="mcp_agent",
    instruction="You can use tools from the connected MCP server.",
    tools=[toolset],
)
```

MCP Toolset 会自动：
- 建立与 MCP 服务器的连接
- 获取服务器提供的所有工具列表
- 将这些工具包装为 ADK 兼容的工具
- 在 Agent 执行完成后自动清理连接

## 使用示例

### 示例 1：基础工具使用

```python
import asyncio
from veadk import Agent, Runner
from veadk.tools import get_city_weather

agent = Agent(
    name="weather_assistant",
    description="An assistant that provides weather information.",
    instruction=(
        "You help users check weather. "
        "Use the get_city_weather tool to look up weather conditions."
    ),
    tools=[get_city_weather],
)

async def main():
    runner = Runner(agent=agent, app_name="weather_app")
    result = await runner.run(
        messages="What's the weather like in Beijing?",
        session_id="session-001",
    )
    print(result)

asyncio.run(main())
```

### 示例 2：使用内置工具（懒加载）

```python
from veadk import Agent
from veadk.tools import get_builtin_tool

web_search = get_builtin_tool("web_search")

agent = Agent(
    name="search_agent",
    instruction="Search the web for the latest information.",
    tools=[web_search],
)
```

代码参考：[veadk/tools/__init__.py:54-67](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/__init__.py#L54-L67)

### 示例 3：自动挂载知识库工具

```python
from veadk import Agent
from veadk.knowledgebase import KnowledgeBase

kb = KnowledgeBase(
    index="my_docs",
    enable_profile=True,
)

agent = Agent(
    name="kb_agent",
    instruction="Answer questions based on the knowledge base.",
    knowledgebase=kb,
    # LoadKnowledgebaseTool 和 load_kb_queries 会自动挂载
)
```

### 示例 4：MCP 文件系统工具

```python
from veadk import Agent
from mcp import StdioServerParameters
from veadk.tools.mcp_tool import TrustedMcpToolset

fs_toolset = TrustedMcpToolset(
    connection_params=StdioServerParameters(
        command='npx',
        args=["-y", "@modelcontextprotocol/server-filesystem", "/home/user/docs"],
    ),
)

agent = Agent(
    name="file_agent",
    instruction="Help the user browse and read files.",
    tools=[fs_toolset],
)
```
