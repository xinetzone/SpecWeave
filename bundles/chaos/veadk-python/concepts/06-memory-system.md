---
type: Concept
title: 记忆系统
description: 短期记忆与长期记忆的四层体系、后端可插拔架构、会话压缩与 Profile 生成机制
tags: [veadk, memory, short-term, long-term, session, profile]
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

# 记忆系统

veadk-python 的记忆系统分为短期记忆（`ShortTermMemory`）和长期记忆（`LongTermMemory`）两个核心类，并在此基础上提供会话压缩（compaction）和 Profile 生成两种增强能力。两类记忆均采用后端可插拔设计，通过 `backend` 字段选择存储实现，后端类采用懒加载以减少不必要的依赖导入。

## ShortTermMemory 短期记忆

`ShortTermMemory` 定义于 `veadk/memory/short_term_memory.py`，继承自 Pydantic `BaseModel` [F-082]。它管理 Agent 的会话状态，对应 ADK 的 `BaseSessionService`。

### 核心字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `backend` | `Literal["local","mysql","sqlite","postgresql","database"]` | `"local"` | 后端类型 [F-082] |
| `backend_configs` | `dict` | `{}` | 后端配置参数 |
| `db_kwargs` | `dict` | `{}` | 数据库连接参数 |
| `db_url` | `str` | `""` | 数据库 URL，设置后覆盖 backend |
| `local_database_path` | `str` | `"/tmp/veadk_local_database.db"` | 本地数据库路径 |
| `after_load_memory_callback` | `Callable \| None` | `None` | 记忆加载后回调 |

`_session_service: BaseSessionService` 是私有属性，在初始化时创建。

### 后端初始化

后端选择逻辑 [F-083]：

- `db_url` 设置时：使用 `DatabaseSessionService`（通过 SQLAlchemy 连接任意数据库）
- `backend="local"`：使用 `InMemorySessionService`（内存存储，进程结束后丢失）
- `backend="mysql"`：使用 `MysqlSTMBackend`
- `backend="sqlite"`：使用 `SQLiteSTMBackend`
- `backend="postgresql"`：使用 `PostgreSqlSTMBackend`
- `backend="database"`：已弃用，映射到 `sqlite`

URL 中包含多个 `@` 或 `:` 时会发出警告，提示需要 URL 编码（如密码中的特殊字符）。

### 核心方法

**session_service 属性**：返回内部的 `_session_service` 实例，供 Runner 使用 [F-084]。

**create_session**：

```python
async create_session(app_name, user_id, session_id) -> Session | None
```

若会话已存在则返回现有会话，否则创建新会话 [F-084]。

**generate_profile**：

```python
async generate_profile(app_name, user_id, session_id, events) -> list[str]
```

使用 LLM 将事件列表分组为 Profile（用户画像），写入 `./profiles/memory/<app>/<user>/<session>/` 目录 [F-084]。Profile 是对会话事件的语义分组，帮助理解用户偏好和行为模式。

**compact_history_events**：

```python
async compact_history_events(app_name, user_id, session_id, compact_limit, agent)
```

当历史事件数超过 `compact_limit` 时，使用 LLM 压缩早期事件为摘要，并追加 `load_history_events` 工具供 Agent 按需加载完整历史 [F-084]。这是防止上下文窗口溢出的关键机制。

## LongTermMemory 长期记忆

`LongTermMemory` 定义于 `veadk/memory/long_term_memory.py`，同时继承 `BaseMemoryService`（Google ADK）和 `BaseModel`（Pydantic）[F-086]。它管理跨会话的持久化记忆，对应 ADK 的 `BaseMemoryService`。

### 核心字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `backend` | `str \| BaseLongTermMemoryBackend` | `"opensearch"` | 后端类型或实例 [F-086] |
| `backend_config` | `dict` | `{}` | 后端配置 |
| `top_k` | `int` | `5` | 检索返回条数 |
| `index` | `str` | `""` | 索引名 |
| `app_name` | `str` | `""` | 应用名 |
| `user_id` | `str` | `""` | 用户 ID（已弃用，保留兼容） |

### 支持的后端

`_get_backend_cls(backend)` 工厂方法支持 8 种后端 [F-087]：

