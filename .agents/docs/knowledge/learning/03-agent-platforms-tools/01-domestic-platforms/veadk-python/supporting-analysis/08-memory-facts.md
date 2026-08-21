---
id: 08-memory-facts
title: Memory 模块事实记录
source: veadk-python codebase analysis
---

# Memory 模块事实记录

## ShortTermMemory 类

### 类签名和继承关系
- 文件位置：veadk/memory/short_term_memory.py:57
- 类定义：`class ShortTermMemory(BaseModel):`
- 继承关系：继承自 `pydantic.BaseModel`

### 构造函数字段（Pydantic 模型字段）

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| backend | Literal["local", "mysql", "sqlite", "postgresql", "database"] | "local" | 短期记忆后端类型 |
| backend_configs | dict | Field(default_factory=dict) | 后端配置字典 |
| db_kwargs | dict | Field(default_factory=dict) | 数据库关键字参数 |
| db_url | str | "" | 数据库连接URL，设置后覆盖 backend 参数 |
| local_database_path | str | "/tmp/veadk_local_database.db" | 本地数据库路径，仅 sqlite 后端使用 |
| after_load_memory_callback | Callable \| None | None | 加载记忆后的回调函数 |
| _session_service | BaseSessionService | PrivateAttr() | 私有属性，存储会话服务实例 |

### 公开方法列表

#### 1. model_post_init 方法
- 位置：veadk/memory/short_term_memory.py:93-130
- 方法签名：`def model_post_init(self, __context: Any) -> None:`
- 执行步骤：
  1. 若 db_url 已设置：
     - 输出 info 日志提示忽略 backend 选项
     - 检查 db_url 中 @ 或 : 符号数量，异常时输出 warning 日志提示 URL 编码
     - 使用 DatabaseSessionService(db_url=self.db_url, **self.db_kwargs) 初始化 _session_service
  2. 若 db_url 未设置：
     - 若 backend 为 "database"：输出 warning 日志提示已废弃，将 backend 设置为 "sqlite"
     - 使用 match 语句匹配 backend：
       - "local"：使用 InMemorySessionService() 初始化
       - "mysql"：使用 MysqlSTMBackend 初始化，获取其 session_service
       - "sqlite"：使用 SQLiteSTMBackend 初始化，获取其 session_service
       - "postgresql"：使用 PostgreSqlSTMBackend 初始化，获取其 session_service
  3. 若 after_load_memory_callback 存在：调用 wrap_get_session_with_callbacks 包装 _session_service 的 get_session 方法

#### 2. session_service 属性
- 位置：veadk/memory/short_term_memory.py:132-134
- 签名：`@property def session_service(self) -> BaseSessionService:`
- 返回 self._session_service

#### 3. create_session 方法
- 位置：veadk/memory/short_term_memory.py:136-179
- 方法签名：
  ```python
  async def create_session(
      self,
      app_name: str,
      user_id: str,
      session_id: str,
  ) -> Session | None:
  ```
- 执行步骤：
  1. 若 _session_service 是 DatabaseSessionService 实例：调用 list_sessions 列出会话，输出 debug 日志
  2. 调用 get_session 尝试获取已存在会话
  3. 若会话存在：输出 info 日志并返回该会话
  4. 若会话不存在：调用 create_session 创建新会话并返回

#### 4. generate_profile 方法
- 位置：veadk/memory/short_term_memory.py:181-240
- 方法签名：
  ```python
  async def generate_profile(
      self,
      app_name: str,
      user_id: str,
      session_id: str,
      events: list["Event"],
  ) -> list[str]:
  ```
- 功能：创建一个 memory_summarizer Agent 来总结记忆事件，生成 JSON 格式的分组配置，写入文件系统并返回分组名称列表。

#### 5. compact_history_events 方法
- 位置：veadk/memory/short_term_memory.py:242-290
- 方法签名：
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
- 功能：压缩历史事件，调用 generate_profile 生成分组，截断 session.events，向 agent.instruction 追加提示文本，挂载 load_history_events 工具。

