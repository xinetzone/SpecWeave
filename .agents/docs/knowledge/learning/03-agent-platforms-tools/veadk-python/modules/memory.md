---
id: memory-module
title: 记忆系统详解（ShortTermMemory & LongTermMemory）
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# 记忆系统详解

VeADK 提供了双层记忆架构：**短期记忆（ShortTermMemory）** 和 **长期记忆（LongTermMemory）**，分别用于会话上下文管理和跨会话持久化记忆。

---

## 记忆系统概述

### 短期记忆 vs 长期记忆

| 维度 | ShortTermMemory | LongTermMemory |
|------|----------------|----------------|
| **作用范围** | 单会话内（session 级） | 跨会话、跨用户持久化 |
| **存储内容** | 完整对话历史（system prompt + 用户/助手消息） | 过滤后的关键记忆片段（向量检索） |
| **上下文传递** | 直接发送给模型（占用上下文窗口） | 通过 `load_memory` 工具按需检索注入 |
| **生命周期** | 会话结束后可持久化到数据库 | 长期保存，支持语义检索 |
| **典型场景** | 多轮对话上下文保持 | 记住用户偏好、历史事实、跨会话回忆 |
| **后端类型** | local/mysql/sqlite/postgresql | local/opensearch/redis/viking/mem0/openviking/tos_context |

> 短期记忆对应 Google ADK 的 Session 服务，长期记忆继承自 `BaseMemoryService` 并提供语义检索能力。

---

## ShortTermMemory（短期/会话记忆）

短期记忆管理单次会话的完整对话上下文，所有内容会直接发送给大模型。支持通过 `session_id` 实现会话隔离，相同 `session_id` 可恢复历史对话。

### 接口定义

**类签名**：
```python
class ShortTermMemory(BaseModel):
```

- 基类：`pydantic.BaseModel`
- 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L57-L290](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L57-L290)

### 构造参数

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `backend` | `Literal["local", "mysql", "sqlite", "postgresql", "database"]` | `"local"` | 短期记忆后端类型。`"database"` 已废弃，映射为 `"sqlite"` |
| `backend_configs` | `dict` | `{}` | 后端初始化配置字典 |
| `db_kwargs` | `dict` | `{}` | 数据库连接额外关键字参数 |
| `db_url` | `str` | `""` | 数据库连接 URL（如 `sqlite:///./test.db`）。设置后覆盖 `backend` 参数 |
| `local_database_path` | `str` | `"/tmp/veadk_local_database.db"` | SQLite 本地数据库文件路径，仅 sqlite 后端使用 |
| `after_load_memory_callback` | `Callable \| None` | `None` | 加载记忆后的回调函数，接收 `Session` 作为参数 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L79-L91](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L79-L91)

### 支持的后端

| 后端类型 | 对应实现类 | 依赖 | 存储位置 |
|----------|-----------|------|---------|
| `local` | `InMemorySessionService` | 内置（google-adk） | 进程内存（进程退出后丢失） |
| `sqlite` | `SQLiteSTMBackend` | 内置（sqlalchemy） | 本地 SQLite 文件 |
| `mysql` | `MysqlSTMBackend` | pymysql, aiomysql（内置依赖） | MySQL 数据库 |
| `postgresql` | `PostgreSqlSTMBackend` | psycopg2-binary, asyncpg（内置依赖） | PostgreSQL 数据库 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L111-L125](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L111-L125)

**使用 db_url 的方式**：
```python
ShortTermMemory(
    db_url="postgresql://user:pass@localhost:5432/mydb",
    db_kwargs={"pool_size": 10}
)
```
设置 `db_url` 后，将使用 `DatabaseSessionService` 自动识别数据库类型，忽略 `backend` 参数。若 URL 中密码包含特殊字符（如 `@`、`:`），需使用 `urllib.parse.quote_plus` 进行编码。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L94-L104](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L94-L104)

### 核心方法

#### `session_service` 属性
```python
@property
def session_service(self) -> BaseSessionService:
```
返回底层的会话服务实例，供 Runner 内部使用。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L132-L134](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L132-L134)

#### `create_session` 方法
```python
async def create_session(
    self,
    app_name: str,
    user_id: str,
    session_id: str,
) -> Session | None:
```
创建或检索用户会话。若指定 `session_id` 的会话已存在则返回现有会话，否则创建新会话。对于数据库后端，会先列出该用户的所有会话并记录日志。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L136-L179](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L136-L179)

#### `generate_profile` 方法
```python
async def generate_profile(
    self,
    app_name: str,
    user_id: str,
    session_id: str,
    events: list["Event"],
) -> list[str]:
```
使用一个 `memory_summarizer` Agent 将历史事件按内容分组，生成 JSON 格式的记忆分组配置，保存到文件系统 `./profiles/memory/<app_name>/<user_id>/<session_id>/` 目录，并返回分组名称列表。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L181-L240](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L181-L240)