| backend 值 | 后端类 | 说明 |
|-----------|--------|------|
| `"local"` | `InMemoryLTMBackend` | 内存存储 |
| `"opensearch"` | `OpensearchLTMBackend` | OpenSearch（默认） |
| `"redis"` | `RedisLTMBackend` | Redis 向量检索 |
| `"viking"` | `VikingDBLTMBackend` | 火山引擎 VikingDB |
| `"viking_mem"` | （映射到 `"viking"`） | 已弃用 |
| `"mem0"` | `Mem0LTMBackend` | Mem0 记忆引擎 |
| `"openviking"` | `OpenVikingLTMBackend` | OpenViking |
| `"tos_context"` | `TosContextBucketLTMBackend` | TOS 上下文桶 |

后端采用懒加载：只有实际选用某个后端时才导入其依赖模块。若 llama_index 相关导入失败，提示安装 `veadk-python[extensions]` [F-087]。

### 初始化逻辑

1. 传入 backend 实例时直接使用
2. `backend_config` 非空时用其初始化（自动补充 `index` 字段）
3. 否则使用 `index` 或 `app_name`，均无则使用 `"default_app"`
4. `"viking_mem"` 自动映射为 `"viking"` [F-088]

### 核心方法

**add_session_to_memory**：

```python
async add_session_to_memory(session: Session, **kwargs)
```

过滤并转换事件为 JSON 字符串后存储。`openviking` 后端包含 assistant 事件，其他后端仅存储 user 事件 [F-089]。

**search_memory**：

```python
async search_memory(*, app_name, user_id, query) -> SearchMemoryResponse
```

根据查询文本检索相关记忆，返回 `top_k` 条结果 [F-089]。

**_filter_and_convert_events**：

过滤无效事件和函数调用，将事件序列化为 JSON 字符串。`include_assistant=False` 时仅保留用户消息 [F-089]。

## MemoryProfile 数据模型

```python
class MemoryProfile(BaseModel):
    name: str
    event_ids: list[str]
```

定义于 `veadk/memory/types.py` [F-085]。每个 Profile 有一个名称和关联的事件 ID 列表。

## 四层记忆体系

veadk 的记忆能力可划分为四个层次：

### 第一层：短期会话记忆

`ShortTermMemory` 维护当前会话的完整事件历史，包括用户消息、Agent 响应、工具调用等。Runner 在每次 `run()` 时自动加载和更新会话状态。

### 第二层：长期跨会话记忆

`LongTermMemory` 在会话结束后（通过 `auto_save_session=True` 自动触发，或手动调用 `save_session_to_long_term_memory`）将重要事件持久化。Agent 执行时通过 `load_memory` 工具检索相关历史记忆 [F-028]。

### 第三层：会话压缩

当对话历史过长时，`compact_history_events` 使用 LLM 将早期对话压缩为摘要，释放上下文窗口。压缩后的摘要作为 system 消息注入，Agent 仍可通过 `load_history_events` 工具访问原始事件。

### 第四层：Profile 生成

`generate_profile` 使用 LLM 分析会话事件，提取用户画像信息（如偏好、习惯、事实），持久化到文件系统。Profile 不同于原始记忆——它是对记忆的结构化提炼。

## 与 Agent 的集成

记忆系统在 Agent 的 `model_post_init` 中自动挂载：

- `short_term_memory` 字段存在时，Runner 使用其 `session_service` [F-068]
- `long_term_memory` 字段存在时，自动追加 ADK 的 `load_memory` 工具，并设置 `custom_metadata["backend"]` 标识后端 [F-028]
- `auto_save_session=True` 且 LTM 存在时，注册 `save_session_to_long_term_memory` 到 `after_agent_callback` [F-031]

## 后端选择建议

| 场景 | 短期记忆后端 | 长期记忆后端 |
|------|-------------|-------------|
| 本地开发 | `local`（内存） | `local`（内存） |
| 单机生产 | `sqlite` | `opensearch` 或 `redis` |
| 分布式生产 | `mysql` 或 `postgresql` | `opensearch` 或 `viking` |
| 火山引擎生态 | `mysql` | `viking` 或 `openviking` |
| 轻量缓存 | `sqlite` | `redis` |

## 相关概念

- [Agent 核心类与生命周期](/concepts/01-agent-lifecycle.md)
- [Runner 运行器](/concepts/05-runner.md)
- [知识库](/concepts/08-knowledgebase.md)
- [配置系统](/concepts/04-configuration.md)
