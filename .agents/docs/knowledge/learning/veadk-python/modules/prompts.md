---
id: prompts-module
title: Prompt管理与优化
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# Prompt管理与优化

## 概述

VeADK 提供了 Prompt 管理、优化和评估相关工具，包括抽象的 PromptManager 接口、CozeLoop 云端 Prompt 管理集成、默认系统 Prompt 模板、Prompt 自动优化器、以及记忆处理 Prompt 模板。系统通过 Jinja2 模板引擎实现 Prompt 的动态渲染，支持基于 Agent 元信息和工具列表的智能优化。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/prompts/](file:///d:/AI/.chaos/libs/veadk-python/veadk/prompts/)

---

## PromptManager 体系

### BasePromptManager 抽象基类

`BasePromptManager` 定义了 Prompt 管理器的统一接口，所有 Prompt 管理实现必须继承此类。

> 源码位置：[prompts/prompt_manager.py#L26-L30](file:///d:/AI/.chaos/libs/veadk-python/veadk/prompts/prompt_manager.py#L26-L30)

```python
class BasePromptManager(ABC):
    def __init__(self) -> None: ...

    @abstractmethod
    def get_prompt(self, context: ReadonlyContext, **kwargs) -> str: ...
```

| 方法 | 说明 |
|------|------|
| `get_prompt(context, **kwargs)` | 根据上下文获取 Prompt 字符串，返回系统指令内容 |

**参数说明：**
- `context: ReadonlyContext`：Google ADK 的只读上下文对象，包含 Agent 名称、会话信息、用户信息等
- `**kwargs`：额外参数，用于自定义 PromptManager 扩展

### CozeloopPromptManager - CozeLoop 云端 Prompt 管理

`CozeloopPromptManager` 是 VeADK 内置的 PromptManager 实现，通过 CozeLoop 平台进行 Prompt 的版本化管理和云端拉取。

> 源码位置：[prompts/prompt_manager.py#L33-L79](file:///d:/AI/.chaos/libs/veadk-python/veadk/prompts/prompt_manager.py#L33-L79)

```python
class CozeloopPromptManager(BasePromptManager):
    def __init__(
        self,
        cozeloop_workspace_id: str,
        cozeloop_token: str,
        prompt_key: str,
        version: str = "",
        label: str = "",
    ) -> None:
        self.client = cozeloop.new_client(
            workspace_id=cozeloop_workspace_id,
            api_token=cozeloop_token,
        )

    @override
    def get_prompt(self, context: ReadonlyContext, **kwargs) -> str:
        prompt = self.client.get_prompt(
            prompt_key=self.prompt_key,
            version=self.version,
            label=self.label,
        )
        if (
            prompt
            and prompt.prompt_template
            and prompt.prompt_template.messages
            and prompt.prompt_template.messages[0].content
        ):
            return prompt.prompt_template.messages[0].content
        return DEFAULT_INSTRUCTION  # 获取失败回退到默认指令
```

**初始化参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `cozeloop_workspace_id` | str | ✅ | CozeLoop 工作空间 ID |
| `cozeloop_token` | str | ✅ | CozeLoop API Token |
| `prompt_key` | str | ✅ | Prompt 模板的唯一标识 Key |
| `version` | str | ❌ | Prompt 版本号（为空时使用最新版本） |
| `label` | str | ❌ | Prompt 标签（如 "production"、"staging"） |

**获取逻辑：**
1. 调用 CozeLoop SDK 的 `client.get_prompt()` 获取 Prompt
2. 支持按 `version` 指定版本，或按 `label`（如 production）获取对应版本
3. 验证返回的 Prompt 结构完整性
4. 获取失败时**回退到默认指令**（DEFAULT_INSTRUCTION），避免服务不可用导致 Agent 崩溃

**使用示例：**
```python
from veadk import Agent
from veadk.prompts.prompt_manager import CozeloopPromptManager

prompt_manager = CozeloopPromptManager(
    cozeloop_workspace_id="your-workspace-id",
    cozeloop_token="your-cozeloop-token",
    prompt_key="my-agent-system-prompt",
    version="1.2.0",           # 指定版本
    # label="production",     # 或使用标签
)

agent = Agent(
    name="managed-agent",
    model_name="doubao-seed-2-1-pro-260628",
    instruction=prompt_manager.get_prompt,  # 传入 get_prompt 方法
)
```

**容错设计：**
- 网络异常或 Prompt 不存在时，自动回退到内置默认指令
- 日志记录 Warning，便于排查问题
- 不影响 Agent 主流程运行

---

## 内置默认 Prompt 模板

### DEFAULT_INSTRUCTION - Agent 默认系统指令

当未配置自定义 instruction 或 CozeLoop Prompt 获取失败时，VeADK 使用内置默认指令。

> 源码位置：[prompts/agent_default_prompt.py#L15-L28](file:///d:/AI/.chaos/libs/veadk-python/veadk/prompts/agent_default_prompt.py#L15-L28)

```python
DEFAULT_INSTRUCTION = """You an AI agent created by the VeADK team.

You excel at the following tasks:
1. Data science
- Information gathering and fact-checking
- Data processing and analysis
2. Documentation
- Writing multi-chapter articles and in-depth research reports
3. Coding & Programming
- Creating websites, applications, and tools
- Solve problems and bugs in code (e.g., Python, JavaScript, SQL, ...)
- If necessary, using programming to solve various problems beyond development
4. If user gives you tools, finish various tasks that can be accomplished using tools and available resources
"""
```

**默认能力定位：**
- 数据科学：信息收集、事实核查、数据处理分析
- 文档写作：多章节文章、深度研究报告
- 编程开发：网站/应用/工具创建、代码调试
- 工具使用：利用给定工具和资源完成任务

### DEFAULT_DESCRIPTION - Agent 默认描述

```python
DEFAULT_DESCRIPTION = """An AI agent developed by the VeADK team, specialized in data science, documentation, and software development."""
```

> 源码位置：[prompts/agent_default_prompt.py#L30](file:///d:/AI/.chaos/libs/veadk-python/veadk/prompts/agent_default_prompt.py#L30)

---

## Prompt 优化器

VeADK 提供了基于 LLM 的 Prompt 自动优化功能，通过分析 Agent 的元信息和工具列表来优化系统 Prompt，使其更加精准高效。

> 源码位置：[prompts/prompt_optimization.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/prompts/prompt_optimization.py)

### 核心优化模板

优化器使用 Jinja2 模板构建优化请求，将原始 Prompt、Agent 信息和工具列表注入到元 Prompt 中：

```python
prompt = """
Please help me to optimize the following agent prompt:
{{ original_prompt }}

The following information is your references：
<agent_info>
name: {{ agent.name }}
model: {{ agent.model }}
description: {{ agent.description }}
</agent_info>

<agent_tools_info>
{% for tool in tools %}
<tool>
name: {{ tool.name }}
type: {{ tool.type }}
description: {{ tool.description }}
arguments: {{ tool.arguments }}
</tool>
{% endfor %}
</agent_tools_info>

Please note that in your optimized prompt:
- the above referenced information is not necessary. For example, the tools list of agent is not necessary in the optimized prompt, because it maybe too long. You should use the tool information to optimize the original prompt rather than simply add tool list in prompt.
- The max length of optimized prompt should be less 4096 tokens.
""".strip()
```

> 源码位置：[prompt_optimization.py#L59-L85](file:///d:/AI/.chaos/libs/veadk-python/veadk/prompts/prompt_optimization.py#L59-L85)

**优化原则：**
1. **工具信息用于理解上下文**：不是简单地将工具列表添加到 Prompt 中，而是根据工具能力优化 Prompt 的表述
2. **长度控制**：优化后的 Prompt 不超过 4096 tokens
3. **信息精炼**：去除冗余信息，保留核心指令

### 带反馈的迭代优化模板

支持基于评估反馈进行迭代优化：

```python
prompt_with_feedback = """
After you optimization, my current prompt is:
{{ prompt }}

I did some evaluations with the optimized prompt, and the feedback is: {{ feedback }}

Please continue to optimize the prompt based on the feedback.
""".strip()
```

> 源码位置：[prompt_optimization.py#L87-L94](file:///d:/AI/.chaos/libs/veadk-python/veadk/prompts/prompt_optimization.py#L87-L94)

### 渲染函数

#### render_prompt_with_jinja2() - 首次优化

```python
def render_prompt_with_jinja2(agent: Agent):
    template = Template(prompt)

    tools = []
    for tool in agent.tools:
        _tool_type = ""
        _tools = []
        if isinstance(tool, Callable):
            _tool_type = "function"
            _tools = [FunctionTool(tool)]
        elif isinstance(tool, MCPToolset):
            _tool_type = "tool"
            _tools = asyncio.run(tool.get_tools())

        for _tool in _tools:
            if _tool and _tool._get_declaration():
                tools.append({
                    "name": _tool.name,
                    "description": _tool.description,
                    "arguments": str(_tool._get_declaration().model_dump()["parameters"]),
                    "type": _tool_type,
                })

    context = {
        "original_prompt": agent.instruction,
        "agent": {
            "name": agent.name,
            "model": agent.model_name,
            "description": agent.description,
        },
        "tools": tools,
    }
    return template.render(context)
```

> 源码位置：[prompt_optimization.py#L110-L150](file:///d:/AI/.chaos/libs/veadk-python/veadk/prompts/prompt_optimization.py#L110-L150)

**支持的工具类型：**
| 工具类型 | 说明 | 处理方式 |
|---------|------|---------|
| `Callable` (函数) | `@tool` 装饰的 Python 函数 | 包装为 FunctionTool 提取声明 |
| `MCPToolset` | MCP 工具集 | 异步获取工具列表 |

**提取的工具信息：**
- `name`：工具名称
- `type`：工具类型（function/tool）
- `description`：工具描述
- `arguments`：工具参数 schema（JSON 字符串）

#### render_prompt_feedback_with_jinja2() - 反馈迭代优化

```python
def render_prompt_feedback_with_jinja2(agent: Agent, feedback: str):
    template = Template(prompt_with_feedback)
    context = {
        "prompt": agent.instruction,
        "feedback": feedback,
    }
    return template.render(context)
```

> 源码位置：[prompt_optimization.py#L97-L107](file:///d:/AI/.chaos/libs/veadk-python/veadk/prompts/prompt_optimization.py#L97-L107)

**优化工作流示例：**
```
1. 初始 Prompt → render_prompt_with_jinja2(agent) → LLM 优化 → Optimized Prompt V1
2. 评估 V1 → 得到反馈 feedback
3. render_prompt_feedback_with_jinja2(agent, feedback) → LLM 优化 → Optimized Prompt V2
4. 重复步骤 2-3 直到满意
```

---

## Prompt 评估

### 评估原则 Prompt

VeADK 内置了用于评估 LLM 响应质量的评估 Prompt，主要用于 Prompt 效果评估和回归测试。

> 源码位置：[prompts/prompt_evaluator.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/prompts/prompt_evaluator.py)

**eval_principle_prompt - 评估原则：**
```python
eval_principle_prompt = """
1. You are a LLM for evaluating other models' responses. Note:
- The response maybe generated by some uncertainty tools (e.g., online-search, random number), you just need to consider whether the response is human-readable, rather than focus on the specific content. Because the specific content maybe different at different time.
"""
```

**评估原则说明：**
- 评估者角色：作为评估其他模型响应的 LLM
- 不确定性容忍：考虑到工具调用（如联网搜索、随机数）会导致结果不确定性，应重点评估**可读性**而非具体内容
- 时间因素：相同输入在不同时间可能产生不同结果（如实时数据）

**criteria_prompt - 评估标准：**
```python
criteria_prompt = "Determine whether the actual output is factually correct based on the expected output."
```

**评估标准：**
- 基于期望输出判断实际输出是否事实正确
- 用于自动化评估和回归测试

---

## 记忆处理 Prompt 模板

`prompt_memory_processor.py` 提供了用于从对话历史中提取重要信息并构建长期记忆的 Prompt 模板。

> 源码位置：[prompts/prompt_memory_processor.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/prompts/prompt_memory_processor.py)

### MEMORY_PROCESSOR_SYSTEM_PROMPT

```python
MEMORY_PROCESSOR_SYSTEM_PROMPT = """I will give you a series of messages of memory, including messages from user and assistant.

You should help me to recognize important information from the messages, and build some new messages.

For example, for the following messages:
[
    {
        "role": "user",
        "content": "Hello, tell me the weather of Beijing, and remember my secret is `abc001`"
    },
    {
        "role": "assistant",
        "content": "The weather of Beijing is sunny, and the temperature is 25 degree Celsius. I have remember that your secret is `abc001`."
    }
]

You should extract the important information from the messages, and build new messages if needed (in JSON format):
[
    {
        "role": "user",
        "content": "My secret is `abc001`."
    }
]

The actual messages are:
{{ messages }}
"""
```

> 源码位置：[prompt_memory_processor.py#L17-L43](file:///d:/AI/.chaos/libs/veadk-python/veadk/prompts/prompt_memory_processor.py#L17-L43)

**核心功能：**
1. **信息提取**：从用户和助手的对话中识别重要信息
2. **记忆构建**：将重要信息重新组织为结构化的记忆消息
3. **示例引导**：通过 Few-shot 示例展示期望的提取行为
4. **JSON 输出**：要求以 JSON 数组格式返回提取结果

**设计思路：**
- 区分**时效性信息**（如"北京天气"）和**持久性信息**（如"我的密码是 abc001"）
- 只提取需要长期记住的用户偏好、个人信息、重要事实
- 输出格式简洁，便于存入长期记忆

### render_prompt() - 渲染记忆处理 Prompt

```python
def render_prompt(messages: list[dict]):
    template = Template(MEMORY_PROCESSOR_SYSTEM_PROMPT)
    context = {"messages": messages}
    return template.render(context)
```

> 源码位置：[prompt_memory_processor.py#L46-L55](file:///d:/AI/.chaos/libs/veadk-python/veadk/prompts/prompt_memory_processor.py#L46-L55)

**输入格式：**
```python
messages = [
    {"role": "user", "content": "用户消息"},
    {"role": "assistant", "content": "助手回复"},
    # ...
]
```

---

## 自定义 PromptManager 开发

继承 `BasePromptManager` 可实现自定义 Prompt 管理逻辑（如从文件、数据库、配置中心加载 Prompt）。

```python
from veadk.prompts.prompt_manager import BasePromptManager
from google.adk.agents.readonly_context import ReadonlyContext

class FilePromptManager(BasePromptManager):
    """从本地文件加载 Prompt 的自定义管理器"""

    def __init__(self, prompt_dir: str = "./prompts"):
        self.prompt_dir = prompt_dir
        super().__init__()

    def get_prompt(self, context: ReadonlyContext, **kwargs) -> str:
        agent_name = context.agent_name
        prompt_file = os.path.join(self.prompt_dir, f"{agent_name}.txt")

        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Prompt file not found for {agent_name}, using default")
            from veadk.prompts.agent_default_prompt import DEFAULT_INSTRUCTION
            return DEFAULT_INSTRUCTION


class DynamicPromptManager(BasePromptManager):
    """支持按场景动态选择 Prompt 的管理器"""

    def __init__(self, prompts: dict[str, str]):
        self.prompts = prompts
        super().__init__()

    def get_prompt(self, context: ReadonlyContext, **kwargs) -> str:
        # 从 kwargs 获取场景
        scenario = kwargs.get("scenario", "default")
        # 根据用户ID或其他上下文信息选择 Prompt
        user_id = context.user_id if hasattr(context, 'user_id') else None

        if scenario in self.prompts:
            return self.prompts[scenario]
        return self.prompts.get("default", DEFAULT_INSTRUCTION)
```

---

## Prompt 版本管理说明

### 当前版本管理状态

VeADK 当前（v1.x）的 Prompt 版本管理策略：

| 功能 | 状态 | 实现方式 |
|------|------|---------|
| 本地文件 Prompt | ❌ 无内置 | 可自定义 PromptManager 实现 |
| CozeLoop 版本管理 | ✅ 支持 | `version` + `label` 参数 |
| 环境变量切换 | ❌ 无内置 | 可通过自定义实现 |
| A/B 测试 | ❌ 无内置 | 可自定义 PromptManager 实现 |
| Prompt 热更新 | ⚠️ 间接支持 | CozeLoop 拉取最新 label 版本 |

### CozeLoop 版本管理最佳实践

1. **使用 Label 管理环境**：
   - `production`：生产环境稳定版本
   - `staging`：预发布测试版本
   - `canary`：金丝雀发布版本

2. **版本号规范**：使用语义化版本（如 `1.0.0`、`1.1.0`）

3. **回滚机制**：指定具体 version 而非 label 可以锁定版本，避免意外更新

```python
# 生产环境：锁定具体版本
prod_pm = CozeloopPromptManager(
    workspace_id="ws-prod",
    token="prod-token",
    prompt_key="customer-service",
    version="2.1.0",  # 锁定版本
)

# 预发布环境：使用 staging label
staging_pm = CozeloopPromptManager(
    workspace_id="ws-prod",
    token="staging-token",
    prompt_key="customer-service",
    label="staging",  # 自动获取最新 staging 版本
)
```

---

## Prompt 编写最佳实践

### 系统 Prompt 编写建议

1. **角色定义清晰**：明确 Agent 的身份、能力边界、行为风格
2. **指令具体可执行**：避免模糊描述，给出明确的行为指引
3. **工具使用说明**：说明何时使用何种工具（工具描述本身也要清晰）
4. **输出格式规范**：指定期望的输出格式（JSON/Markdown/特定结构）
5. **长度控制**：建议控制在 2000 tokens 以内，不超过 4096 tokens
6. **避免冗余**：不要重复工具列表，通过工具描述让模型理解工具能力
7. **使用分隔符**：用 XML 标签或 Markdown 分隔不同的指令区块

### 优化提示

1. **利用优化器**：先写初稿，使用 Prompt 优化器根据 Agent 配置进行优化
2. **迭代优化**：通过评估反馈不断迭代，使用 `render_prompt_feedback_with_jinja2()`
3. **测试验证**：优化后使用评估 Prompt 进行自动化测试
4. **版本锁定**：生产环境锁定版本，避免意外变更

---

## 使用示例

### 基础：使用默认 Prompt

```python
from veadk import Agent, tool

@tool
def search(query: str) -> str:
    """搜索互联网"""
    return f"结果 for: {query}"

# 不指定 instruction，使用 DEFAULT_INSTRUCTION
agent = Agent(
    name="default-agent",
    model_name="doubao-seed-2-1-pro-260628",
    tools=[search],
)
```

### 自定义系统 Prompt

```python
agent = Agent(
    name="customer-service",
    model_name="doubao-seed-2-1-pro-260628",
    description="客服助手",
    instruction="""你是一个专业的客服助手。
你的职责：
1. 耐心解答用户问题
2. 遇到无法解决的问题，引导用户转人工
3. 语气友好、专业
""",
)
```

### 使用 CozeLoop 管理 Prompt

```python
from veadk.prompts.prompt_manager import CozeloopPromptManager

# 初始化 CozeLoop Prompt 管理器
pm = CozeloopPromptManager(
    cozeloop_workspace_id="your-workspace-id",
    cozeloop_token="cozeloop-api-token",
    prompt_key="customer-service-prompt",
    label="production",  # 生产环境标签
)

agent = Agent(
    name="customer-service",
    model_name="doubao-seed-2-1-pro-260628",
    instruction=pm.get_prompt,  # 传入方法引用，运行时动态获取
)
```

### 使用 Prompt 优化器

```python
from veadk import Agent
from veadk.prompts.prompt_optimization import render_prompt_with_jinja2

# 创建 Agent（使用初始 Prompt）
agent = Agent(
    name="my-agent",
    model_name="doubao-seed-2-1-pro-260628",
    description="一个助手",
    instruction="你是一个有用的助手",
    tools=[...]
)

# 生成优化请求（发送给 LLM 进行优化）
optimization_request = render_prompt_with_jinja2(agent)

# 将 optimization_request 发送给模型，获取优化后的 Prompt
# optimized_prompt = llm.generate(optimization_request)

# 迭代优化：根据反馈继续优化
# feedback = "工具调用不够积极"
# next_request = render_prompt_feedback_with_jinja2(agent, feedback)
```

### 使用记忆处理 Prompt

```python
from veadk.prompts.prompt_memory_processor import render_prompt

# 对话消息
messages = [
    {"role": "user", "content": "我叫小明，我喜欢Python编程"},
    {"role": "assistant", "content": "好的小明，我记住你喜欢Python了"},
]

# 渲染记忆提取 Prompt
memory_prompt = render_prompt(messages)

# 发送给 LLM，提取重要信息
# extracted_memories = llm.generate(memory_prompt)
# 返回: [{"role": "user", "content": "我叫小明，喜欢Python编程"}]
```

---

## 目录结构

```
veadk/prompts/
├── __init__.py
├── agent_default_prompt.py           # 默认系统指令和描述
├── prompt_manager.py                 # BasePromptManager + CozeloopPromptManager
├── prompt_optimization.py            # Prompt 优化模板与渲染函数
├── prompt_evaluator.py               # Prompt 评估原则
└── prompt_memory_processor.py        # 记忆提取处理 Prompt 模板
```