#### `compact_history_events` 方法
```python
async def compact_history_events(
    self,
    app_name: str,
    user_id: str,
    session_id: str,
    compact_limit: int,
    agent: "Agent",
):
```
压缩历史事件：
1. 调用 `generate_profile` 对超过 `compact_limit` 条用户消息的历史进行分组
2. 截断 session.events，保留近期事件
3. 在 agent.instruction 中追加提示文本，告知历史已压缩及可用分组
4. 自动挂载 `load_history_events` 工具，允许 Agent 按需加载压缩的历史

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L242-L290](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L242-L290)

### 会话隔离机制

短期记忆通过三元组 `(app_name, user_id, session_id)` 实现会话隔离：
- **app_name**：应用名称，区分不同应用
- **user_id**：用户唯一标识，区分不同用户
- **session_id**：会话唯一标识，区分同一用户的不同会话

相同 `session_id` 的后续调用会恢复历史对话上下文；不同 `session_id` 则创建独立会话。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L136-L179](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L136-L179)

### after_load_memory_callback 回调机制

可通过 `after_load_memory_callback` 参数注册回调函数，在每次加载会话后执行自定义逻辑（如统计、审计、上下文注入等）。回调函数接收加载的 `Session` 对象。

```python
def on_memory_loaded(session: Session):
    print(f"Loaded session with {len(session.events)} events")

stm = ShortTermMemory(
    backend="sqlite",
    after_load_memory_callback=on_memory_loaded
)
```