### 模块级函数

#### wrap_get_session_with_callbacks
- 位置：veadk/memory/short_term_memory.py:45-54
- 功能：包装对象的 get_session 方法，在返回结果后调用 callback_fn。

---

## LongTermMemory 类

### 类签名和继承关系
- 文件位置：veadk/memory/long_term_memory.py:98
- 类定义：`class LongTermMemory(BaseMemoryService, BaseModel):`
- 继承关系：继承自 `google.adk.memory.base_memory_service.BaseMemoryService` 和 `pydantic.BaseModel`

### 构造函数字段（Pydantic 模型字段）

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| backend | Union[Literal[...], BaseLongTermMemoryBackend] | "opensearch" | 长期记忆后端类型或实例 |
| backend_config | dict | Field(default_factory=dict) | 后端配置参数字典 |
| top_k | int | 5 | 搜索时返回的最相似文档数量 |
| index | str | "" | 存储记忆项的索引或集合名称 |
| app_name | str | "" | 应用名称 |
| user_id | str | "" | 已废弃属性，保留用于向后兼容 |

backend 支持的字面量类型："local", "opensearch", "redis", "viking", "viking_mem", "mem0", "openviking", "tos_context"

### 公开方法列表

#### 1. model_post_init 方法
- 位置：veadk/memory/long_term_memory.py:152-195
- 执行步骤：
  1. 若 backend 是 BaseLongTermMemoryBackend 实例：直接使用该实例作为 _backend，设置 index 为 _backend.index，输出 info 日志并返回
  2. 若 backend_config 非空：
     - 若 backend_config 中无 "index" 键：输出 warning 日志，设置 index 为 self.index 或 self.app_name
     - 输出 debug 日志，使用 _get_backend_cls(self.backend)(**self.backend_config) 初始化 _backend 并返回
  3. 设置 self.index = self.index or self.app_name
  4. 若 index 为空：输出 warning 日志，设置 index 为 "default_app"
  5. 若 backend 为 "viking_mem"：输出 warning 日志提示已废弃，将 backend 设置为 "viking"
  6. 使用 _get_backend_cls(self.backend)(index=self.index) 初始化 _backend
  7. 输出 info 日志

#### 2. add_session_to_memory 方法
- 位置：veadk/memory/long_term_memory.py:230-293
- 方法签名（override）：
  ```python
  @override
  async def add_session_to_memory(
      self,
      session: Session,
      **kwargs,
  ):
  ```
- 执行步骤：
  1. 从 session 获取 user_id
  2. 处理 kwargs 中的嵌套 kwargs
  3. 设置 app_name = self.app_name 或 session.app_name
  4. 判断是否包含 assistant 消息（openviking 后端包含）
  5. 调用 _filter_and_convert_events 转换事件
  6. 输出 info 日志
  7. 构造 save_call 参数字典
  8. 若使用 openviking 后端：使用 asyncio.to_thread 异步调用 _backend.save_memory
  9. 否则：同步调用 _backend.save_memory
  10. 输出 info 日志

#### 3. search_memory 方法
- 位置：veadk/memory/long_term_memory.py:296-345
- 方法签名（override）：
  ```python
  @override
  async def search_memory(
      self, *, app_name: str, user_id: str, query: str
  ) -> SearchMemoryResponse:
  ```
- 执行步骤：
  1. 输出 info 日志
  2. 初始化 memory_chunks 为空列表
  3. 构造 search_call 参数字典
  4. 若使用 openviking 后端：使用 asyncio.to_thread 异步调用 _backend.search_memory
  5. 否则：同步调用 _backend.search_memory
  6. 异常时输出 error 日志并返回空结果
  7. 遍历 memory_chunks，调用 _convert_memory_chunk_to_entries 转换为 MemoryEntry 列表
  8. 输出 info 日志
  9. 返回 SearchMemoryResponse(memories=memory_events)

