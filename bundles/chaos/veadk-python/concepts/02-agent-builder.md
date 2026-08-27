---
type: Concept
title: AgentBuilder 与 YAML 配置驱动
description: AgentBuilder 如何通过 OmegaConf 加载 YAML 配置、递归构建子代理、动态导入工具并映射 5 种 Agent 类型
tags: [veadk, agent-builder, yaml, configuration, omega-conf]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: veadk-source
    resource: "/references/veadk-source.md"
    title: veadk-python 源码
  - id: facts
    resource: "/references/facts.md"
    title: veadk-python 事实清单
---

# AgentBuilder 与 YAML 配置驱动

`AgentBuilder` 是 veadk-python 提供的声明式 Agent 构建器，定义于 `veadk/agent_builder.py` [F-041]。它允许开发者通过 YAML 文件描述 Agent 的类型、模型、工具、子代理拓扑等结构，而非在 Python 代码中逐步实例化。这是 veadk"配置即挂载"设计理念在构建层面的体现。

## AgentBuilder 类定义

```python
class AgentBuilder:
```

`AgentBuilder` 不继承任何基类，是一个纯构建器类 [F-041]。其核心是三个方法：`_read_config`、`_build` 和 `build`，构成"读取配置→递归构建→返回根 Agent"的流水线。

## AGENT_TYPES 类型映射

AgentBuilder 维护一个类型字符串到 Python 类的映射表 [F-042]：

```python
AGENT_TYPES = {
    "Agent": Agent,
    "SequentialAgent": SequentialAgent,
    "ParallelAgent": ParallelAgent,
    "LoopAgent": LoopAgent,
    "RemoteVeAgent": RemoteVeAgent,
}
```

这 5 种类型覆盖了 veadk 的 Agent 拓扑需求：

| 类型字符串 | 对应类 | 用途 |
|-----------|--------|------|
| `"Agent"` | `Agent` | 基础 LLM Agent，支持工具调用和子代理转移 |
| `"SequentialAgent"` | `SequentialAgent` | 按顺序执行子代理 |
| `"ParallelAgent"` | `ParallelAgent` | 并行执行子代理 |
| `"LoopAgent"` | `LoopAgent` | 循环执行子代理直到满足条件 |
| `"RemoteVeAgent"` | `RemoteVeAgent` | 远程 A2A Agent 代理 |

YAML 配置中的 `type` 字段决定实例化哪个类。若未指定 `type`，默认使用 `"Agent"`。

## 配置读取：_read_config

```python
def _read_config(self, path: str) -> dict
```

该方法负责将 YAML 文件加载为 Python 字典 [F-044]：

1. 断言文件路径以 `.yaml` 结尾
2. 使用 `OmegaConf.load(path)` 加载 YAML（OmegaConf 是 `omegaconf==2.3.0` 库提供的配置解析器，支持插值和类型转换）
3. 通过 `OmegaConf.to_container(resolve=True)` 将 OmegaConf 对象解析为普通 Python 字典（`resolve=True` 会解析所有 `${...}` 插值表达式）

OmegaConf 的支持使得 YAML 配置可以使用变量引用和插值，例如：

```yaml
model_name: &model "doubao-seed-2-1-pro-260628"
root_agent:
  model_name: *model
```

## 递归构建：_build

```python
def _build(self, agent_config: dict) -> BaseAgent
```

这是 AgentBuilder 的核心方法，负责将单个 Agent 配置字典转化为 Agent 实例 [F-043]。其执行流程如下：

### 1. 子代理递归构建

若 `agent_config` 中包含 `sub_agents` 字段，遍历每个子代理配置，递归调用 `self._build(sub_config)` 构建子 Agent 实例，形成 Agent 树 [F-043]。这使得任意深度的嵌套 Agent 拓扑都可以通过 YAML 描述。

### 2. 工具动态导入

工具通过 `importlib.import_module` 动态导入 [F-043]。YAML 中工具以字符串格式 `"module.path.function_name"` 指定，AgentBuilder 按 `.` 分割，导入模块并获取函数对象。例如：

```yaml
tools:
  - "veadk.tools.builtin_tools.web_search.web_search"
  - "my_project.tools.custom_tool"
```

这种设计使得工具不需要在构建时代码中静态导入，可以按配置按需加载。

### 3. 类型选择与实例化

根据 `agent_config.get("type", "Agent")` 从 `AGENT_TYPES` 映射表获取对应的类 [F-043]。将配置字典（已处理子代理和工具）作为关键字参数传入类构造函数，实例化 Agent。

由于 Agent 是 Pydantic 模型（`model_config = ConfigDict(extra="allow")`），YAML 中的额外字段不会导致报错，而是被允许传入 [F-014]。

## 公开入口：build

```python
def build(self, path: str, root_agent_identifier: str = "root_agent") -> BaseAgent
```

`build` 是用户调用的公开方法 [F-045]：

1. 调用 `_read_config(path)` 加载完整 YAML 配置
2. 从配置字典中取 `root_agent_identifier`（默认 `"root_agent"`）指定的配置段
3. 调用 `_build` 构建该配置段对应的 Agent 并返回

这意味着一个 YAML 文件可以包含多个 Agent 定义，`root_agent_identifier` 参数选择哪个作为根 Agent 入口。

## YAML 配置结构示例

基于 AgentBuilder 的设计，一个典型的配置文件结构如下：

```yaml
root_agent:
  type: Agent
  name: "my_assistant"
  description: "A helpful assistant"
  instruction: "You are a helpful assistant."
  model_name: "doubao-seed-2-1-pro-260628"
  model_provider: "openai"
  tools:
    - "veadk.tools.builtin_tools.web_search.web_search"
  sub_agents:
    - type: SequentialAgent
      name: "research_pipeline"
      sub_agents:
        - type: Agent
          name: "searcher"
          instruction: "Search for information."
        - type: Agent
          name: "writer"
          instruction: "Summarize findings."
```

## 与代码式构建的对比

veadk 提供两种构建 Agent 的方式：

**代码式构建**（直接实例化）：

```python
from veadk import Agent

agent = Agent(
    name="my_agent",
    instruction="...",
    tools=[my_tool],
)
```

适用于简单场景、需要编程逻辑动态决定配置的场景。

**声明式构建**（AgentBuilder + YAML）：

```python
from veadk.agent_builder import AgentBuilder

agent = AgentBuilder().build("config.yaml")
```

适用于复杂多 Agent 拓扑、配置与代码分离、需要非开发者修改 Agent 结构的场景。

两种方式最终产出的都是 `BaseAgent` 实例，后续通过 `Runner` 驱动执行的方式完全相同。

## 设计要点

1. **递归性**：`_build` 方法通过自递归处理任意深度的 `sub_agents` 嵌套，Agent 树的深度不受构建器限制
2. **动态性**：工具通过字符串路径动态导入，配置文件不依赖 Python 导入语句
3. **扩展性**：`AGENT_TYPES` 映射表是类级别的常量，理论上可以通过修改或继承来添加自定义 Agent 类型
4. **OmegaConf 插值**：`resolve=True` 确保 YAML 中的 `${...}` 变量引用在传递给 Agent 构造函数前被解析
5. **Pydantic extra=allow**：Agent 的 Pydantic 配置允许 YAML 中的额外字段直接传入，无需在 AgentBuilder 中做字段白名单过滤

## 相关概念

- [Agent 核心类与生命周期](/concepts/01-agent-lifecycle.md)
- [Agent 类型体系](/concepts/03-agent-types.md)
- [配置系统](/concepts/04-configuration.md)
- [veadk-python 概览](/concepts/00-overview.md)