回调通过 `wrap_get_session_with_callbacks` 包装 `get_session` 方法实现，在返回会话后触发。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L45-L54](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L45-L54), [file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L127-L130](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/short_term_memory.py#L127-L130)

---

## LongTermMemory（长期/跨会话记忆）

长期记忆提供跨会话的持久化记忆存储，支持语义检索。配置后 Agent 会自动获得 `load_memory` 工具，可在对话中主动检索历史记忆。结合 `auto_save_session` 可实现会话自动归档。

### 接口定义

**类签名**：
```python
class LongTermMemory(BaseMemoryService, BaseModel):
```

- 基类：`google.adk.memory.base_memory_service.BaseMemoryService` + `pydantic.BaseModel`
- 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/long_term_memory.py#L98-L496](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/long_term_memory.py#L98-L496)

### 构造参数

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `backend` | `Union[Literal[...], BaseLongTermMemoryBackend]` | `"opensearch"` | 长期记忆后端类型或自定义后端实例。支持：`"local"`, `"opensearch"`, `"redis"`, `"viking"`, `"viking_mem"`(废弃→viking), `"mem0"`, `"openviking"`, `"tos_context"` |
| `backend_config` | `dict` | `{}` | 后端配置参数字典，若提供则直接传递给后端构造函数 |
| `top_k` | `int` | `5` | 检索时返回的最相似记忆片段数量 |
| `index` | `str` | `""` | 存储记忆的索引/集合名称 |
| `app_name` | `str` | `""` | 应用名称。若 `index` 未设置，则使用 `app_name` 作为索引名 |
| `user_id` | `str` | `""` | **已废弃**，保留用于向后兼容 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/long_term_memory.py#L128-L150](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/long_term_memory.py#L128-L150)

### 支持的后端

| 后端类型 | 对应实现类 | 依赖分组 | 说明 |
|----------|-----------|---------|------|
| `local` | `InMemoryLTMBackend` | extensions（llama-index） | 内存向量存储，开发测试用 |
| `opensearch` | `OpensearchLTMBackend` | extensions（llama-index, opensearch-py） | OpenSearch 向量检索 |
| `redis` | `RedisLTMBackend` | database/extensions（redis, llama-index-redis） | Redis 向量检索 |
| `viking` | `VikingDBLTMBackend` | 内置（vikingdb-python-sdk） | 火山引擎 VikingDB |
| `mem0` | `Mem0LTMBackend` | database（mem0ai） | Mem0 记忆服务 |
| `openviking` | `OpenVikingLTMBackend` | 内置（openviking-sdk） | OpenViking 托管服务 |
| `tos_context` | `TosContextBucketLTMBackend` | 内置（tos） | TOS 对象存储上下文桶 |

> **注意**：`opensearch`、`redis`、`local` 等基于 llama-index 的后端需要安装 `veadk-python[extensions]`。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/long_term_memory.py#L42-L95](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/long_term_memory.py#L42-L95)

### 后端基类接口

所有长期记忆后端必须实现 `BaseLongTermMemoryBackend` 抽象基类：

```python
class BaseLongTermMemoryBackend(ABC, BaseModel):
    index: str

    @abstractmethod
    def precheck_index_naming(self):
        """检查索引名称合法性"""

    @abstractmethod
    def save_memory(self, user_id: str, event_strings: list[str], **kwargs) -> bool:
        """保存记忆到后端"""

    @abstractmethod
    def search_memory(
        self, user_id: str, query: str, top_k: int, **kwargs
    ) -> list[str]:
        """从后端检索记忆"""
```

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/long_term_memory_backends/base_backend.py#L20-L35](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/long_term_memory_backends/base_backend.py#L20-L35)

### 核心方法

#### `add_session_to_memory` 方法
```python
@override
async def add_session_to_memory(
    self,
    session: Session,
    **kwargs,
):
```
将会话事件持久化到长期记忆。执行流程：
1. 从 session 获取 user_id
2. 过滤事件：默认只保存用户消息（排除函数调用/响应），openviking 后端同时保存助手消息
3. 将事件转换为 JSON 字符串
4. 调用后端 `save_memory` 存储
5. openviking 后端使用 `asyncio.to_thread` 异步执行，其他后端同步执行

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/long_term_memory.py#L229-L293](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/long_term_memory.py#L229-L293)

#### `search_memory` 方法
```python
@override
async def search_memory(
    self, *, app_name: str, user_id: str, query: str
) -> SearchMemoryResponse:
```
根据查询文本检索相关记忆。执行流程：
1. 调用后端 `search_memory` 获取原始记忆片段
2. 将每个片段解析并转换为 `MemoryEntry` 对象列表
3. 返回 `SearchMemoryResponse(memories=memory_events)`

异常时返回空结果，不中断对话。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/long_term_memory.py#L295-L345](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/long_term_memory.py#L295-L345)

#### `get_user_profile` 方法
```python
def get_user_profile(self, user_id: str) -> str:
```
获取用户画像。**仅 `viking` 后端支持**，其他后端返回空字符串并记录错误日志。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/long_term_memory.py#L488-L496](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/long_term_memory.py#L488-L496)

### 记忆检索与存储机制

**存储流程**：
1. 事件过滤：丢弃空内容、函数调用/响应事件
2. 默认只保留用户消息（提升检索性能），openviking 后端保留全部
3. 序列化为 JSON 字符串，包含 role 规范化处理
4. 后端进行 Embedding 后存储到向量数据库

**检索流程**：
1. 接收自然语言查询
2. 后端进行向量相似度检索，返回 top_k 个最相关片段
3. 反序列化为 `MemoryEntry` 对象，包含 author、content、metadata 等
4. 注入到 Agent 上下文中供模型参考

---

## auto_save_session 自动保存机制

当 Agent 设置 `auto_save_session=True` 且配置了 `long_term_memory` 时，VeADK 会自动注册 `after_agent_callback` 回调，在每次 Agent 执行完成后触发会话保存。

### 自动保存策略

回调函数 `save_session_to_long_term_memory` 实现了智能保存节流机制：

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|---------|--------|------|
| 最小消息阈值 | `MIN_MESSAGES_THRESHOLD` | 10 | 新增消息数达到此值才保存 |
| 最小时间间隔 | `MIN_TIME_THRESHOLD` | 60 秒 | 两次保存的最小时间间隔 |

**保存触发条件**：新增消息数 ≥ 10 **或** 距上次保存 ≥ 60 秒。两个条件满足其一即保存。

### 会话切换检测

系统维护 `_active_sessions` 字典记录每个用户当前活跃会话。当检测到同一用户切换到新 session_id 时，会**强制保存**上一个会话的数据，防止数据丢失。

```python
# 会话切换时强制保存旧会话
if previous_session_id and previous_session_id != session_id:
    # 立即保存 previous_session
    await long_term_memory.add_session_to_memory(old_session)
```

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/save_session_callback.py#L39-L159](file:///d:/AI/.chaos/libs/veadk-python/veadk/memory/save_session_callback.py#L39-L159)

---

## 记忆与 Agent 的集成

在 Agent 构造函数中通过以下参数配置记忆：

| 参数 | 类型 | 说明 |
|------|------|------|
| `short_term_memory` | `Optional[ShortTermMemory]` | 短期记忆实例，管理会话上下文 |
| `long_term_memory` | `Optional[LongTermMemory]` | 长期记忆实例，提供跨会话记忆检索 |
| `auto_save_session` | `bool` | 是否自动将会话保存到长期记忆（需同时配置 long_term_memory） |

### 自动工具挂载

Agent 初始化时自动完成以下集成：

1. **长期记忆工具**：若配置了 `long_term_memory`，自动挂载 Google ADK 的 `load_memory` 工具，Agent 可在对话中调用此工具检索历史记忆。工具的 `custom_metadata["backend"]` 会被设置为当前后端类型。

   > 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L326-L333](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L326-L333)