#### 4. get_user_profile 方法
- 位置：veadk/memory/long_term_memory.py:488-496
- 方法签名：`def get_user_profile(self, user_id: str) -> str:`
- 执行步骤：
  1. 输出 info 日志
  2. 若 backend 为 "viking"：调用 self._backend.get_user_profile(user_id=user_id) 并返回
  3. 否则：输出 error 日志，返回空字符串

### 内部辅助方法（以下划线开头）

- _filter_and_convert_events：过滤和转换事件为字符串列表（veadk/memory/long_term_memory.py:197-219）
- _normalize_event_role：规范化事件角色（veadk/memory/long_term_memory.py:221-227）
- _uses_openviking_backend：判断是否使用 openviking 后端（veadk/memory/long_term_memory.py:347-351）
- _convert_memory_chunk_to_entries：将记忆块转换为 MemoryEntry 列表（veadk/memory/long_term_memory.py:353-391）
- _convert_memory_dict_to_entry：将记忆字典转换为 MemoryEntry（veadk/memory/long_term_memory.py:393-420）
- _extract_memory_custom_metadata：提取自定义元数据（veadk/memory/long_term_memory.py:422-435）
- _extract_memory_parts_text：从 parts 中提取文本（veadk/memory/long_term_memory.py:437-443）
- _extract_memory_part_text：从单个 part 中提取文本（veadk/memory/long_term_memory.py:445-460）
- _extract_memory_text_field：从记忆字段中提取文本（veadk/memory/long_term_memory.py:462-467）
- _clean_memory_text：清理记忆文本（veadk/memory/long_term_memory.py:469-486）

### 模块级函数

#### _get_backend_cls
- 位置：veadk/memory/long_term_memory.py:42-95
- 功能：根据 backend 字符串返回对应的后端类，支持的后端映射：
  - "local" → InMemoryLTMBackend
  - "opensearch" → OpensearchLTMBackend
  - "viking" → VikingDBLTMBackend
  - "redis" → RedisLTMBackend
  - "mem0" → Mem0LTMBackend
  - "openviking" → OpenVikingLTMBackend
  - "tos_context" → TosContextBucketLTMBackend
- 导入失败时若涉及 llama_index，抛出 ImportError 提示安装 veadk-python[extensions]

---

## 支持的后端类型列表

### ShortTermMemory 后端类型
| 后端类型 | 对应实现类 | 来源 |
|----------|-----------|------|
| local | InMemorySessionService | google.adk.sessions |
| mysql | MysqlSTMBackend | veadk.memory.short_term_memory_backends.mysql_backend |
| sqlite | SQLiteSTMBackend | veadk.memory.short_term_memory_backends.sqlite_backend |
| postgresql | PostgreSqlSTMBackend | veadk.memory.short_term_memory_backends.postgresql_backend |
| database | DatabaseSessionService（已废弃，映射到 sqlite） | google.adk.sessions |

### LongTermMemory 后端类型
| 后端类型 | 对应实现类 | 来源 |
|----------|-----------|------|
| local | InMemoryLTMBackend | veadk.memory.long_term_memory_backends.in_memory_backend |
| opensearch | OpensearchLTMBackend | veadk.memory.long_term_memory_backends.opensearch_backend |
| viking | VikingDBLTMBackend | veadk.memory.long_term_memory_backends.vikingdb_memory_backend |
| redis | RedisLTMBackend | veadk.memory.long_term_memory_backends.redis_backend |
| mem0 | Mem0LTMBackend | veadk.memory.long_term_memory_backends.mem0_backend |
| openviking | OpenVikingLTMBackend | veadk.memory.long_term_memory_backends.openviking_backend |
| tos_context | TosContextBucketLTMBackend | veadk.memory.long_term_memory_backends.tos_context_bucket_backend |
| viking_mem | （已废弃，映射到 viking） | - |

---

本文档记录了 ShortTermMemory 和 LongTermMemory 两个类的类签名、构造参数、公开方法及内部辅助方法。本文档从代码中提取了两个记忆模块支持的全部后端类型及对应实现类。所有内容均为客观代码事实描述，未包含主观评价。
