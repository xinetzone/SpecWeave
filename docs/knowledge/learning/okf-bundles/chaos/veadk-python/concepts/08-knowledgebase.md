---
type: Concept
title: 知识库
description: KnowledgeBase 统一接口、8 种可插拔后端、CRUD 方法、Profile 自动生成与 Agent 工具自动挂载
tags: [veadk, knowledgebase, rag, vector-database, profile, backend]
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

# 知识库

`KnowledgeBase` 是 veadk-python 的检索增强生成（RAG）核心组件，定义于 `veadk/knowledgebase/knowledgebase.py` [F-102]。它为 8 种向量/搜索后端提供统一的 CRUD 接口，支持从目录、文件列表或纯文本添加知识，并可通过 LLM 自动生成 Profile（标签和关键词）来优化检索策略。Agent 在 `model_post_init` 中检测到 `knowledgebase` 字段时自动挂载知识库工具。

## KnowledgeBase 类定义

`KnowledgeBase` 继承自 Pydantic `BaseModel` [F-102]。

### 核心字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | `str` | `"user_knowledgebase"` | 知识库名称 |
| `description` | `str` | `"This knowledgebase stores some user-related information."` | 描述 |
| `backend` | `str \| BaseKnowledgebaseBackend` | `"local"` | 后端类型或实例 |
| `backend_config` | `dict` | `{}` | 后端配置参数 |
| `top_k` | `int` | `10` | 默认检索返回条数 |
| `app_name` | `str` | `""` | 应用名 |
| `index` | `str` | `""` | 索引名 |
| `enable_profile` | `bool` | `False` | 启用 Profile 功能 |
| `query_with_user_profile` | `bool` | `False` | 查询时结合用户 Profile |

来源：[F-102]

## 8 种可插拔后端

`_get_backend_cls(backend)` 工厂方法支持以下后端 [F-103]：

| backend 值 | 后端类 | 适用场景 |
|-----------|--------|---------|
| `"local"` | `InMemoryKnowledgeBackend` | 本地开发、测试（内存存储） |
| `"opensearch"` | `OpensearchKnowledgeBackend` | 生产级全文+向量检索 |
| `"redis"` | `RedisKnowledgeBackend` | 低延迟向量检索 |
| `"milvus"` | `MilvusKnowledgeBackend` | 大规模向量数据库 |
| `"tos_vector"` | `TosVectorKnowledgeBackend` | TOS 对象存储+向量 |
| `"viking"` | `VikingDBKnowledgeBackend` | 火山引擎 VikingDB |
| `"context_search"` | `ContextSearchBackend` | 上下文搜索 |
| `"openviking"` | `OpenVikingKnowledgeBackend` | OpenViking |

后端采用懒加载机制：只有实际选用某个后端时才导入其依赖模块。若 llama_index 相关导入失败，提示安装 `veadk-python[extensions]` 可选依赖组 [F-103]。

## 初始化逻辑

1. 传入 backend 实例时直接使用并设置 index [F-104]
2. `backend_config` 非空时用其初始化后端实例
3. 否则 `index` 取 `self.index or self.app_name`，均无则抛出 `ValueError`
4. `query_with_user_profile=True` 时记录提示，建议使用 Viking Memory 后端 [F-104]

## 核心 CRUD 方法

### 添加知识

**从目录添加**：

```python
add_from_directory(directory: str, **kwargs) -> bool
```

递归扫描目录中的文件，解析并添加到知识库 [F-105]。

**从文件列表添加**：

```python
add_from_files(files: list[str], **kwargs) -> bool
```

批量添加指定文件 [F-105]。

**从文本添加**：

```python
add_from_text(text: str | list[str], **kwargs) -> bool
```

直接添加纯文本内容，支持单条或批量 [F-105]。

### 搜索

```python
search(query: str, top_k: int = 0, **kwargs) -> list[KnowledgebaseEntry]
```

根据查询文本检索相关条目 [F-105]：
- `top_k=0` 时使用实例的 `self.top_k`（默认 10）
- 返回 `KnowledgebaseEntry` 列表，按相关度排序

### 关闭