2. **自动保存回调**：若 `auto_save_session=True`，注册 `save_session_to_long_term_memory` 到 `after_agent_callback`。

   > 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L354-L375](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L354-L375)

> **注意**：Runner 也需要传入 `short_term_memory` 参数才能启用持久化会话存储。

---

## 使用示例

### 示例 1：短期记忆（SQLite 持久化）

实现多轮对话，会话数据持久化到本地 SQLite 文件，进程重启后可恢复。

```python
import asyncio
from veadk import Agent, Runner
from veadk.memory.short_term_memory import ShortTermMemory

APP_NAME = "memory_demo"
SESSION_ID = "user-42-chat"

async def main() -> None:
    short_term_memory = ShortTermMemory(
        backend="sqlite",
        local_database_path="./short_term_memory.db",
    )

    agent = Agent(
        name="memory_agent",
        instruction="You are a concise assistant. Remember what the user tells you.",
        short_term_memory=short_term_memory,
    )

    runner = Runner(
        agent=agent,
        short_term_memory=short_term_memory,
        app_name=APP_NAME,
    )

    # 第一轮：告知信息
    print(
        "Turn 1 ->",
        await runner.run(
            messages="我叫小明，最喜欢的颜色是蓝色。",
            session_id=SESSION_ID,
        ),
    )

    # 第二轮：相同 session_id，Agent 能回忆起第一轮内容
    print(
        "Turn 2 ->",
        await runner.run(
            messages="我叫什么名字？我喜欢什么颜色？",
            session_id=SESSION_ID,
        ),
    )

if __name__ == "__main__":
    asyncio.run(main())
```

> 示例来源：[file:///d:/AI/.chaos/libs/veadk-python/examples/03_short_term_memory/main.py](file:///d:/AI/.chaos/libs/veadk-python/examples/03_short_term_memory/main.py)

### 示例 2：长期记忆（跨会话回忆）

第一次对话告知饮食偏好，第二次全新会话中 Agent 通过 `load_memory` 工具检索历史并给出合适建议。

```python
import asyncio
from veadk import Agent, Runner
from veadk.memory.long_term_memory import LongTermMemory

APP_NAME = "ltm_demo"
USER_ID = "user-42"

def build_runner() -> Runner:
    long_term_memory = LongTermMemory(backend="local", app_name=APP_NAME)
    agent = Agent(
        name="ltm_agent",
        instruction=(
            "You are a personal assistant. When the user asks about something "
            "they told you before, use the `load_memory` tool to recall it."
        ),
        long_term_memory=long_term_memory,
        auto_save_session=True,
    )
    return Runner(agent=agent, app_name=APP_NAME, user_id=USER_ID)

async def main() -> None:
    runner = build_runner()

    # Session 1：分享信息，auto_save_session 自动保存
    print(
        "Session 1 ->",
        await runner.run(
            messages="记一下：我对花生过敏，而且我是素食者。",
            session_id="session-1",
        ),
    )

    # Session 2：不同的 session，Agent 通过记忆检索回忆
    print(
        "Session 2 ->",
        await runner.run(
            messages="帮我推荐一道适合我的菜，要考虑我的饮食限制。",
            session_id="session-2",
        ),
    )

if __name__ == "__main__":
    asyncio.run(main())
```

> 示例来源：[file:///d:/AI/.chaos/libs/veadk-python/examples/09_long_term_memory/main.py](file:///d:/AI/.chaos/libs/veadk-python/examples/09_long_term_memory/main.py)

### 示例 3：使用 PostgreSQL 短期记忆

```python
short_term_memory = ShortTermMemory(
    backend="postgresql",
    backend_configs={
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": "your_password",
        "database": "veadk_sessions",
    }
)
```

### 示例 4：使用 VikingDB 长期记忆

```python
long_term_memory = LongTermMemory(
    backend="viking",
    backend_config={
        "index": "my_agent_memory",
        "viking_host": "your-viking-endpoint",
        # 其他 VikingDB 配置
    },
    top_k=3,
)
```

---

## 依赖说明

| 依赖分组 | 安装命令 | 包含的后端 |
|---------|---------|-----------|
| 基础依赖（内置） | `pip install veadk-python` | local, sqlite, mysql, postgresql（短期记忆）；viking, openviking, tos_context（长期记忆） |
| database | `pip install "veadk-python[database]"` | redis, mem0（长期记忆） |
| extensions | `pip install "veadk-python[extensions]"` | llama-index 生态：opensearch, redis, local 向量检索（长期记忆） |

> 依赖来源：[file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L60-L84](file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L60-L84)

**环境变量要求**：
- 使用基于 llama-index 的向量后端（local/opensearch/redis 等）时，需配置 Embedding 模型相关环境变量（如 `OPENAI_API_KEY` 或火山引擎 Ark 相关配置）
- VikingDB/OpenViking 后端需配置对应的服务访问凭证