```python
close() -> None
```

释放后端资源（如数据库连接）[F-105]。

### 动态代理

`KnowledgeBase` 通过 `__getattr__(name)` 将未定义的属性调用代理到底层后端实例 [F-105]。这意味着后端特有的方法（如 `delete`、`list_chunks` 等）可以直接在 KnowledgeBase 上调用，无需显式包装。例如：

```python
kb = KnowledgeBase(backend="opensearch", ...)
kb.delete(doc_id="123")  # 代理到 OpensearchKnowledgeBackend.delete()
```

这种"透明代理"模式提供了统一接口的便利性，同时保留了后端特有能力。

## KnowledgebaseEntry 数据模型

```python
class KnowledgebaseEntry(BaseModel):
    content: str
    metadata: dict | None = None
```

定义于 `veadk/knowledgebase/entry.py` [F-107]。每个检索结果包含文本内容和可选的元数据（如来源文件、页码、时间戳等）。

## Profile 自动生成

`generate_profiles` 方法使用 LLM 为知识库文件自动生成结构化 Profile [F-106]：

```python
async def generate_profiles(files: list[str], profile_path: str = "")
```

### Profile 结构

```python
class KnowledgebaseProfile(BaseModel):
    name: str
    description: str
    tags: list[str]        # 3-5 个分类标签
    keywords: list[str]    # 3-5 个推荐查询关键词
```

定义于 `veadk/knowledgebase/types.py` [F-108]。

### 生成流程

1. 默认使用 `deepseek-v3-2-251201` 模型 [F-106]
2. 为每个文件生成 JSON 格式 Profile，包含名称、描述、标签和关键词
3. 写入 `./profiles/knowledgebase/profiles_<index>/` 目录

### Profile 的用途

- **检索优化**：Profile 中的关键词可作为查询扩展，提升召回率
- **知识库概览**：tags 提供知识库内容的分类视图
- **Agent 工具增强**：`enable_profile=True` 时，Agent 额外挂载 `load_kb_queries` 工具，可以查询 Profile 来理解知识库结构并制定检索策略

## 与 Agent 的集成

Agent 在 `model_post_init` 中自动挂载知识库工具 [F-027]：

1. `knowledgebase` 字段存在时，自动追加 `LoadKnowledgebaseTool` 到 tools
2. `knowledgebase.enable_profile=True` 时，额外追加 `load_kb_queries` 工具

`LoadKnowledgebaseTool` 允许 Agent 在对话中主动查询知识库，`load_kb_queries` 允许 Agent 查看知识库的 Profile 信息。

## 知识库 vs 长期记忆

知识库和长期记忆（`LongTermMemory`）都支持多种后端且功能有重叠，但定位不同：

| 维度 | KnowledgeBase | LongTermMemory |
|------|--------------|----------------|
| 数据来源 | 外部文档、目录、文本 | Agent 会话事件 |
| 写入时机 | 构建时批量添加 | 会话结束后自动保存 |
| 查询方式 | Agent 主动调用工具 | ADK MemoryService 自动注入 |
| 数据性质 | 静态知识（文档、手册） | 动态记忆（用户偏好、历史对话） |
| 默认后端 | `"local"` | `"opensearch"` |
| Profile 支持 | 有（LLM 生成标签/关键词） | 有（会话事件分组） |

## 使用示例

```python
from veadk import Agent
from veadk.knowledgebase import KnowledgeBase

kb = KnowledgeBase(
    backend="local",
    top_k=5,
    enable_profile=True,
)

kb.add_from_text("火山引擎是字节跳动旗下的云服务平台。")
kb.add_from_directory("./docs/")

agent = Agent(
    name="doc_assistant",
    instruction="基于知识库回答问题。",
    knowledgebase=kb,
)
```

## 相关概念

- [Agent 核心类与生命周期](/concepts/01-agent-lifecycle.md)
- [记忆系统](/concepts/06-memory-system.md)
- [LLM 模型抽象](/concepts/07-llm-models.md)
- [评估系统](/concepts/09-evaluation.md)
- [配置系统](/concepts/04-configuration.md)
